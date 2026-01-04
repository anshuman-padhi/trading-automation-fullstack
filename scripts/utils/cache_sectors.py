import yfinance as yf
import boto3
import json
import logging
from src.modules.data_fetcher import DataFetcher
from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sector_cache")

def fetch_and_upload_sectors():
    fetcher = DataFetcher()
    
    # 1. Get Universe
    tickers = fetcher.fetch_sp500_tickers()
    # Add some non-SP500 if needed (e.g. from Nasdaq)
    # For now SP500 is the main focus of the report
    
    logger.info(f"Fetching sector data for {len(tickers)} tickers...")
    
    sector_map = {}
    
    # Batch processing could be done, but Ticker.info is single
    # We can use Tickers object for multi? 
    # yf.Tickers(' '.join(tickers)).tickers -> accesses each.
    
    count = 0
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            sector = t.info.get('sector', 'N/A')
            sector_map[ticker] = sector
            count += 1
            if count % 50 == 0:
                print(f"Processed {count}/{len(tickers)}...")
        except Exception as e:
            print(f"Failed {ticker}: {e}")
            sector_map[ticker] = 'N/A'
            
    # Upload to S3
    s3 = boto3.client('s3')
    bucket = settings.S3_BUCKET
    key = "min_data/sectors.json"
    
    logger.info(f"Uploading sector map to s3://{bucket}/{key}...")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(sector_map),
        ContentType='application/json'
    )
    logger.info("✅ Sector cache uploaded successfully!")

if __name__ == "__main__":
    fetch_and_upload_sectors()
