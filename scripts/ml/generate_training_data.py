
import sys
import os
import json
import concurrent.futures
import boto3
import pandas as pd
import logging
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modules.backtester import Backtester

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("ml_data_gen")

# Configuration
NUM_WORKERS = max(1, int(os.cpu_count() * 0.75))
OUTPUT_PATH = "scripts/ml/training_data.csv"
S3_BUCKET = "quantx-market-data"

S3_BUCKET = os.environ.get("S3_BUCKET", "trading-automation-data-904583676284")

def get_all_symbols_from_s3() -> list:
    s3 = boto3.client('s3')
    symbols = []
    try:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix='historical_data/')
        for page in pages:
            if 'Contents' not in page: continue
            for obj in page['Contents']:
                if obj['Key'].endswith('.csv'):
                    symbols.append(obj['Key'].split('/')[-1].replace('.csv', ''))
        return symbols
    except Exception as e:
        logger.error(f"S3 Error: {e}")
        return []

def load_data(symbol: str) -> pd.DataFrame:
    try:
        s3 = boto3.client('s3')
        key = f"historical_data/{symbol}.csv"
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        df = pd.read_csv(obj['Body'], index_col=0, parse_dates=True)
        return df
    except Exception as e:
        return pd.DataFrame()

import multiprocessing
from functools import partial

# ... (imports remain)

# Global variable for workers (efficient for multiprocessing read-only)
market_data_global = None
vix_data_global = None  # PHASE 2A
s3_client_global = None

def init_worker(market_df, vix_df=None):
    global market_data_global, vix_data_global, s3_client_global
    market_data_global = market_df
    vix_data_global = vix_df
    try:
        s3_client_global = boto3.client('s3')
    except Exception as e:
        logger.error(f"Failed to init S3 client: {e}")

def load_data(symbol: str) -> pd.DataFrame:
    try:
        # Reuse global client if available (worker), else create new (main)
        s3 = s3_client_global if s3_client_global else boto3.client('s3')
        key = f"historical_data/{symbol}.csv"
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        df = pd.read_csv(obj['Body'], index_col=0, parse_dates=True)
        return df
    except Exception as e:
        # logger.error(f"S3 Error {symbol}: {e}")
        return pd.DataFrame()

def process_symbol(symbol):
    """Worker function for multiprocessing"""
    try:
        df = load_data(symbol)
        if df.empty:
            return []
            
        # Create a fresh backtester instance for each process to avoid state issues
        bt = Backtester()
        bt.collect_ml_data = True
        bt.skip_ml_filter = True  # PHASE 1: Skip ML filter to collect training data
        
        # Inject Market Data if available
        if market_data_global is not None:
            bt.set_market_data(market_data_global)
        
        # PHASE 2A: Inject VIX Data if available
        if vix_data_global is not None and not vix_data_global.empty:
            bt.vix_data = vix_data_global
            
        # New Signature expectation: Dict[str, DataFrame]
        bt.run_backtest({symbol: df})
        return bt.ml_data
    except Exception as e:
        logger.error(f"Error processing {symbol}: {e}")
        return []


def get_tickers_from_manifest():
    try:
        with open("data/tickers.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def generate_training_data():
    logger.info("🚀 Starting Full-Scale Data Generation (Multiprocessed)...")
    
    # Load Market Data (SPY)
    logger.info("Loading Market Data (SPY)...")
    s3 = boto3.client('s3')
    spy_obj = s3.get_object(Bucket=S3_BUCKET, Key="historical_data/SPY.csv")
    market_df = pd.read_csv(spy_obj['Body'], index_col=0, parse_dates=True)
    
    # PHASE 2A: Load VIX data
    from src.modules.market_breadth import load_cached_vix
    vix_df = load_cached_vix()
    if vix_df is None or vix_df.empty:
        logger.info("VIX cache not found, will use defaults")
        vix_df = None
    else:
        logger.info(f"Loaded VIX data: {len(vix_df)} points")
    
    # Get Universe (from Manifest)
    symbols = get_tickers_from_manifest()
    
    # Fallback to manual if manifest missing (e.g. CI/CD)
    if not symbols:
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'SPY']
        logger.warning("Manifest not found. Using subset.")
        
    if not symbols:
        logger.warning("No symbols to process!")
        return

    data = {} # Initialize data dictionary for loaded DFs
    # Load Data in Parallel
    logger.info(f"Scanning {len(symbols)} stocks from Manifest.")
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(load_data, sym): sym for sym in symbols}
        for future in concurrent.futures.as_completed(futures):
            symbol = futures[future]
            try:
                df = future.result()
                if not df.empty and len(df) > 250: # Filter out empty or too short dataframes
                    data[symbol] = df
            except Exception as e:
                logger.error(f"Error loading data for {symbol}: {e}")
                pass
    
    logger.info(f"Loaded {len(data)} stocks.")
    
    if not data:
        logger.warning("No valid stock data loaded for backtesting.")
        return

    # Multiprocessing - PHASE 2A: Pass VIX to workers
    logger.info(f"Spinning up pool with {NUM_WORKERS} workers...")
    with multiprocessing.Pool(processes=NUM_WORKERS, initializer=init_worker, initargs=(market_df, vix_df)) as pool:
        results = pool.map(process_symbol, list(data.keys()))
    
    # Aggregate and Save
    all_samples = []
    for result in results:
        if result:
            all_samples.extend(result)
    
    if all_samples:
        df_ml = pd.DataFrame(all_samples)
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True) # Ensure directory exists
        df_ml.to_csv(OUTPUT_PATH, index=False)
        
        logger.info("\n" + "="*50)
        logger.info(f"✅ Data Generation Complete!")
        logger.info(f"Total Samples: {len(df_ml)}")
        logger.info(f"Win Rate in Data: {(df_ml['outcome'].mean() * 100):.1f}%")
        logger.info(f"Saved to: {output_path}")
        logger.info("="*50)
    else:
        logger.warning("No trades generated from backtest.")

if __name__ == "__main__":
    # Fix for macOS multiprocessing
    multiprocessing.set_start_method('fork', force=True) 
    generate_training_data()
