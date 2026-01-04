
import pandas as pd
import numpy as np
import joblib
import logging
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score, precision_score
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("ml_trainer")

def train_model():
    data_path = "scripts/ml/training_data.csv"
    model_path = "scripts/ml/breakout_classifier.joblib"
    
    if not os.path.exists(data_path):
        logger.error(f"Data file not found: {data_path}")
        return

    # 1. Load Data
    df = pd.read_csv(data_path, parse_dates=['entry_date'])
    logger.info(f"Loaded {len(df)} samples.")
    
    # 2. Preprocessing
    df = df.dropna()
    # PHASE 2A: Enhanced feature set (22 features)
    features = [
        # Original 8 (with 2 now fixed)
        'rsi', 'vol_ratio', 'atr_pct', 'sma50_dist', 'sma200_dist', 'bb_width', 'spy_trend', 'rs_rel',
        # Phase 1 (7 features)
        'mom_1m', 'mom_3m', 'mom_6m', 'realized_vol', 'vol_spike', 'dist_52w_high', 'dist_52w_low',
        # Phase 2A: Market Breadth (5 features)
        'pct_above_200sma', 'adv_dec_ratio', 'new_highs_lows', 'spy_rsi_market', 'vix_level'
    ]
    
    # Walk-Forward Split (Train: 2006-2015, Test: 2016-2025)
    split_date = "2016-01-01"
    train_df = df[df['entry_date'] < split_date]
    test_df = df[df['entry_date'] >= split_date]
    
    logger.info(f"Train Set: {len(train_df)} samples (< {split_date})")
    logger.info(f"Test Set:  {len(test_df)} samples (>= {split_date})")
    
    if len(train_df) < 50:
        logger.error("Not enough training samples!")
        return

    X_train = train_df[features]
    y_train = train_df['outcome']
    X_test = test_df[features]
    y_test = test_df['outcome']
    
    # Feature Scaling (Fit on Train ONLY to avoid leakage)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    X_train = pd.DataFrame(X_train, columns=features) # Keep names for warnings? No, returns numpy array usually
    X_test = pd.DataFrame(X_test, columns=features)
    
    # 3. Model Comparison
    models = {
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=5, class_weight='balanced', random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42)
    }
    
    best_model = None
    best_precision = 0
    target_threshold = 0.55 # We want high confidence
    
    logger.info("Comparing Models...")
    
    for name, clf in models.items():
        logger.info(f"\nTraining {name}...")
        clf.fit(X_train, y_train)
        
        y_prob = clf.predict_proba(X_test)[:, 1]
        
        # Evaluate at Threshold
        high_conf_idx = np.where(y_prob > target_threshold)[0]
        if len(high_conf_idx) > 0:
            precision = y_test.iloc[high_conf_idx].mean()
            coverage = len(high_conf_idx) / len(X_test)
            logger.info(f"  Precision (>{target_threshold}): {precision:.1%}")
            logger.info(f"  Coverage: {coverage:.1%}")
            
            if precision > best_precision:
                best_precision = precision
                best_model = clf
        else:
            logger.info("  No trades met threshold.")

    # 4. Save Best Model
    if best_model:
        logger.info(f"\n🏆 Best Model: {best_model.__class__.__name__} (Precision: {best_precision:.1%})")
        
        # We need to save the scaler too for inference pipeline
        pipeline = {
            "model": best_model,
            "scaler": scaler
        }
        joblib.dump(pipeline, model_path) # Save whole pipeline
        logger.info(f"✅ Pipeline saved to {model_path}")
    else:
        logger.error("No model met the criteria.")

if __name__ == "__main__":
    train_model()
