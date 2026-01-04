
import boto3
import json
import os
import logging
from botocore.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manifest_gen")

S3_BUCKET = os.environ.get("S3_BUCKET", "trading-automation-data-904583676284")
MANIFEST_PATH = "data/tickers.json"

def generate_manifest():
    # Robust Config
    config = Config(
        retries = dict(
            max_attempts = 10
        ),
        read_timeout = 300,
        connect_timeout = 300
    )
    
    s3 = boto3.client('s3', config=config)
    tickers = []
    
    logger.info(f"Scanning bucket {S3_BUCKET} for historical data...")
    
    try:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix='historical_data/')
        
        count = 0
        for page in pages:
            if 'Contents' not in page: continue
            for obj in page['Contents']:
                if obj['Key'].endswith('.csv'):
                    symbol = obj['Key'].split('/')[-1].replace('.csv', '')
                    tickers.append(symbol)
                    count += 1
                    if count % 100 == 0: logger.info(f"Found {count} files...")
        
        logger.info(f"Total Tickers Found: {len(tickers)}")
        
        # Save to file
        os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
        with open(MANIFEST_PATH, 'w') as f:
            json.dump(tickers, f)
            
        logger.info(f"Manifest saved to {MANIFEST_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to list S3: {e}")
        return False

if __name__ == "__main__":
    generate_manifest()
