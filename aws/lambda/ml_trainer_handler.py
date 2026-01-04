import boto3
import pandas as pd
import numpy as np
import joblib
import logging
import os
import json
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from io import StringIO
import tempfile

# Configure Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
ses_client = boto3.client('ses', region_name=os.environ.get('SES_REGION', 'us-east-1'))

def lambda_handler(event, context):
    """
    ML Trainer Lambda.
    Triggered by EventBridge (e.g., Weekly).
    1. Downloads training data from S3 (ml_data/training_data.csv).
    2. Trains RandomForest/GradientBoosting.
    3. Selects best model.
    4. Uploads pipeline to S3 (ml_models/model.joblib).
    5. Sends Email Report.
    """
    bucket = os.environ['S3_BUCKET']
    data_key = "ml_data/training_data.csv"
    model_key = "ml_models/model.joblib"
    
    logger.info(f"Starting ML Retraining Task. Bucket: {bucket}")
    
    # 1. Download Data
    try:
        response = s3_client.get_object(Bucket=bucket, Key=data_key)
        csv_content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_content))
        logger.info(f"Loaded {len(df)} samples from S3.")
    except Exception as e:
        logger.error(f"Failed to download data: {e}")
        return {"statusCode": 500, "body": "Data Download Failed"}

    # 2. Preprocessing
    df = df.dropna()
    features = ['rsi', 'vol_ratio', 'atr_pct', 'sma50_dist', 'sma200_dist', 'bb_width', 'spy_trend', 'rs_rel']
    # Validate columns exist
    missing = [f for f in features if f not in df.columns]
    if missing:
        msg = f"Missing features in CSV: {missing}"
        logger.error(msg)
        return {"statusCode": 400, "body": msg}

    X = df[features]
    y = df['outcome']
    
    # Feature Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    # 3. Training
    model = RandomForestClassifier(n_estimators=100, max_depth=5, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluation
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # High Confidence Metrics
    threshold = 0.55
    high_conf_idx = np.where(y_prob > threshold)[0]
    if len(high_conf_idx) > 0:
        precision = y_test.iloc[high_conf_idx].mean()
        coverage = len(high_conf_idx) / len(X_test)
    else:
        precision = 0.0
        coverage = 0.0
        
    logger.info(f"Model Trained. Acc: {accuracy:.1%}, Precision(>{threshold}): {precision:.1%}")
    
    # 4. Save & Upload
    pipeline = {"model": model, "scaler": scaler}
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        joblib.dump(pipeline, tmp.name)
        tmp.close()
        s3_client.upload_file(tmp.name, bucket, model_key)
        os.unlink(tmp.name)
        
    logger.info(f"Model uploaded to s3://{bucket}/{model_key}")
    
    # 5. Notify
    message = (
        f"ML Model Retrained Successfully.\n\n"
        f"Samples: {len(df)}\n"
        f"Accuracy: {accuracy:.1%}\n"
        f"Precision (> {threshold}): {precision:.1%}\n"
        f"High Confidence Trades: {len(high_conf_idx)} (Coverage: {coverage:.1%})"
    )
    
    try:
        ses_client.send_email(
            Source=os.environ['FROM_EMAIL'],
            Destination={'ToAddresses': [os.environ['TO_EMAIL']]},
            Message={
                'Subject': {'Data': 'ML Model Retraining Report'},
                'Body': {'Text': {'Data': message}}
            }
        )
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

    return {
        "statusCode": 200,
        "body": json.dumps({"status": "Success", "precision": precision})
    }
