"""
Market Breadth Calculator - Phase 2A
Calculates market-wide breadth indicators to provide context for individual stock signals.
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MarketBreadthCalculator:
    """
    Calculates breadth indicators from a universe of stocks.
    Provides market context signals like % above 200 SMA, advance/decline, etc.
    """
    
    def __init__(self, stock_universe: Dict[str, pd.DataFrame]):
        """
        Initialize with a universe of stock dataframes.
        
        Args:
            stock_universe: Dict mapping symbol -> DataFrame with OHLCV + indicators
        """
        self.universe = stock_universe
        self.cache = {}  # Cache breadth by date
        logger.info(f"Initialized MarketBreadthCalculator with {len(stock_universe)} stocks")
        
    def calculate_daily_breadth(self, date: pd.Timestamp) -> dict:
        """
        Calculate breadth indicators for a specific trading day.
        
        Returns dict with:
        - pct_above_200sma: % of stocks above 200-day SMA
        - pct_at_52w_high: % of stocks near 52-week high (within 2%)
        - adv_dec_ratio: Advancing stocks / Declining stocks
        - new_highs_lows: (52W highs - 52W lows) / total stocks
        """
        # Check cache
        date_key = date.strftime('%Y-%m-%d')
        if date_key in self.cache:
            return self.cache[date_key]
        
        stocks_data = []
        
        for symbol, df in self.universe.items():
            if date not in df.index:
                continue
                
            try:
                row = df.loc[date]
                
                # Skip if missing critical data
                if pd.isna(row.get('Close')) or pd.isna(row.get('SMA_200')):
                    continue
                
                stocks_data.append({
                    'close': row['Close'],
                    'prev_close': row.get('Close_prev', row['Close']),
                    'high_252d': row.get('High_252d', row['High']),
                    'low_252d': row.get('Low_252d', row['Low']),
                    'sma_200': row.get('SMA_200', row['Close'])
                })
            except Exception as e:
                continue
        
        if len(stocks_data) < 50:  # Need minimum sample size
            result = self._default_breadth()
        else:
            result = self._calculate_metrics(stocks_data)
        
        # Cache result
        self.cache[date_key] = result
        return result
    
    def _calculate_metrics(self, stocks_data: list) -> dict:
        """Calculate actual breadth metrics from stock data"""
        total = len(stocks_data)
        
        # 1. % Above 200-day SMA
        above_200sma = sum(1 for s in stocks_data if s['close'] > s['sma_200'])
        pct_above_200sma = (above_200sma / total) * 100
        
        # 2. % At 52-week high (within 2%)
        at_52w_high = sum(1 for s in stocks_data 
                         if s['close'] >= s['high_252d'] * 0.98)
        pct_at_52w_high = (at_52w_high / total) * 100
        
        # 3. % At 52-week low (within 2%)
        at_52w_low = sum(1 for s in stocks_data 
                        if s['close'] <= s['low_252d'] * 1.02)
        
        # 4. Advance/Decline Ratio
        advancing = sum(1 for s in stocks_data if s['close'] > s['prev_close'])
        declining = total - advancing
        adv_dec_ratio = advancing / max(declining, 1)
        
        # 5. New Highs - New Lows (normalized)
        new_highs_lows = (at_52w_high - at_52w_low) / total * 100
        
        return {
            'pct_above_200sma': round(pct_above_200sma, 2),
            'pct_at_52w_high': round(pct_at_52w_high, 2),
            'adv_dec_ratio': round(adv_dec_ratio, 3),
            'new_highs_lows': round(new_highs_lows, 2),
        }
    
    def _default_breadth(self) -> dict:
        """Return neutral/default breadth values"""
        return {
            'pct_above_200sma': 50.0,
            'pct_at_52w_high': 5.0,
            'adv_dec_ratio': 1.0,
            'new_highs_lows': 0.0,
        }
    
    def clear_cache(self):
        """Clear the breadth cache (useful for backtesting)"""
        self.cache = {}


def fetch_vix_data(start_date='2006-01-01', end_date='2025-12-31') -> pd.DataFrame:
    """
    Fetch VIX (CBOE Volatility Index) data from Yahoo Finance.
    
    Returns DataFrame with VIX close values indexed by date.
    """
    try:
        import yfinance as yf
        
        logger.info(f"Fetching VIX data from {start_date} to {end_date}...")
        vix = yf.download('^VIX', start=start_date, end=end_date, progress=False)
        
        if vix.empty:
            logger.warning("No VIX data returned from Yahoo Finance")
            return pd.DataFrame()
        
        # Clean and prepare
        vix = vix[['Close']].rename(columns={'Close': 'VIX'})
        vix.index = pd.to_datetime(vix.index)
        
        # Forward fill missing dates
        vix = vix.ffill()
        
        logger.info(f"Fetched {len(vix)} VIX data points ({vix.index[0]} to {vix.index[-1]})")
        return vix
        
    except ImportError:
        logger.error("yfinance not installed. Run: pip install yfinance")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Failed to fetch VIX data: {e}")
        return pd.DataFrame()


def load_cached_vix(cache_path='data/cache/vix_data.csv') -> Optional[pd.DataFrame]:
    """Load VIX data from cache if available"""
    try:
        import os
        if os.path.exists(cache_path):
            vix = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            logger.info(f"Loaded VIX from cache: {len(vix)} points")
            return vix
    except Exception as e:
        logger.warning(f"Failed to load cached VIX: {e}")
    return None


def save_vix_cache(vix_df: pd.DataFrame, cache_path='data/cache/vix_data.csv'):
    """Save VIX data to cache"""
    try:
        import os
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        vix_df.to_csv(cache_path)
        logger.info(f"Saved VIX cache to {cache_path}")
    except Exception as e:
        logger.warning(f"Failed to save VIX cache: {e}")
