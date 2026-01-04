
import sys
import os
import boto3
import pandas as pd
import logging
from pathlib import Path
import concurrent.futures

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modules.backtester import Backtester

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("backtest_runner")

S3_BUCKET = os.environ.get("S3_BUCKET", "trading-automation-data-904583676284")

import threading

thread_local = threading.local()

def get_s3_client():
    if not hasattr(thread_local, "s3_client"):
        thread_local.s3_client = boto3.client('s3')
    return thread_local.s3_client

def load_data(symbol: str) -> tuple:
    """Load data from S3 Data Lake"""
    try:
        s3 = get_s3_client()
        key = f"historical_data/{symbol}.csv"
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        df = pd.read_csv(obj['Body'], index_col=0, parse_dates=True)
        return symbol, df
    except Exception as e:
        # logger.error(f"Failed to load {symbol}: {e}")
        return symbol, pd.DataFrame()

def get_all_symbols_from_s3() -> list:
    """List all stock CSVs in the S3 bucket"""
    s3 = boto3.client('s3')
    symbols = []
    try:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix='historical_data/')
        for page in pages:
            if 'Contents' not in page: continue
            for obj in page['Contents']:
                if obj['Key'].endswith('.csv'):
                    symbol = obj['Key'].split('/')[-1].replace('.csv', '')
                    symbols.append(symbol)
        return symbols
    except Exception as e:
        logger.error(f"Failed to list S3 objects: {e}")
        return []

import json

def get_tickers_from_manifest():
    try:
        with open("data/tickers.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def run_portfolio_backtest():
    """Evaluate Strategy on Full Universe with Portfolio Constraints"""
    logger.info("1. Discovery: Loading Ticker Manifest...")
    tickers = get_tickers_from_manifest()
    
    if not tickers:
        logger.info("Manifest not found. Fallback to S3 Listing...")
        tickers = get_all_symbols_from_s3()

    if not tickers:
        logger.warning("No data found. Exiting.")
        return
    
    # Ensure SPY is present
    if 'SPY' not in tickers: tickers.append('SPY')

    logger.info(f"2. Loading Data for {len(tickers)} symbols (Parallel)...")
    data_dict = {}
    
    # Pre-fetch 'SPY' specifically to ensure we have market data
    spy_symbol = 'SPY'
    if spy_symbol not in tickers: tickers.append(spy_symbol)

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(load_data, tickers)
        for symbol, df in results:
            if not df.empty:
                data_dict[symbol] = df
    
    logger.info(f"Loaded {len(data_dict)} DataFrames.")
    
    # 3. Execution
    logger.info("3. Running Portfolio Backtest (2016-2025 Out-of-Sample)...")
    engine = Backtester(initial_capital=100000.0)
    
    # Run from 2016-01-01 to test the model trained on < 2016
    engine.run_backtest(data_dict, start_date="2016-01-01")
    
    # Results are printed by analyze_results_simple inside run_backtest

if __name__ == "__main__":
    run_portfolio_backtest()
