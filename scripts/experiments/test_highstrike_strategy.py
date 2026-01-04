
import logging
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from modules.backtester import Backtester, Trade
import yfinance as yf

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("highstrike_test")

class HighstrikeBacktester(Backtester):
    def __init__(self, initial_capital=100000.0):
        super().__init__(initial_capital)
        self.risk_per_trade_pct = 0.03 # 3% Risk
        self.max_portfolio_risk_pct = 0.05 # 5% Total Risk
        self.profit_target_pct = 0.07 # 7% Target
        self.current_portfolio_risk = 0.0
        
    def run_backtest_highstrike(self, symbol: str, df: pd.DataFrame) -> list:
        """Run 3-5-7 Rules"""
        if df.empty or len(df) < 250: return []
        
        df = self.calculate_indicators(df)
        local_trades = []
        position = None
        
        for i in range(200, len(df)):
            date = df.index[i]
            row = df.iloc[i]
            prev = df.iloc[i-1]
            
            # --- EXIT Logic ---
            if position:
                # 7% Profit Rule: If hit +7%, take ALL profits? Or Half?
                # Highstrike implies "Aim for 7%". Let's assume Full Exit for strict adherence or Partial.
                # Let's try: Sell 50% at +7%, move stop to BE.
                
                curr_price = row['Close']
                pnl_pct = (curr_price - position.entry_price) / position.entry_price
                
                # 1. Target Hit (+7%)
                if pnl_pct >= self.profit_target_pct and not getattr(position, 'target_hit', False):
                    # Mark target hit, maybe exit half?
                    # For simplicity: EXIT ALL at 7% (High Turnover Swing Strategy)
                    # This tests the "Base Hit" approach.
                    position.exit_price = position.entry_price * (1 + self.profit_target_pct)
                    position.exit_date = date
                    position.exit_reason = "3-5-7 Target (7%)"
                    self._close_trade(position)
                    local_trades.append(position)
                    position = None
                    # Reduce Portfolio Risk
                    continue

                # 2. Stop Loss (Based on Entry Logic)
                stop_price = position.stop_price
                if row['Low'] <= stop_price:
                    position.exit_price = stop_price
                    position.exit_date = date
                    position.exit_reason = "Stop Loss"
                    self._close_trade(position)
                    local_trades.append(position)
                    position = None
                    continue
                    
            # --- ENTRY Logic ---
            elif not position:
                # Use ML Signal? Yes, keep ML filter.
                # Just change Sizing and Management.
                
                # 1. Trigger
                is_uptrend = (row['Close'] > row['SMA_50'])
                breakout = (row['Close'] > row['High_20']) and (prev['Close'] <= prev['High_20'])
                # ML Check
                # (Skipping ML inference code for brevity, assuming raw signal first)
                
                if is_uptrend and breakout:
                    # 2. Risk Calc (3% Rule)
                    atr = row['ATR']
                    stop_dist = 2 * atr
                    stop_price = row['Close'] - stop_dist
                    risk_per_share = stop_dist
                    stop_pct = stop_dist / row['Close']
                    
                    # 3% Account Risk
                    capital = self.initial_capital # Simplified (Fixed Fractional)
                    dollars_to_risk = capital * self.risk_per_trade_pct
                    
                    if risk_per_share > 0:
                        qty = dollars_to_risk / risk_per_share
                        
                        # Check 5% Portfolio Risk Rule
                        # New Risk = stop_pct * (qty * price) / capital
                        # Actually simpler: We are risking 'dollars_to_risk' which is 3% of capital.
                        # So adding this trade adds 3% to Portfolio Risk.
                        # If Max is 5%, we can only have 1 trade open (3%)? 
                        # Or maybe 2 trades (3% + 2% reduced)?
                        # "3-5-7" usually means: Max 3% per trade, Max 5% Total.
                        # This implies you can hold:
                        # - 1 trade at 3% risk
                        # - OR 2 trades at 2.5% risk
                        # - OR 5 trades at 1% risk.
                        
                        # If we strictly enforce 3% per trade, we can only have 1 trade! (Since 3+3 = 6 > 5).
                        # This seems very restrictive for a portfolio.
                        # Likely Interpretation: "Risk UP TO 3% per trade, but Total Cap 5%".
                        
                        # Implementation: Use 2.5% Risk per trade to allow 2 positions?
                        # Or 1.5% to allow 3?
                        # Let's try: Dynamic Limit.
                        # If Current Risk is 0%, take 3%. New Risk = 3%.
                        # If Current Risk is 3%, take 2%. New Risk = 5%.
                        # If Current Risk is 5%, REJECT.
                        
                        # Since this is a single-stock backtest, we can't track "Other Stocks".
                        # Evaluation: This rule is a PORTFOLIO rule.
                        # We cannot validate the "5%" rule on a single ticker backtest properly without simulating the whole portfolio.
                        
                        # We CAN validate the "Risk 3%, Target 7%" part.
                        
                        pos_size = (qty * row['Close']) / capital
                        # Cap at 1.0 leverage
                        pos_size = min(pos_size, 1.0)
                        
                        trade = Trade(symbol, date, row['Close'])
                        trade.size = pos_size
                        trade.stop_price = stop_price
                        position = trade
                        
        return local_trades

if __name__ == "__main__":
    # Load Data and Run
    print("🚀 Testing 3-5-7 Pattern (Single Stock Proxy)...")
    # For single stock, we test the "3% Risk / 7% Target" mechanics
    SYMBOLS = ["NVDA", "NFLX", "AAPL"]
    
    mh = HighstrikeBacktester()
    
    spy = yf.download("SPY", start="2005-01-01", end="2024-12-31", progress=False)
    if not spy.empty: 
        if isinstance(spy.columns, pd.MultiIndex): spy.columns = spy.columns.get_level_values(0)
        mh.set_market_data(spy)
        
    for sym in SYMBOLS:
        print(f"--- {sym} ---")
        df = yf.download(sym, start="2005-01-01", end="2024-12-31", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            trades = mh.run_backtest_highstrike(sym, df)
            
            # Analytics
            total = len(trades)
            wins = len([t for t in trades if t.pnl > 0])
            wr = (wins/total*100) if total else 0
            # Approx PnL (Sum of size-weighted returns)
            # Since size varies, we sum (ret * size)
            total_ret = sum([t.pnl * getattr(t, 'size', 1.0) for t in trades])
            
            print(f"Trades: {total}, Win Rate: {wr:.1f}%")
            print(f"Total Return Unit: {total_ret:.2f} R")
