
import os
import sys
import time
import logging
import pandas as pd
import yfinance as yf
import boto3
from pathlib import Path
from io import StringIO
from botocore.exceptions import ClientError

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modules.data_fetcher import DataFetcher

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("data_lake_init")

# Configuration
S3_BUCKET = os.environ.get("S3_BUCKET", "trading-automation-data-904583676284")
HISTORY_PERIOD = "20y"
BATCH_SIZE = 50
SLEEP_BETWEEN_BATCHES = 5  # Seconds

def upload_to_s3(df: pd.DataFrame, symbol: str, s3_client):
    """Upload DataFrame to S3 as CSV"""
    try:
        csv_buffer = StringIO()
        df.to_csv(csv_buffer)
        
        key = f"historical_data/{symbol}.csv"
        
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=csv_buffer.getvalue()
        )
        return True
    except Exception as e:
        logger.error(f"Failed to upload {symbol} to S3: {e}")
        return False

def initialize_data_lake():
    logger.info(f"🚀 Starting Data Lake Initialization (Target: {S3_BUCKET})")
    
    # 1. Initialize AWS S3 Client
    try:
        s3_client = boto3.client('s3')
        # Check if bucket exists
        s3_client.head_bucket(Bucket=S3_BUCKET)
    except ClientError as e:
        logger.error(f"Could not connect to S3 Bucket {S3_BUCKET}: {e}")
        return

    # 2. Fetch Universe
    fetcher = DataFetcher()
    universe = fetcher.fetch_full_universe()
    logger.info(f"Loaded {len(universe)} tickers for processing.")
    
    # 3. Batch Process
    total_processed = 0
    total_failed = 0
    
    for i in range(0, len(universe), BATCH_SIZE):
        batch = universe[i:i + BATCH_SIZE]
        logger.info(f"Processing Batch {i//BATCH_SIZE + 1} ({len(batch)} tickers)...")
        
        for symbol in batch:
            try:
                # Fetch Data
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=HISTORY_PERIOD)
                
                if hist.empty:
                    logger.warning(f"No data found for {symbol}")
                    total_failed += 1
                    continue
                
                # Fix for yfinance/pandas/numpy compatibility issues
                if pd.api.types.is_datetime64_any_dtype(hist.index):
                    hist.index = hist.index.tz_localize(None)
                
                if isinstance(hist.columns, pd.MultiIndex):
                    hist.columns = hist.columns.get_level_values(0)

                # Upload
                if upload_to_s3(hist, symbol, s3_client):
                    total_processed += 1
                else:
                    total_failed += 1
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                total_failed += 1
                
        # Rate limit protection
        logger.info(f"Batch complete. Sleeping {SLEEP_BETWEEN_BATCHES}s...")
        time.sleep(SLEEP_BETWEEN_BATCHES)

    logger.info("="*50)
    logger.info(f"✅ Data Lake Initialization Complete")
    logger.info(f"Total Processed: {total_processed}")
    logger.info(f"Total Failed: {total_failed}")
    logger.info("="*50)

if __name__ == "__main__":
    initialize_data_lake()
