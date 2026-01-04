
import logging
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
from typing import List
import sys
import os

# Add project root to path (so 'src.modules' works)
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
# Also add src directly if needed for direct module imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from modules.backtester import Backtester, Trade
from modules.data_fetcher import DataFetcher

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("monte_carlo")

def calculate_sharpe(returns: List[float], risk_free_rate: float = 0.03) -> float:
    """Calculate Annualized Sharpe Ratio from trade returns"""
    if len(returns) < 2:
        return 0.0
    
    # Assuming avg holding period of 10 days -> ~25 trades per year equivalent?
    # Actually, simpler: Sharpe = (Mean Return - Rf) / StdDev
    # We need to annualize appropriately. 
    # Approx: Mean Trade Return * Trades_Per_Year - Rf
    
    # A robust way for discrete trades:
    # 1. Convert to daily equity curve
    # 2. Daily Sharpe * sqrt(252)
    # But here we have list of trade returns.
    
    # Let's use the simplest robust proxy:
    # Sharpe = (Avg Return / StdDev) * sqrt(Trades Per Year)
    # Assume 250 days / avg hold time (10 days) * concurrency
    
    avg_ret = np.mean(returns)
    std_ret = np.std(returns)
    
    if std_ret == 0:
        return 0.0
        
    trades_per_year = len(returns) / 20.0 # Over 20 years
    if trades_per_year == 0:
        return 0.0
        
    # Annualized Sharpe Approximation
    sharpe = (avg_ret / std_ret) * np.sqrt(trades_per_year) 
    return sharpe

def run_random_entry_validation(backtester: Backtester, symbols: List[str], num_simulations: int = 100):
    """
    Run Random Entry Validation.
    Compare Real Strategy vs 100 Random Strategies.
    Random Strategy: Enters randomly, uses SAME exit logic (Stop/Target).
    """
    import random
    
    # 1. Get Real Performance
    print("Running Real Strategy...")
    real_trades = []
    # (Simplified: logic moved here to avoid duplicated code if I refactor properly, 
    # but for now assume we pass processed DFs or re-fetch. 
    # To save time, we will assume 'real_trades' passed in or calculated outside).
    pass 

def simulate_random_trades(trade_count: int, all_daily_returns: pd.Series, avg_duration: int = 10):
    """
    Fast Proxy: Pick random start dates, hold for avg_duration.
    """
    possible_starts = len(all_daily_returns) - avg_duration
    if possible_starts < 1: return []
    
    random_starts = np.random.randint(0, possible_starts, size=trade_count)
    pnl_samples = []
    
    # Vectorized approach or loop
    # Loop is fine for 100k iters
    for start in random_starts:
        # Calculate N-day return
        # (Close[start+N] - Close[start]) / Close[start]
        # Faster: (Cumulative[start+N] / Cumulative[start]) - 1
        ret = (all_daily_returns.iloc[start+avg_duration] / all_daily_returns.iloc[start]) - 1
        pnl_samples.append(ret)
        
    return pnl_samples

if __name__ == "__main__":
    print("🚀 Starting Monte Carlo: Random Entry Validation")
    
    # 1. Setup & Data Fetch
    SYMBOLS = ["NVDA", "AMD", "NFLX", "META", "AMZN", "TSLA", "AAPL", "GOOGL", "MSFT", "CRM"]
    backtester = Backtester(initial_capital=100000.0)
    
    import yfinance as yf
    
    # Set Market Data
    spy = yf.download("SPY", start="2005-01-01", end="2024-12-31", progress=False)
    if not spy.empty:
        if isinstance(spy.columns, pd.MultiIndex): spy.columns = spy.columns.get_level_values(0)
        backtester.set_market_data(spy)
        
    all_data = {}
    real_trades = []
    
    print("1. Generating Real Trades...")
    for symbol in SYMBOLS:
        try:
            df = yf.download(symbol, start="2005-01-01", end="2024-12-31", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                all_data[symbol] = df['Close']
                trades = backtester.run_backtest(symbol, df)
                real_trades.extend(trades)
        except Exception as e:
            print(f"Error {symbol}: {e}")
            
    real_sharpe = calculate_sharpe([t.pnl for t in real_trades])
    avg_duration = 20 # Default assumption if calculation fails
    
    if real_trades:
        durations = [(t.exit_date - t.entry_date).days for t in real_trades if t.exit_date and t.entry_date]
        if durations:
            avg_duration = int(np.mean(durations))
            
    print(f"Real Sharpe: {real_sharpe:.4f}")
    print(f"Total Trades: {len(real_trades)}")
    print(f"Avg Duration: {avg_duration} days")
    
    # 2. Random Entry Simulation
    print("2. Running 1000 Random Simulations...")
    random_sharpes = []
    
    # Pre-process data for speed
    # Create list of (Symbol, Log Returns Series or Price Series)
    
    for _ in range(1000):
        # Build a random portfolio of N trades
        sim_pnls = []
        for _ in range(len(real_trades)):
            # Pick a random stock
            sym = np.random.choice(list(all_data.keys()))
            prices = all_data[sym]
            
            # Pick random start
            if len(prices) > avg_duration + 10:
                start_idx = np.random.randint(0, len(prices) - avg_duration - 1)
                entry = prices.iloc[start_idx]
                exit_price = prices.iloc[start_idx + avg_duration]
                pnl = (exit_price - entry) / entry
                sim_pnls.append(pnl)
            else:
                sim_pnls.append(0.0)
                
        r_sharpe = calculate_sharpe(sim_pnls)
        random_sharpes.append(r_sharpe)
        
    random_sharpes = np.array(random_sharpes)
    p_value = np.sum(random_sharpes >= real_sharpe) / 1000
    
    print("\n" + "="*50)
    print("🎰 RANDOM ENTRY VALIDATION RESULTS")
    print("="*50)
    print(f"Original Sharpe: {real_sharpe:.4f}")
    print(f"Mean Random Sharpe: {np.mean(random_sharpes):.4f}")
    print(f"95th Percentile Random Sharpe: {np.percentile(random_sharpes, 95):.4f}")
    print(f"P-Value: {p_value:.4f}")
    
    if p_value < 0.05:
        print("✅ RESULT: SIGNIFICANT SKILL (Beats Luck)")
    else:
        print("⚠️ RESULT: NOT SIGNIFICANT (Indistinguishable from Luck)")
    print("="*50)
