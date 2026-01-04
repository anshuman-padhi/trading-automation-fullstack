
import os
import sys
from pathlib import Path
import pandas as pd
import boto3
import logging
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.modules.data_fetcher import DataFetcher

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

S3_BUCKET = settings.S3_BUCKET
CACHE_KEY = "market_data/universe_history.parquet"

def create_baseline():
    """
    Fetch 2 years of history for Full Universe and upload to S3 as Parquet.
    """
    logger.info("Initializing DataFetcher...")
    fetcher = DataFetcher()
    
    # 1. Get Universe
    logger.info("Fetching Full Universe tickers...")
    tickers = fetcher.fetch_full_universe()
    logger.info(f"Found {len(tickers)} tickers.")
    
    # Filter out problematic tickers often causing API issues
    problematic = ['BF-B', 'BRK-B']
    tickers = [t for t in tickers if t not in problematic]
    logger.info(f"Filtered tickers count: {len(tickers)}")
    
    # 2. Fetch History (Bulk)
    logger.info("Fetching 2 years of historical data (this may take a while)...")
    # Using fetch_bulk_history which we assume handles chunking and multi-threading
    # We might need to ensure DataFetcher has a robust bulk method.
    # checking src/modules/data_fetcher.py... it does have fetch_bulk_history.
    
    try:
        df = fetcher.fetch_bulk_history(tickers, period="2y")
    except Exception as e:
        logger.error(f"Failed to fetch bulk history: {e}")
        return

    if df.empty:
        logger.error("No data fetched. Exiting.")
        return

    logger.info(f"Fetched DataFrame Shape: {df.shape}")
    
    # 3. Format for Parquet
    # DataFetcher.fetch_bulk_history returns a MultiIndex (Ticker, Date) or (PriceType, Ticker)?
    # Let's verify standard yfinance/alpaca structure.
    # In data_fetcher.py: fetch_bulk_history returns pd.concat(all_dfs, keys=tickers)
    # The index will be MultiIndex: (Ticker, Timestamp)
    # Columns: Open, High, Low, Close, Volume...
    
    # Flatten for easier storage if needed, or keep MultiIndex. 
    # Parquet handles MultiIndex reasonably well, but resetting index is safer for broad compatibility.
    
    # Flatten to Long Format (Date, Symbol, Open, High, Low, Close, Volume)
    # df columns are MultiIndex: (Symbol, Field)
    # df index is Date
    logger.info("Flattening to Long Format...")
    
    # Ensure column levels are named
    df.columns.names = ['Symbol', 'Field']
    
    # Stack 'Symbol' level from columns to index -> (Date, Symbol) index
    df_stacked = df.stack(level='Symbol', future_stack=True)
    
    # Reset index to make Date and Symbol columns
    df_reset = df_stacked.reset_index()
    
    # Ensure Date is renamed if needed (it might be 'timestamp' or 'Date')
    # If index didn't have a name, reset_index names it 'level_0'
    if 'level_0' in df_reset.columns:
        df_reset.rename(columns={'level_0': 'Date'}, inplace=True)
    elif 'index' in df_reset.columns:
        df_reset.rename(columns={'index': 'Date'}, inplace=True)

    # Reorder columns for clarity
    cols = ['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']
    # Filter only existing columns
    cols = [c for c in cols if c in df_reset.columns]
    df_reset = df_reset[cols]

    logger.info("Sample Data:")
    logger.info(df_reset.head())
    
    # 4. Upload to S3
    s3 = boto3.client('s3')
    
    logger.info(f"Uploading to s3://{S3_BUCKET}/{CACHE_KEY}...")
    
    # Use partial file to avoid large memory buffer if possible, or just to_parquet(buffer)
    try:
        out_buffer = pd.DataFrame.to_parquet(df_reset, engine='pyarrow', index=False)
        # to_parquet returns bytes if path is None? No, it takes a path or file-like object.
        # Use io.BytesIO
        from io import BytesIO
        buffer = BytesIO()
        df_reset.to_parquet(buffer, engine='pyarrow', index=False)
        buffer.seek(0)
        
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=CACHE_KEY,
            Body=buffer.getvalue()
        )
        logger.info("Upload Successful!")
        
    except Exception as e:
        logger.error(f"Failed to upload to S3: {e}")

if __name__ == "__main__":
    create_baseline()
