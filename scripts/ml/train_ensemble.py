"""
Enhanced ML Training with Ensemble Model
Uses top 15 features and voting classifier for improved precision.
"""
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import logging

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, precision_score, recall_score

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("XGBoost not available, using RF + GBM only")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_ensemble_model():
    data_path = "scripts/ml/training_data.csv"
    model_path = "scripts/ml/breakout_classifier.joblib"
    
    if not os.path.exists(data_path):
        logger.error(f"Data file not found: {data_path}")
        return

    # Load top 15 features
    with open("scripts/ml/selected_features.txt", "r") as f:
        selected_features = [line.strip() for line in f.readlines()]
    
    logger.info(f"Using {len(selected_features)} selected features")
    
    # 1. Load Data
    df = pd.read_csv(data_path, parse_dates=['entry_date'])
    logger.info(f"Loaded {len(df)} samples.")
    
    # 2. Preprocessing
    df = df.dropna()
    
    # Use only selected features
    features = selected_features
    
    # Walk-Forward Split (Train: 2006-2015, Test: 2016-2025)
    split_date = "2016-01-01"
    train_df = df[df['entry_date'] < split_date]
    test_df = df[df['entry_date'] >= split_date]
    
    X_train = train_df[features]
    y_train = train_df['outcome']
    X_test = test_df[features]
    y_test = test_df['outcome']
    
    logger.info(f"Train Set: {len(train_df)} samples (< {split_date})")
    logger.info(f"Test Set:  {len(test_df)} samples (>= {split_date})")
    
    # 3. Create Ensemble Model
    logger.info("\n" + "="*60)
    logger.info("BUILDING ENSEMBLE MODEL")
    logger.info("="*60)
    
    # Define individual models with optimized hyperparameters
    models = []
    
    # Random Forest - Best for general patterns
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=4,
        max_features='sqrt',
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    models.append(('rf', rf))
    logger.info("✓ Added Random Forest (n_estimators=300)")
    
    # Gradient Boosting - Best for sequential learning
    gbm = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        min_samples_split=10,
        min_samples_leaf=4,
        subsample=0.9,
        random_state=42
    )
    models.append(('gbm', gbm))
    logger.info("✓ Added Gradient Boosting (n_estimators=200)")
    
    # XGBoost - Best for speed and performance
    if XGBOOST_AVAILABLE:
        xgb = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.8,
            scale_pos_weight=1.5,  # Handle imbalance
            random_state=42,
            n_jobs=-1
        )
        models.append(('xgb', xgb))
        logger.info("✓ Added XGBoost (n_estimators=200)")
    
    # Create voting ensemble
    weights = [1.5, 1.0, 1.2] if XGBOOST_AVAILABLE else [1.5, 1.0]
    ensemble = VotingClassifier(
        estimators=models,
        voting='soft',  # Use probability averaging
        weights=weights,
        n_jobs=-1
    )
    
    logger.info(f"\nEnsemble Configuration:")
    logger.info(f"  - Voting: Soft (probability averaging)")
    logger.info(f"  - Weights: {dict(zip([m[0] for m in models], weights))}")
    
    # 4. Train Ensemble
    logger.info("\nTraining ensemble model...")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    ensemble.fit(X_train_scaled, y_train)
    logger.info("✓ Training complete")
    
    # 5. Evaluate
    logger.info("\n" + "="*60)
    logger.info("ENSEMBLE PERFORMANCE EVALUATION")
    logger.info("="*60)
    
    # Test set predictions
    y_pred = ensemble.predict(X_test_scaled)
    y_proba = ensemble.predict_proba(X_test_scaled)[:, 1]
    
    # Overall metrics
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    
    logger.info(f"\nTest Set Performance:")
    logger.info(f"  Precision: {precision*100:.1f}%")
    logger.info(f"  Recall:    {recall*100:.1f}%")
    logger.info(f"  F1-Score:  {2*precision*recall/(precision+recall)*100:.1f}%")
    
    # Precision at different thresholds
    logger.info(f"\nPrecision at Different Thresholds:")
    for threshold in [0.45, 0.50, 0.55, 0.60, 0.65]:
        y_pred_thresh = (y_proba >= threshold).astype(int)
        if y_pred_thresh.sum() > 0:
            prec = precision_score(y_test, y_pred_thresh)
            coverage = y_pred_thresh.sum() / len(y_pred_thresh)
            logger.info(f"  >{threshold:.2f}: {prec*100:5.1f}% precision (coverage: {coverage*100:4.1f}%)")
    
    # Individual model performance (Check fitted estimators)
    logger.info(f"\nIndividual Model Performance:")
    if hasattr(ensemble, 'estimators_'):
        for name, model in zip(ensemble.named_estimators_.keys(), ensemble.estimators_):
            try:
                model_proba = model.predict_proba(X_train_scaled)[:, 1]
                model_pred = (model_proba >= 0.55).astype(int)
                if model_pred.sum() > 0:
                    model_prec = precision_score(y_train, model_pred)
                    logger.info(f"  {name.upper():6s}: {model_prec*100:5.1f}% precision (train)")
            except Exception as e:
                logger.warning(f"Could not evaluate {name}: {e}")

    # 6. Save Model
    # Save the pipeline with the scaler and model
    pipeline = {
        'model': ensemble,
        'scaler': scaler,
        'features': features
    }
    
    joblib.dump(pipeline, model_path)
    logger.info(f"\n✅ Ensemble pipeline saved to {model_path}")
    logger.info(f"   - Features: {len(features)}")
    
    # 7. Comparison
    logger.info("\n" + "="*60)
    logger.info("IMPROVEMENT SUMMARY")
    logger.info("="*60)
    logger.info(f"Baseline precision:    ~24%")
    logger.info(f"Ensemble precision:    ~{precision*100:.0f}%")
    logger.info("="*60)

if __name__ == "__main__":
    train_ensemble_model()
