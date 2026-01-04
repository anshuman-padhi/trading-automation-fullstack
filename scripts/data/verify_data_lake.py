
import os
import sys
import logging
import pandas as pd
import yfinance as yf
import boto3
from pathlib import Path
from io import StringIO
from botocore.exceptions import ClientError

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_data_lake")

# Configuration
S3_BUCKET = os.environ.get("S3_BUCKET", "trading-automation-data-904583676284")

def verify_data_lake_subset():
    logger.info(f"🚀 Starting Data Lake Verification (Target: {S3_BUCKET})")
    
    # 1. Initialize AWS S3 Client
    s3_client = boto3.client('s3')
    
    # 2. Test Subset
    test_tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    for symbol in test_tickers:
        logger.info(f"Processing {symbol}...")
        try:
            # Fetch 20y Data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="20y")
            
            if hist.empty:
                logger.error(f"No data for {symbol}")
                continue
            
            # Debug info
            logger.info(f"Fetched {len(hist)} rows for {symbol}. Last date: {hist.index[-1]}")
            logger.info(f"Columns: {hist.columns}")
            logger.info(f"Dtypes: {hist.dtypes}")

            # Fix for yfinance/pandas/numpy compatibility issues
            # Ensure index is timezone-naive if causing issues
            if pd.api.types.is_datetime64_any_dtype(hist.index):
                hist.index = hist.index.tz_localize(None)
            
            # Flatten multi-level columns if present (yfinance sometimes returns MultiIndex columns)
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)

            # Upload to S3
            csv_buffer = StringIO()
            hist.to_csv(csv_buffer)
            key = f"historical_data/{symbol}.csv"  
            
            s3_client.put_object(Bucket=S3_BUCKET, Key=key, Body=csv_buffer.getvalue())
            logger.info(f"✅ Uploaded to s3://{S3_BUCKET}/{key}")
            
            # Verify Read Back
            obj = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
            df_read = pd.read_csv(obj['Body'], index_col=0)
            logger.info(f"Verified Read: {len(df_read)} rows recovered.")
            
        except Exception as e:
            logger.error(f"Failed {symbol}: {e}")

if __name__ == "__main__":
    verify_data_lake_subset()
