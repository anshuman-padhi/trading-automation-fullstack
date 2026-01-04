
import pandas as pd
import numpy as np
from typing import List, Dict

import logging
logger = logging.getLogger(__name__)

class StockSelector:
    """
    Implements the "Funnel" logic from Section 2 of Reference Docs.
    Filters the broad universe into a curated 'Weekly Focus List'.
    """
    
    def __init__(self):
        pass

    def get_weekly_focus_list(self, universe_data: Dict[str, pd.DataFrame], market_data: pd.DataFrame, current_date: pd.Timestamp, regime: str = "A") -> List[str]:

        """
        Select top candidates for the week based on Market Regime.
        
        Args:
            universe_data: Dict of Symbol -> DataFrame (Full History)
            market_data: DataFrame of SPY/QQQ (Full History)
            current_date: The date to run selection for (no lookahead)
            regime: Current Market Regime ("A", "B", "C")
            
        Returns:
            List of top symbols (ranked by RS).
        """
        # 1. Regime-based settings
        if regime == "C":
            # logger.info(f"Regime C (Defensive) - No Candidates selected.")
            return []  # Defensive in Bear Market
            
        target_count = 25 if regime == "A" else 10
        min_rs_score = 0.0 if regime == "A" else 0.05  # Stricter in Regime B
        
        candidates = []
        checked = 0
        passed_liq = 0
        passed_trend = 0
        
        # Helper to safely get history up to current_date
        def get_history(df, date, lookback=200):
            # Ensure timezone-naive comparison if needed, or rely on pandas alignment
            if date not in df.index: return None
            # loc slice includes the end date
            return df.loc[:date].tail(lookback)

        # SPY 3M Return
        spy_hist = get_history(market_data, current_date, 64)
        if spy_hist is None or len(spy_hist) < 64:
            market_ret = 0.0
        else:
            market_ret = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0]) - 1
        
        for symbol, df in universe_data.items():
            # Basic Data Check
            if current_date not in df.index: continue
            checked += 1
            
            hist = get_history(df, current_date, 200)
            if hist is None or len(hist) < 200: continue
            
            row = hist.iloc[-1]
            close = row['Close']
            
            # 2. Liquidity Filter (Min $5M Daily Dollar Volume)
            avg_vol = hist['Volume'].tail(20).mean()
            dollar_vol = close * avg_vol
            if dollar_vol < 5_000_000:
                continue
            passed_liq += 1

            # 3. Trend Filter (Regime Dependent)
            ema21 = hist['Close'].ewm(span=21).mean().iloc[-1]
            sma50 = hist['Close'].rolling(50).mean().iloc[-1]
            sma200 = hist['Close'].rolling(200).mean().iloc[-1]

            is_uptrend = False
            if regime == "A":
                if close > sma50 and sma50 > sma200:
                    is_uptrend = True
            else:
                if close > ema21 and ema21 > sma50 and sma50 > sma200:
                    is_uptrend = True
            
            if not is_uptrend:
                continue
            passed_trend += 1

            # 4. Relative Strength (vs SPY)
            hist_3m = hist.tail(64)
            if len(hist_3m) < 64: continue
            
            stock_ret = (close / hist_3m['Close'].iloc[0]) - 1
            rs_score = stock_ret - market_ret
            
            if rs_score > min_rs_score:
                candidates.append({
                    'symbol': symbol,
                    'rs_score': rs_score,
                    'close': close,
                    'ret_3m': stock_ret
                })
        
        # 5. Rank and Cut
        candidates.sort(key=lambda x: x['rs_score'], reverse=True)
        top_picks = [c['symbol'] for c in candidates[:target_count]]
        
        # logger.info(f"Selector Stats: Checked={checked}, Liq={passed_liq}, Trend={passed_trend}, Candidates={len(candidates)} -> Picks={len(top_picks)}")
        
        return top_picks

    def _get_3m_return(self, df: pd.DataFrame) -> float:
        """Deprecated helper kept for interface compatibility if needed"""
        pass
