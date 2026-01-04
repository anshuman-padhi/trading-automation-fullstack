
import sys
import os
import boto3
import pandas as pd
import yfinance as yf
import logging
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modules.backtester import Backtester

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("tqqq_test")

S3_BUCKET = os.environ.get("S3_BUCKET", "trading-automation-data-904583676284")

def get_data(symbol: str) -> pd.DataFrame:
    """Try S3, then fallback to YFinance"""
    # 1. Try S3
    try:
        s3 = boto3.client('s3')
        key = f"historical_data/{symbol}.csv"
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        df = pd.read_csv(obj['Body'], index_col=0, parse_dates=True)
        logger.info(f"Loaded {symbol} from S3.")
        return df
    except:
        logger.info(f"{symbol} not in S3, downloading from YFinance...")
        
    # 2. Fallback YFinance
    try:
        df = yf.download(symbol, period="max", progress=False)
        if df.empty:
            return pd.DataFrame()
        # Flat columns if needed
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        logger.error(f"Failed to fetch {symbol}: {e}")
        return pd.DataFrame()

def test_tqqq():
    logger.info("🚀 Testing Advanced ML Strategy on TQQQ (3x Leveraged Nasdaq)...")
    
    # 1. Init Backtester
    bt = Backtester()
    
    # 2. Load Market Data (SPY) for ML Features
    spy_df = get_data("SPY")
    if not spy_df.empty:
        bt.set_market_data(spy_df)
    else:
        logger.warning("SPY missing! ML features will be wrong.")

    # 3. Load TQQQ
    tqqq_df = get_data("TQQQ")
    if tqqq_df.empty:
        logger.error("Could not load TQQQ data.")
        return

    # 4. Run Backtest
    trades = bt.run_backtest("TQQQ", tqqq_df)
    
    # 5. Analyze
    if not trades:
        logger.warning("No trades taken.")
        return
        
    duration_days = (tqqq_df.index[-1] - tqqq_df.index[0]).days
    years = max(duration_days / 365.25, 0.1)
    
    metrics = bt.analyze_results(trades, duration_years=years)
    
    logger.info("\n" + "="*40)
    logger.info("TQQQ RESULTS (ML Filtered)")
    logger.info("="*40)
    logger.info(f"Data Period: {tqqq_df.index[0].date()} to {tqqq_df.index[-1].date()}")
    logger.info(f"Total Trades: {metrics['Total Trades']}")
    logger.info(f"Win Rate: {metrics['Win Rate']:.1f}%")
    logger.info(f"CAGR: {metrics['CAGR']:.1f}%")
    logger.info(f"Total Return: {metrics['Total Return']:.1f}%")
    logger.info(f"Max Drawdown: {metrics.get('Max Drawdown', 0):.1f}%")
    logger.info(f"Sortino Ratio: {metrics['Sortino Ratio']:.2f}")

    # Visualize recent trades
    logger.info("\nRecent Trades:")
    for t in trades[-5:]:
        logger.info(f"{t.entry_date.date()} -> {t.exit_date.date() if t.exit_date else 'OPEN'}: {t.return_pct:.1f}%")

if __name__ == "__main__":
    test_tqqq()
