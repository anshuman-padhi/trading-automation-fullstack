"""
Module: Data Fetcher
Fetch market data using yfinance and convert to screener data objects
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Tuple, Optional, Dict, List
import requests
import io

from src.modules.stock_screener import FundamentalData, TechnicalData
from src.config.constants import TREND_UP, TREND_DOWN, TREND_NEUTRAL

logger = logging.getLogger("data_fetcher")

class DataFetcher:
    """Fetch and process market data for screening"""
    
    def __init__(self):
        self.market_index = "QQQ"  # For relative strength comparison
    
    def fetch_sp500_tickers(self) -> List[str]:
        """
        Fetch list of S&P 500 tickers
        
        Returns:
            List of ticker symbols
        """
        try:
            logger.info("Fetching S&P 500 tickers...")
            # Use requests with headers to avoid 403
            
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse table
            tables = pd.read_html(io.StringIO(response.text))
            df = tables[0]
            tickers = df['Symbol'].tolist()
            
            # Clean tickers (e.g., BRK.B -> BRK-B for yfinance)
            tickers = [t.replace('.', '-') for t in tickers]
            
            logger.info(f"Successfully fetched {len(tickers)} S&P 500 tickers")
            return tickers
            
        except Exception as e:
            logger.error(f"Error fetching S&P 500 tickers: {e}")
            # Fallback to a small sample
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'SPY', 'QQQ', 'IWM']

    def fetch_nasdaq100_tickers(self) -> List[str]:
        """
        Fetch list of NASDAQ 100 tickers
        
        Returns:
            List of ticker symbols
        """
        try:
            logger.info("Fetching NASDAQ 100 tickers...")
            
            url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse table (Usually table 4 or 5 contains components, look for 'Ticker' or 'Symbol')
            tables = pd.read_html(io.StringIO(response.text))
            
            # Find the components table
            df = None
            for table in tables:
                if 'Ticker' in table.columns:
                    df = table
                    break
                elif 'Symbol' in table.columns:
                    df = table
                    break
            
            if df is None:
                raise ValueError("Could not find NASDAQ 100 table")
                
            col = 'Ticker' if 'Ticker' in df.columns else 'Symbol'
            tickers = df[col].tolist()
            
            # Clean tickers
            tickers = [t.replace('.', '-') for t in tickers]
            
            logger.info(f"Successfully fetched {len(tickers)} NASDAQ 100 tickers")
            return tickers
            
        except Exception as e:
            logger.error(f"Error fetching NASDAQ 100 tickers: {e}")
            return [] # Return empty on fail, don't fallback here to avoid dups with SP500 fallback

    def fetch_key_etfs(self) -> List[str]:
        """
        Return list of liquid ETFs for sector/style analysis
        """
        return [
            # Major Indices
            'SPY', 'QQQ', 'IWM', 'DIA',
            # Sectors
            'XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLP', 'XLY', 'XLU', 'XLB', 'XLC', 'XLRE',
            # Sub-sectors / Styles
            'SMH', 'IGV', 'XBI', 'KRE', 'ARKK', 'GBTC', 'GLD', 'SLV', 'TLT'
        ]

    def fetch_full_universe(self) -> List[str]:
        """
        Fetch combined unique universe: S&P 500 + NASDAQ 100 + ETFs
        """
        logger.info("Fetching full stock universe...")
        
        sp500 = self.fetch_sp500_tickers()
        nasdaq = self.fetch_nasdaq100_tickers()
        etfs = self.fetch_key_etfs()
        
        # Merge and deduplicate
        combined = list(set(sp500 + nasdaq + etfs))
        combined.sort()
        
        logger.info(f"Full Universe: {len(combined)} unique symbols (SP500:{len(sp500)}, NDX:{len(nasdaq)}, ETF:{len(etfs)})")
        return combined

    def fetch_bulk_history(self, tickers: List[str], period: str = "1y") -> pd.DataFrame:
        """
        Fetch historical data via iterative approach (Bulk download is broken in this env)
        
        Args:
            tickers: List of symbols
            period: History period
            
        Returns:
            DataFrame with MultiIndex (Symbol, Date) or similar structure
        """
        # This method is kept for API compatibility but we'll implement loop inside batch_fetch
        # Returning empty to force usage of fetch_batch_data logic instead
        return pd.DataFrame()

    def fetch_batch_data(self, tickers: List[str]) -> Dict[str, Tuple[Optional[FundamentalData], Optional[TechnicalData]]]:
        """
        Fetch data for multiple stocks iteratively and calculate RS Rankings.
        
        Args:
            tickers: List of symbols
            
        Returns:
            Dict mapping symbol -> (FundamentalData, TechnicalData)
        """
        results = {}
        rocs = []
        valid_tickers = []
        
        logger.info(f"Starting iterative fetch for {len(tickers)} tickers...")
        
        # 1. Iterative Fetch & RS Calculation Preparation
        # Using a loop since yf.download is broken in this env
        
        for i, ticker in enumerate(tickers):
            try:
                # Progress log every 50
                if i % 50 == 0:
                    logger.info(f"Processing {i}/{len(tickers)}: {ticker}")
                    
                t_obj = yf.Ticker(ticker)
                
                # Fetch history
                hist = t_obj.history(period="1y")
                
                if hist.empty or len(hist) < 130:
                    continue
                
                # Calculate Technical Data immediately
                tech_data = self._process_technical_data(ticker, hist)
                
                if not tech_data:
                    continue
                    
                # Calculate ROC for RS Rating
                current_price = tech_data.current_price
                price_12m_ago = hist['Close'].iloc[-250] if len(hist) >= 250 else hist['Close'].iloc[0]
                roc_12m = ((current_price - price_12m_ago) / price_12m_ago) * 100
                
                rocs.append(roc_12m)
                valid_tickers.append(ticker)
                
                # Fetch Fundamentals (Lazy/Empty for speed or try basic)
                # In iterative mode, we could try fetching info, but it might be too slow.
                # Let's try basic info, catch error if it fails
                # To be safe for timeout, we simply start with empty fundamentals
                # and assume Screener will rely on Technicals for the first pass.
                fund_data = self._process_fundamental_data(ticker, {}) 
                
                results[ticker] = (fund_data, tech_data)
                
            except Exception as e:
                # logger.warning(f"Failed to fetch {ticker}: {e}") # Reduce log noise
                continue
                
        # 2. Calculate Percentiles for RS Rating
        rs_scores = {}
        if rocs:
             roc_series = pd.Series(rocs, index=valid_tickers)
             pct_ranks = roc_series.rank(pct=True) * 99
             rs_scores = pct_ranks.to_dict()
        
        # 3. Update RS Ratings in results
        for ticker, (fund, tech) in results.items():
            if ticker in rs_scores:
                tech.rs_rating = rs_scores[ticker]
                
        return results

    def get_fundamental_data(self, symbol: str) -> Optional[FundamentalData]:
        """
        Fetch ONLY fundamental data for a stock (no history required)
        Used for Stage 2 of screening (Deep Dive)
        """
        try:
            logger.info(f"Fetching fundamentals for {symbol}...")
            ticker = yf.Ticker(symbol)
            
            # Get info
            try:
                info = ticker.info
            except Exception:
                logger.warning(f"Could not fetch fundamentals for {symbol}")
                info = {}
                
            return self._process_fundamental_data(symbol, info)
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {str(e)}")
            return None

    def fetch_stock_data(self, symbol: str) -> Tuple[Optional[FundamentalData], Optional[TechnicalData]]:
        """
        Fetch data for a single stock
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Tuple of (FundamentalData, TechnicalData) or (None, None) if failed
        """
        try:
            logger.info(f"Fetching data for {symbol}...")
            
            # Fetch data from yfinance
            ticker = yf.Ticker(symbol)
            
            # Get historical data (1 year for 200d MA + buffer)
            history = ticker.history(period="1y")
            
            if history.empty:
                logger.warning(f"No history found for {symbol}")
                return None, None
            
            # For backward compatibility, fetch details too
            # Get info dictionary (fundamentals)
            try:
                info = ticker.info
            except Exception:
                logger.warning(f"Could not fetch fundamentals for {symbol}")
                info = {}
            
            # Process data
            fund_data = self._process_fundamental_data(symbol, info)
            tech_data = self._process_technical_data(symbol, history)
            
            return fund_data, tech_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None, None
    
    def _process_fundamental_data(self, symbol: str, info: Dict) -> FundamentalData:
        """Convert yfinance info to FundamentalData"""
        
        # Safely get values with defaults
        def get_safe(key, default=0.0):
            val = info.get(key)
            return float(val) if val is not None else default

        return FundamentalData(
            symbol=symbol,
            eps_growth=get_safe('earningsGrowth', 0) * 100,  # Convert to %
            sales_growth=get_safe('revenueGrowth', 0) * 100, # Convert to %
            profit_margin=get_safe('profitMargins', 0) * 100, # Convert to %
            roe=get_safe('returnOnEquity', 0) * 100,          # Convert to %
            debt_to_equity=get_safe('debtToEquity', 0) / 100, # Convert from %
            dividend_yield=get_safe('dividendYield', 0) * 100, # Convert to %
            current_ratio=get_safe('currentRatio', 0),
            earnings_date=None,  # yfinance often doesn't provide this reliably in info
            sector=info.get('sector', 'N/A')
        )
    
    def _process_technical_data(self, symbol: str, df: pd.DataFrame) -> TechnicalData:
        """Calculate technical indicators from history"""
        
        # Ensure we have data
        if df.empty:
             return None

        current_price = df['Close'].iloc[-1]
        
        # Moving Averages
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        ma_50 = df['SMA_50'].iloc[-1]
        ma_200 = df['SMA_200'].iloc[-1]
        
        # 52-week High/Low
        high_52w = df['Close'].max()
        low_52w = df['Close'].min()
        
        # Days from 52w high
        date_high = df['Close'].idxmax()
        days_from_high = (df.index[-1] - date_high).days
        
        # Volume averages
        avg_vol_20d = df['Volume'].tail(20).mean()
        avg_vol_50d = df['Volume'].tail(50).mean()
        
        # Volume Trend (Simple)
        vol_trend = TREND_NEUTRAL
        if df['Volume'].iloc[-1] > avg_vol_50d:
            vol_trend = TREND_UP
        elif df['Volume'].iloc[-1] < avg_vol_50d * 0.8:
            vol_trend = TREND_DOWN
            
        # Price Trend (based on MAs)
        price_trend = TREND_NEUTRAL
        if current_price > ma_50 > ma_200:
            price_trend = TREND_UP
        elif current_price < ma_50 < ma_200:
            price_trend = TREND_DOWN
            
        # Distances
        ma_50_dist = ((current_price - ma_50) / ma_50) * 100 if not pd.isna(ma_50) else 0
        ma_200_dist = ((current_price - ma_200) / ma_200) * 100 if not pd.isna(ma_200) else 0
        
        # RS Rating will be calculated externally by the batch processor
        # For single fetch, we leave it as placeholder 50
        rs_rating = 50.0 
        
        return TechnicalData(
            symbol=symbol,
            price_52w_high=float(high_52w),
            current_price=float(current_price),
            price_52w_low=float(low_52w),
            days_from_52w_high=int(days_from_high),
            rs_rating=float(rs_rating),
            avg_volume_20d=float(avg_vol_20d),
            avg_volume_50d=float(avg_vol_50d),
            volume_trend=vol_trend,
            price_trend=price_trend,
            ma_50_distance=float(ma_50_dist),
            ma_200_distance=float(ma_200_dist)
        )
