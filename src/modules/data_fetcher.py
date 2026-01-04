"""
Module: Data Fetcher (Alpaca Edition)
Fetch market data using Alpaca Data API (v2)
"""
import os
import pandas as pd
import numpy as np
import logging
from typing import Tuple, Optional, Dict, List
from datetime import datetime, timedelta
import requests
import io
from io import BytesIO
import boto3
import json

# Alpaca Imports
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from src.modules.stock_screener import FundamentalData, TechnicalData
from src.config.constants import TREND_UP, TREND_DOWN, TREND_NEUTRAL
from src.config import settings

logger = logging.getLogger("data_fetcher")

CACHE_KEY = "market_data/universe_history.parquet"
S3_BUCKET = settings.S3_BUCKET

class DataFetchError(Exception):
    """Base exception for data fetching errors"""
    pass

class DataFetcher:
    """Fetch and process market data using Alpaca API"""
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.market_index = "QQQ"
        
        # Initialize Alpaca Client
        self.api_key = api_key or settings.get_alpaca_api_key()
        self.secret_key = secret_key or settings.get_alpaca_secret_key()
        
        self.s3_client = boto3.client('s3')
        
        if not self.api_key or not self.secret_key:
            logger.warning("Alpaca API credentials not found. Data fetching will fail.")
            self.client = None
        else:
            try:
                self.client = StockHistoricalDataClient(self.api_key, self.secret_key)
            except Exception as e:
                logger.error(f"Failed to initialize Alpaca Client: {e}")
                self.client = None
        
        self._load_sector_cache()

    def fetch_market_data(self, tickers: List[str], days: int = 400, use_cache: bool = True) -> pd.DataFrame:
        """
        Fetch market data with S3 Caching + Incremental Updates.
        Returns a DataFrame with MultiIndex (Symbol, Date) or similar structure.
        """
        full_df = pd.DataFrame()
        
        # 1. Try Load from S3
        if use_cache:
            try:
                logger.info(f"Checking S3 cache: s3://{S3_BUCKET}/{CACHE_KEY}")
                response = self.s3_client.get_object(Bucket=S3_BUCKET, Key=CACHE_KEY)
                full_df = pd.read_parquet(BytesIO(response['Body'].read()))
                logger.info(f"Loaded Cached Data: {full_df.shape}")
            except Exception as e:
                logger.info(f"Cache miss or error (will fetch full history): {e}")

        # 2. Determine Data Gaps
        start_date = datetime.now() - timedelta(days=days)
        new_data_needed = False
        
        if not full_df.empty:
            # Ensure proper types
            if 'Date' not in full_df.columns and isinstance(full_df.index, pd.MultiIndex):
                 full_df = full_df.reset_index()
            
            # Identify max date
            if 'Date' in full_df.columns:
                full_df['Date'] = pd.to_datetime(full_df['Date'])
                max_date = full_df['Date'].max()
                
                # Check if we are up to date (allow for today's data if market closed)
                # Simple check: If max_date < yesterday, fetch
                yesterday = datetime.now().date() - timedelta(days=1)
                if max_date.date() < yesterday:
                    start_date = max_date + timedelta(days=1)
                    new_data_needed = True
                    logger.info(f"Cache stale. Fetching fresh data from {start_date}")
                else:
                    logger.info("Cache is up to date.")
            else:
                 new_data_needed = True # Schema issue?
        else:
            new_data_needed = True
            
        # 3. Fetch Incremental Data (if needed)
        if new_data_needed and self.client:
            try:
                # Fetch only for needed tickers (or all if cache empty)
                # Note: fetch_bars handles chunking internally for symbols? SDK does, but safe to chunk
                logger.info(f"Fetching from Alpaca starting {start_date}...")
                
                # Use bulk fetch logic
                # We reuse fetch_bulk_history but force start date
                chunk_size = 200
                new_dfs = []
                
                for i in range(0, len(tickers), chunk_size):
                    chunk = tickers[i:i + chunk_size]
                    req = StockBarsRequest(
                        symbol_or_symbols=chunk,
                        timeframe=TimeFrame.Day,
                        start=start_date
                    )
                    bars = self.client.get_stock_bars(req)
                    
                    for symbol, symbol_bars in bars.data.items():
                        df = self._alpaca_bars_to_df(symbol_bars)
                        if not df.empty:
                            df['Symbol'] = symbol # Explicit Column
                            df.reset_index(inplace=True) # Date becomes column
                            df.rename(columns={'timestamp': 'Date'}, inplace=True)
                            new_dfs.append(df)
                            
                if new_dfs:
                    new_data = pd.concat(new_dfs)
                    logger.info(f"Fetched {len(new_data)} new rows.")
                    
                    # 4. Merge
                    if not full_df.empty:
                        # Align schemas
                        # Ensure 'Date' is datetime in both
                        if 'Date' in new_data.columns: new_data['Date'] = pd.to_datetime(new_data['Date'], utc=True)
                        if 'Date' in full_df.columns: full_df['Date'] = pd.to_datetime(full_df['Date'], utc=True)
                        
                        full_df = pd.concat([full_df, new_data])
                        # Drop duplicates: keep last
                        full_df.drop_duplicates(subset=['Symbol', 'Date'], keep='last', inplace=True)
                    else:
                        full_df = new_data
                    
                    # 5. Update Cache
                    try:
                        out_buffer = BytesIO()
                        full_df.to_parquet(out_buffer, index=False)
                        self.s3_client.put_object(Bucket=S3_BUCKET, Key=CACHE_KEY, Body=out_buffer.getvalue())
                        logger.info("Updated S3 Cache.")
                    except Exception as e:
                        logger.error(f"Failed to update cache: {e}")
                        
            except Exception as e:
                logger.error(f"Error fetching incremental data: {e}")

        # 6. Return filtered view
        # Filter for requested tickers and date range
        if full_df.empty: return pd.DataFrame()
        
        mask = (full_df['Symbol'].isin(tickers)) & (full_df['Date'] >= pd.to_datetime(start_date, utc=True))
        # Wait, start_date was for fetch. We want return data for 'days' arg.
        cutoff = datetime.now(full_df['Date'].dt.tz) - timedelta(days=days) if full_df['Date'].dt.tz else datetime.now() - timedelta(days=days)
        # Handle timezone naive/aware... Simplest is assume UTC
        cutoff = pd.Timestamp.now(tz='UTC') - timedelta(days=days)
        
        # Ensure Date is UTC
        if full_df['Date'].dt.tz is None:
             full_df['Date'] = full_df['Date'].dt.tz_localize('UTC')
             
        final_df = full_df[(full_df['Symbol'].isin(tickers)) & (full_df['Date'] >= cutoff)]
        
        # Restore Index for compatibility?
        # Consumers expect specific format?
        # fetch_batch_data expects to parse it. 
        
        return final_df
    
    def fetch_sp500_tickers(self) -> List[str]:
        """Fetch list of S&P 500 tickers from Wikipedia"""
        try:
            logger.info("Fetching S&P 500 tickers...")
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            tables = pd.read_html(io.StringIO(response.text))
            df = tables[0]
            tickers = df['Symbol'].tolist()
            tickers = [t.replace('.', '-') for t in tickers] # Alpaca uses '-' not '.'
            
            logger.info(f"Successfully fetched {len(tickers)} S&P 500 tickers")
            return tickers
        except Exception as e:
            logger.error(f"Error fetching S&P 500 tickers: {e}")
            raise DataFetchError(f"Failed to fetch S&P 500 tickers: {e}")

    def fetch_nasdaq100_tickers(self) -> List[str]:
        """Fetch list of NASDAQ 100 tickers"""
        try:
            logger.info("Fetching NASDAQ 100 tickers...")
            url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            
            tables = pd.read_html(io.StringIO(response.text))
            df = None
            for table in tables:
                if 'Ticker' in table.columns:
                    df = table; break
                elif 'Symbol' in table.columns:
                    df = table; break
            
            if df is None: return []

            col = 'Ticker' if 'Ticker' in df.columns else 'Symbol'
            tickers = df[col].tolist()
            tickers = [t.replace('.', '-') for t in tickers]
            return tickers
        except Exception as e:
            logger.error(f"Error fetching NDX tickers: {e}")
            raise DataFetchError(f"Failed to fetch NASDAQ 100 tickers: {e}")

    def fetch_key_etfs(self) -> List[str]:
        return ['SPY', 'QQQ', 'IWM', 'DIA', 'XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLP', 'XLY', 'XLU', 'XLB', 'XLC', 'XLRE', 'SMH', 'IGV', 'XBI', 'KRE', 'ARKK', 'GBTC', 'GLD', 'SLV', 'TLT']

    def fetch_full_universe(self) -> List[str]:
        logger.info("Fetching full stock universe...")
        sp500 = self.fetch_sp500_tickers()
        nasdaq = self.fetch_nasdaq100_tickers()
        etfs = self.fetch_key_etfs()
        combined = list(set(sp500 + nasdaq + etfs))
        
        # Filter out problematic tickers
        excluded = ['BF-B', 'BRK-B']
        combined = [t for t in combined if t not in excluded]
        
        combined.sort()
        logger.info(f"Full Universe: {len(combined)} unique symbols")
        return combined

    def fetch_batch_data(self, tickers: List[str]) -> Dict[str, Tuple[Optional[FundamentalData], Optional[TechnicalData]]]:
        """
        Fetch data for multiple stocks using Optimized S3 Cache + Incremental Fetch
        """
        results = {}
        rocs = []
        valid_tickers = []
        
        if not self.client:
            logger.error("Alpaca Client not initialized.")
            return {}
            
        logger.info(f"Starting Optimized Batch Fetch for {len(tickers)} tickers...")
        
        try:
            # 1. Fetch Aggregated Data
            all_data = self.fetch_market_data(tickers, days=400, use_cache=True)
            
            if all_data.empty:
                logger.warning("No data returned from fetch_market_data")
                return {}
                
            # 2. Process per ticker
            # Group by Symbol
            grouped = all_data.groupby('Symbol')
            
            for symbol, group in grouped:
                try:
                    # Convert to Format expected by _process_technical_data
                    # Needs Index=Date (Datetime)
                    df = group.set_index('Date').sort_index()
                    # Rename columns to match expected: Open, High, Low, Close, Volume
                    # Already CamelCase from _alpaca_bars_to_df conversion if it came from there?
                    # fetch_market_data normalizes to CamelCase? No it relied on _alpaca_bars_to_df which does CamelCase.
                    # But if loaded from Parquet, columns are preserved.
                    # Let's ensure columns are correct.
                    
                    if len(df) < 130: continue
                    
                    # Technicals
                    tech_data = self._process_technical_data(symbol, df)
                    if not tech_data: continue
                    
                    # Rate of Change
                    current_price = tech_data.current_price
                    price_12m_ago = df['Close'].iloc[-250] if len(df) >= 250 else df['Close'].iloc[0]
                    roc_12m = ((current_price - price_12m_ago) / price_12m_ago) * 100
                    rocs.append(roc_12m)
                    valid_tickers.append(symbol)
                    
                    # Fundamentals
                    fund_data = self._process_fundamental_data(symbol, {})
                    
                    results[symbol] = (fund_data, tech_data)
                    
                except Exception as e:
                    logger.debug(f"Error processing {symbol}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Batch fetch failed: {e}")
            return {}

        # RS Rating Calculation
        rs_scores = {}
        if rocs:
             roc_series = pd.Series(rocs, index=valid_tickers)
             pct_ranks = roc_series.rank(pct=True) * 99
             rs_scores = pct_ranks.to_dict()
        
        for ticker, (fund, tech) in results.items():
            if ticker in rs_scores:
                tech.rs_rating = rs_scores[ticker]
                
        return results

    def fetch_price_history(self, symbol: str, days: int = 400) -> pd.DataFrame:
        """
        Fetch historical price data as DataFrame (Date, Open, High, Low, Close, Volume)
        Used by MarketAnalyzer for custom calculations.
        """
        if not self.client:
            logger.error("Alpaca Client not initialized.")
            return pd.DataFrame()
            
        try:
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=datetime.now() - timedelta(days=days)
            )
            bars = self.client.get_stock_bars(request_params)
            
            if symbol not in bars.data:
                return pd.DataFrame()
                
            df = self._alpaca_bars_to_df(bars.data[symbol])
            
            # Ensure Lowercase columns if expected by Analyzer
            df.columns = [c.lower() for c in df.columns]
            return df
            
        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {e}")
            raise DataFetchError(f"Failed to fetch history for {symbol}: {e}")

    def fetch_bulk_history(self, tickers: List[str], period: str = "1y") -> pd.DataFrame:
        """
        Fetch historical data for multiple stickers and return a MultiIndex DataFrame.
        """
        if not self.client:
            logger.error("Alpaca Client not initialized.")
            return pd.DataFrame()

        days = 400
        if period == "2y": days = 730
        
        start_date = datetime.now() - timedelta(days=days)
        
        all_dfs = {}
        chunk_size = 200
        
        logger.info(f"Fetching bulk history for {len(tickers)} tickers...")
        
        for i in range(0, len(tickers), chunk_size):
            chunk = tickers[i:i + chunk_size]
            try:
                request_params = StockBarsRequest(
                    symbol_or_symbols=chunk,
                    timeframe=TimeFrame.Day,
                    start=start_date
                )
                bars = self.client.get_stock_bars(request_params)
                
                for symbol, symbol_bars in bars.data.items():
                    df = self._alpaca_bars_to_df(symbol_bars)
                    if not df.empty:
                        all_dfs[symbol] = df
                        
            except Exception as e:
                logger.error(f"Error fetching chunk {i}: {e}")
                continue
                
        if not all_dfs:
            return pd.DataFrame()
            
        try:
             # keys=tickers ensure top level index is the Ticker
            multi_df = pd.concat(all_dfs.values(), axis=1, keys=all_dfs.keys())
            return multi_df
        except Exception as e:
            logger.error(f"Error concatenating bulk data: {e}")
            raise DataFetchError(f"Failed to concatenate bulk data: {e}")

    def get_fundamental_data(self, symbol: str) -> Optional[FundamentalData]:
        """Fetch fundamental data (Placeholder for Alpaca transition)"""
        return self._process_fundamental_data(symbol, {})

    def fetch_stock_data(self, symbol: str) -> Tuple[Optional[FundamentalData], Optional[TechnicalData]]:
        """Fetch single stock data via Alpaca"""
        if not self.client: return None, None
        
        try:
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=datetime.now() - timedelta(days=400)
            )
            bars = self.client.get_stock_bars(request_params)
            
            if symbol not in bars.data:
                return None, None
                
            df = self._alpaca_bars_to_df(bars.data[symbol])
            
            tech_data = self._process_technical_data(symbol, df)
            fund_data = self._process_fundamental_data(symbol, {})
            
            return fund_data, tech_data
            
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None, None
    
    def _alpaca_bars_to_df(self, bars: List) -> pd.DataFrame:
        """Convert Alpaca Bar objects to DataFrame compatible with technical analysis"""
        data = [
            {
                'timestamp': b.timestamp,
                'Open': b.open,
                'High': b.high,
                'Low': b.low,
                'Close': b.close,
                'Volume': b.volume
            }
            for b in bars
        ]
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df

    
    def _load_sector_cache(self):
        """Load static sector map from S3"""
        try:
            key = "min_data/sectors.json"
            response = self.s3_client.get_object(Bucket=S3_BUCKET, Key=key)
            content = response['Body'].read().decode('utf-8')
            self.sector_cache = json.loads(content)
            logger.info(f"Loaded {len(self.sector_cache)} sectors from S3 cache.")
        except Exception as e:
            logger.error(f"Failed to load static sector cache from S3 (Key: {key}): {e}")
            self.sector_cache = {}

    def _process_fundamental_data(self, symbol: str, info: Dict) -> FundamentalData:
        """Fetch Fundamentals using S3 Cache then yfinance fallback"""
        sector = 'N/A'
        
        # 1. Try S3 Cache
        if hasattr(self, 'sector_cache') and symbol in self.sector_cache:
            sector = self.sector_cache[symbol]
        
        # 2. Try yfinance (with session fix)
        if sector == 'N/A' or not sector: 
            try:
                # Use yfinance for Sector (Lightweight)
                import yfinance as yf
                import requests
    
                session = requests.Session()
                session.headers.update({
             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
    
                ticker = yf.Ticker(symbol, session=session)
                # Use fast_info if available or info
                sector = ticker.info.get('sector', 'N/A')
            except Exception as e:
                logger.warning(f"Sector fetch failed for {symbol}: {e}")
                pass
            
        return FundamentalData(
            symbol=symbol,
            eps_growth=0.0,
            sales_growth=0.0,
            profit_margin=0.0,
            roe=0.0,
            debt_to_equity=0.0,
            dividend_yield=0.0,
            current_ratio=0.0,
            earnings_date=None,
            sector=sector
        )
    
    def _process_technical_data(self, symbol: str, df: pd.DataFrame) -> TechnicalData:
        """Calculate technical indicators"""
        if df.empty: return None

        current_price = df['Close'].iloc[-1]
        
        # Simple Moving Averages
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        ma_50 = df['SMA_50'].iloc[-1]
        ma_200 = df['SMA_200'].iloc[-1]
        
        high_52w = df['Close'].max()
        low_52w = df['Close'].min()
        
        date_high = df['Close'].idxmax()
        days_from_high = (df.index[-1] - date_high).days
        
        avg_vol_20d = df['Volume'].tail(20).mean()
        avg_vol_50d = df['Volume'].tail(50).mean()
        
        vol_trend = TREND_NEUTRAL
        if df['Volume'].iloc[-1] > avg_vol_50d: vol_trend = TREND_UP
        elif df['Volume'].iloc[-1] < avg_vol_50d * 0.8: vol_trend = TREND_DOWN
            
        price_trend = TREND_NEUTRAL
        if current_price > ma_50 > ma_200: price_trend = TREND_UP
        elif current_price < ma_50 < ma_200: price_trend = TREND_DOWN
            
        ma_50_dist = ((current_price - ma_50) / ma_50) * 100 if not pd.isna(ma_50) else 0
        ma_200_dist = ((current_price - ma_200) / ma_200) * 100 if not pd.isna(ma_200) else 0
        
        return TechnicalData(
            symbol=symbol,
            price_52w_high=float(high_52w),
            current_price=float(current_price),
            price_52w_low=float(low_52w),
            days_from_52w_high=int(days_from_high),
            rs_rating=50.0,
            avg_volume_20d=float(avg_vol_20d),
            avg_volume_50d=float(avg_vol_50d),
            volume_trend=vol_trend,
            price_trend=price_trend,
            ma_50_distance=float(ma_50_dist),
            ma_200_distance=float(ma_200_dist)
        )
