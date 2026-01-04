import yfinance as yf
import boto3
import json
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vix_cache")

# Mock Env if needed or verify settings load
# We assume aws/credentials are set
from src.config import settings

def fetch_and_upload_vix():
    logger.info("Fetching VIX data locally...")
    
    try:
        # Fetch VIX
        vix = yf.Ticker("^VIX")
        # period=1mo to get recent history
        df = vix.history(period="1mo")
        
        if df.empty:
            logger.error("VIX fetch returned empty data locally! blocked?")
            return

        current_vix = df['Close'].iloc[-1]
        logger.info(f"Current VIX: {current_vix}")

        data = {
            "symbol": "^VIX",
            "price": current_vix,
            "timestamp": datetime.now().isoformat(),
            "status": "Normal" if 12 <= current_vix <= 20 else ("Elevated" if current_vix > 20 else "Low")
        }
        
        # Upload to S3
        s3 = boto3.client('s3')
        bucket = "trading-automation-data-904583676284" # Hardcoded to be safe or use settings.S3_BUCKET
        key = "min_data/vix_latest.json"
        
        logger.info(f"Uploading VIX data to s3://{bucket}/{key}...")
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
        logger.info("✅ VIX cache uploaded successfully!")
        
    except Exception as e:
        logger.error(f"Failed to fetch/upload VIX: {e}")

if __name__ == "__main__":
    fetch_and_upload_vix()
