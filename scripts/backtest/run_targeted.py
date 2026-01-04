
import sys
import os
import boto3
import pandas as pd
import logging
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modules.backtester import Backtester

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("backtest_sample")

S3_BUCKET = os.environ.get("S3_BUCKET", "trading-automation-data-904583676284")

def load_data(symbol: str) -> pd.DataFrame:
    try:
        s3 = boto3.client('s3')
        key = f"historical_data/{symbol}.csv"
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        df = pd.read_csv(obj['Body'], index_col=0, parse_dates=True)
        return df
    except Exception as e:
        logger.warning(f"Could not load {symbol}: {e}")
        return pd.DataFrame()

def run_comparison():
    tickers = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'NVDA', 'TSLA', 'NFLX', 'AMD', 'META', 'CRM']
    
    # helper
    def run_batch(name, use_ml_filter=False):
        logger.info(f"\n🚀 Running {name} Strategy...")
        bt = Backtester()
        
        # Load SPY
        spy_df = load_data("SPY")
        if not spy_df.empty: bt.set_market_data(spy_df)

        if not use_ml_filter:
            bt.model = None # Disable ML
            
        all_trades = []
        for sym in tickers:
            df = load_data(sym)
            if df.empty: continue
            trades = bt.run_backtest(sym, df)
            all_trades.extend(trades)
            
        return bt.analyze_results(all_trades, duration_years=20), all_trades

    # 1. Run Rule-Based
    metrics_rule, trades_rule = run_batch("Rule-Based (Baseline)", use_ml_filter=False)
    
    # 2. Run ML-Based
    metrics_ml, trades_ml = run_batch("Advanced ML", use_ml_filter=True)
    
    # 3. Print Comparison
    print("\n" + "="*80)
    print("STRATEGY COMPARISON (20 Years)")
    print("="*80)
    print(f"{'METRIC':<20} {'RULE-BASED':<15} {'ADVANCED ML':<15} {'DELTA':<10}")
    print("-" * 80)
    
    for key in ['Win Rate', 'CAGR', 'Sharpe Ratio', 'Calmar Ratio', 'Max Drawdown', 'Total Trades']:
        v1 = metrics_rule.get(key, 0)
        v2 = metrics_ml.get(key, 0)
        
        # Format
        if key in ['Sharpe Ratio', 'Calmar Ratio']:
            diff = v2 - v1
            print(f"{key:<20} {v1:<15.2f} {v2:<15.2f} {diff:+.2f}")
        elif key == 'Total Trades':
            diff = v2 - v1
            print(f"{key:<20} {v1:<15} {v2:<15} {diff:+}")
        else: # Percentages
            diff = v2 - v1
            print(f"{key:<20} {v1:<14.1f}% {v2:<14.1f}% {diff:+.1f}%")
            
    print("="*80)
    
    # 4. Bias Analysis (Recency Check)
    print("\n🕵️ BIAS ANALYSIS (Recency Check - Advanced ML)")
    print("-" * 80)
    trades_ml.sort(key=lambda x: x.entry_date)
    if trades_ml:
        mid_idx = len(trades_ml) // 2
        mid_date = trades_ml[mid_idx].entry_date
        
        first_half = trades_ml[:mid_idx]
        second_half = trades_ml[mid_idx:]
        
        # Calculate Win Rates
        wr1 = len([t for t in first_half if t.pnl > 0]) / len(first_half) * 100
        wr2 = len([t for t in second_half if t.pnl > 0]) / len(second_half) * 100
        
        print(f"Split Date: {mid_date.date()}")
        print(f"First Half Win Rate:  {wr1:.1f}% ({len(first_half)} trades)")
        print(f"Second Half Win Rate: {wr2:.1f}% ({len(second_half)} trades)")
        
        if abs(wr1 - wr2) < 10:
            print("✅ Result: Robust (Consistent performance across decades)")
        elif wr2 > wr1 + 10:
            print("⚠️ Result: Potential Recency Bias (Performance improved recently)")
        else:
            print("⚠️ Result: Decay (Performance degraded recently)")
            
if __name__ == "__main__":
    run_comparison()
