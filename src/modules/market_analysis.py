"""
Module 1: Market Analysis
Analyzes market trends and determines trading environment
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
# import yfinance as yf # Removed
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import requests

from src.modules.data_fetcher import DataFetcher


from src.config.settings import (
    MARKET_INDEX, SHORT_TERM_MA, INTERMEDIATE_MA, LONG_TERM_MA
)
from src.config.constants import (
    TREND_UP, TREND_DOWN, TREND_NEUTRAL, MARKET_CONDITIONS
)
from src.utils.logger import setup_logger

logger = setup_logger("market_analysis", "market_analysis.log")


class MarketAnalyzer:
    """
    Analyzes market conditions and determines trading environment
    
    Uses QQQ (Nasdaq) with moving averages to determine:
    - Short-term trend (10 SMA)
    - Intermediate-term trend (21 EMA)
    - Long-term trend (200 SMA)
    - Market environment (A, B, C, D, E)
    """
    
    def __init__(self, index_symbol: str = MARKET_INDEX, data_fetcher: Optional[DataFetcher] = None):
        """
        Initialize Market Analyzer
        
        Args:
            index_symbol: Market index to analyze (default: QQQ)
            data_fetcher: Injected DataFetcher instance
        """
        self.index_symbol = index_symbol
        self.short_ma = SHORT_TERM_MA
        self.intermediate_ma = INTERMEDIATE_MA
        self.long_ma = LONG_TERM_MA
        
        # Dependency Injection with fallback (for backward compatibility/testing)
        self.data_fetcher = data_fetcher if data_fetcher else DataFetcher()
        
        logger.info(f"Initialized MarketAnalyzer for {index_symbol}")
    
    def calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate moving averages for price data
        
        Args:
            df: DataFrame with 'close' column
        
        Returns:
            DataFrame with MA columns added
        """
        df = df.copy()
        
        # Simple Moving Average for short-term
        df[f'SMA_{self.short_ma}'] = df['close'].rolling(window=self.short_ma).mean()
        
        # Exponential Moving Average for intermediate
        df[f'EMA_{self.intermediate_ma}'] = df['close'].ewm(
            span=self.intermediate_ma, adjust=False
        ).mean()
        
        # Simple Moving Average for long-term
        df[f'SMA_{self.long_ma}'] = df['close'].rolling(window=self.long_ma).mean()
        
        return df
    
    def check_ma_rising(self, ma_series: pd.Series, lookback: int = 5) -> bool:
        """
        Check if moving average is rising
        
        Args:
            ma_series: Series of MA values
            lookback: Number of periods to check
        
        Returns:
            True if MA is rising, False otherwise
        """
        if len(ma_series) < lookback:
            return False
        
        recent_values = ma_series.tail(lookback).values
        
        # Check if generally trending up
        slope = np.polyfit(range(len(recent_values)), recent_values, 1)[0]
        return slope > 0
        
    def determine_regime(self, df: pd.DataFrame) -> Tuple[str, dict]:
        """
        Determine the Market Regime (A, B, C, D) based on QQQ analysis.
        
        Rules (from Section 1):
        - Environment A (Strong Bull): Price > 10SMA and > 21EMA and > 200SMA.
        - Environment B (Rally/Correction): Price > 21EMA but < 10SMA OR < 200SMA.
        - Environment C (Bear/Downtrend): Price < 21EMA.
        """
        last_row = df.iloc[-1]
        close = last_row['close']
        sma10 = last_row[f'SMA_{self.short_ma}']
        ema21 = last_row[f'EMA_{self.intermediate_ma}']
        sma200 = last_row[f'SMA_{self.long_ma}']
        
        regime = "C" # Default to Defensive
        details = {
            "close": close, "10sma": sma10, "21ema": ema21, "200sma": sma200
        }

        # Logic Tree
        if close < ema21:
            regime = "C" # Downtrend
        elif close > sma10 and close > ema21 and close > sma200:
            regime = "A" # Strong Uptrend
        else:
            regime = "B" # Mixed / Rally attempt
            
        return regime, details
    
    def determine_trend(
        self, 
        current_price: float, 
        ma_value: float, 
        ma_rising: bool
    ) -> str:
        """
        Determine trend based on price relative to MA
        
        Args:
            current_price: Current market price
            ma_value: Moving average value
            ma_rising: Whether MA is rising
        
        Returns:
            TREND_UP, TREND_DOWN, or TREND_NEUTRAL
        """
        if pd.isna(ma_value):
            return TREND_NEUTRAL
        
        # Price above rising MA = uptrend
        if current_price > ma_value and ma_rising:
            return TREND_UP
        
        # Price below declining MA = downtrend
        elif current_price < ma_value and not ma_rising:
            return TREND_DOWN
        
        else:
            return TREND_NEUTRAL
    
    def classify_market_environment(
        self,
        short_trend: str,
        intermediate_trend: str,
        long_trend: str,
        leadership_strong: bool = True,
        breadth_metrics: Optional[Dict] = None
    ) -> str:
        """
        Classify market environment into A, B, C, D, or E
        
        Args:
            short_trend: Short-term trend
            intermediate_trend: Intermediate trend
            long_trend: Long-term trend
            leadership_strong: Whether leadership is strong
            breadth_metrics: Optional dictionary containing breadth stats
        
        Returns:
            Market environment grade (A, B, C, D, E)
        """
        # Default breadth if missing (assume neutral/positive to not break legacy logic)
        pct_above_50 = 50.0
        if breadth_metrics and 'pct_above_50ma' in breadth_metrics:
            pct_above_50 = breadth_metrics['pct_above_50ma']

        # A: All timeframes up, strong leadership, broad participation
        if (short_trend == TREND_UP and 
            intermediate_trend == TREND_UP and 
            long_trend == TREND_UP and 
            leadership_strong and
            pct_above_50 > 50):
            return "A"
        
        # B: Long-term up, short-term down, leaders weakening (or breadth diverging)
        elif (long_trend == TREND_UP and 
              (short_trend == TREND_DOWN or intermediate_trend == TREND_DOWN or pct_above_50 < 50)):
            return "B"
        
        # C: Long-term downtrend, Breadth Weak (Bear Market)
        elif long_trend == TREND_DOWN and pct_above_50 < 40:
            return "C"
        
        # D: Long-term downtrend, but Breadth Improving (Recovery/Rally attempt)
        # Price might still be below 200SMA, but >40% stocks are reclaiming 50SMA
        elif long_trend == TREND_DOWN and pct_above_50 >= 40:
            return "D"
        
        # E: Choppy/mixed signals or high volatility default
        else:
            return "E"
    
    def analyze_market(self, price_data: pd.DataFrame, breadth_metrics: Optional[Dict] = None) -> Dict:
        """
        Perform complete market analysis
        
        Args:
            price_data: DataFrame with columns: ['date', 'close', 'volume']
            breadth_metrics: Optional dictionary with breadth stats
        
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Starting market analysis for {self.index_symbol}")
        
        if price_data.empty:
            raise ValueError(f"Cannot analyze market: Price data is empty for {self.index_symbol}")
            
        # Calculate moving averages
        df = self.calculate_moving_averages(price_data)
        
        # Get current values
        current_price = df['close'].iloc[-1]
        current_date = df['date'].iloc[-1] if 'date' in df.columns else datetime.now()
        
        sma_short = df[f'SMA_{self.short_ma}'].iloc[-1]
        ema_intermediate = df[f'EMA_{self.intermediate_ma}'].iloc[-1]
        sma_long = df[f'SMA_{self.long_ma}'].iloc[-1]
        
        # Check if MAs are rising (convert to Python bool)
        short_rising = bool(self.check_ma_rising(df[f'SMA_{self.short_ma}']))
        intermediate_rising = bool(self.check_ma_rising(df[f'EMA_{self.intermediate_ma}']))
        long_rising = bool(self.check_ma_rising(df[f'SMA_{self.long_ma}']))
        
        # Determine trends
        short_trend = self.determine_trend(current_price, sma_short, short_rising)
        intermediate_trend = self.determine_trend(
            current_price, ema_intermediate, intermediate_rising
        )
        long_trend = self.determine_trend(current_price, sma_long, long_rising)
        
        # Classify environment
        # Leadership check: If breadth provided, use it. Else use price trend proxy.
        leadership_strong = True
        if breadth_metrics:
            # Strong leadership if new highs > new lows OR >50% above 50SMA
            leadership_strong = (breadth_metrics.get('new_highs', 0) > breadth_metrics.get('new_lows', 0))
        else:
             leadership_strong = bool(short_trend == TREND_UP and intermediate_trend == TREND_UP)
        
        environment = self.classify_market_environment(
            short_trend, intermediate_trend, long_trend, leadership_strong, breadth_metrics
        )
        
        # Generate Explanation
        explanation = self._get_environment_explanation(
            environment, 
            {"short_term": short_trend, "intermediate_term": intermediate_trend, "long_term": long_trend},
            breadth_metrics if breadth_metrics else {}
        )

        # Build result with explicit type conversions for JSON serialization
        result = {
            "symbol": str(self.index_symbol),
            "analysis_date": str(current_date),
            "current_price": round(float(current_price), 2),
            "moving_averages": {
                f"SMA_{self.short_ma}": round(float(sma_short), 2),
                f"EMA_{self.intermediate_ma}": round(float(ema_intermediate), 2),
                f"SMA_{self.long_ma}": round(float(sma_long), 2)
            },
            "ma_rising": {
                "short": short_rising,
                "intermediate": intermediate_rising,
                "long": long_rising
            },
            "trends": {
                "short_term": short_trend,
                "intermediate_term": intermediate_trend,
                "long_term": long_trend
            },
            "environment": environment,
            "environment_description": MARKET_CONDITIONS[environment],
            "explanation": explanation, # Added explanation
            "leadership_strong": leadership_strong,
            "breadth": breadth_metrics if breadth_metrics else "Not Available",
            "recommended_exposure": self._get_recommended_exposure(environment),
            "recommended_position_size": self._get_recommended_position_size(environment)
        }
        
        logger.info(f"Market analysis complete: Environment {environment}")
        
        return result
    
    def analyze_market_environment(self) -> Dict:
        """Fetch data and analyze market environment for Handler"""
        
        logger.info(f"Fetching market data for {self.index_symbol} via DataFetcher...")
        
        # Fetch QQQ history using injected fetcher
        try:
            df = self.data_fetcher.fetch_price_history(self.index_symbol, days=400)
        except Exception as e:
            logger.error(f"Error fetching price history: {e}")
            df = pd.DataFrame()
        
        if df.empty:
            logger.error(f"No market data found for {self.index_symbol}")
            raise ValueError(f"No market data found for {self.index_symbol}")
            
        # Calculate Breadth
        breadth = {}
        try:
            breadth = self.calculate_breadth_metrics()
        except Exception as e:
            logger.warning(f"Could not calculate breadth: {e}")
            breadth = self._get_fallback_breadth()
            
        # Perform analysis
        analysis = self.analyze_market(df, breadth_metrics=breadth)
        env = analysis['environment']
        regime = MARKET_CONDITIONS[env].split(" - ")[0]
        
        # Parse position size safely
        try:
             position_size_pct = float(self._get_recommended_exposure(env).split("-")[0].replace("%", "").strip().split(" ")[0])
        except:
             position_size_pct = 0.0
        
        # Map to handler expectations
        return {
            "regime": regime,
            "position_size_pct": position_size_pct, 
            "confidence": "High" if env in ["A", "C"] else "Medium",
            "recommendation": self._get_recommended_position_size(env),
            "exposure_guidance": self._get_recommended_exposure(env),
            "explanation": analysis.get('explanation', ''),
            "metrics": analysis
        }

    def analyze_vix(self) -> Dict:
        """Analyze VIX volatility index"""
        try:
            import os
            import boto3
            import json
            import yfinance as yf
            import requests
            from src.config import settings
            
            # Setup Cache Dir for yfinance (writeable)
            os.environ["YFINANCE_CACHE_DIR"] = "/tmp"

            # 1. Try S3 Cache first (Most Robust)
            try:
                s3 = boto3.client('s3')
                # Use bucket from env or settings
                bucket = os.getenv("S3_BUCKET", settings.S3_BUCKET)
                key = "min_data/vix_latest.json"
                response = s3.get_object(Bucket=bucket, Key=key)
                content = response['Body'].read().decode('utf-8')
                vix_data = json.loads(content)
                current_vix = vix_data.get('price', 0.0)
                logger.info(f"Loaded VIX from S3 Cache: {current_vix}")
                
                if current_vix > 0:
                     status = "Normal"
                     explanation = "Volatility is within normal range (12-20). Standard trading rules apply."
                     if current_vix > 20:
                         status = "Elevated"
                         explanation = "Volatility is elevated (>20). Reduce position sizes and tighten stops."
                     elif current_vix < 12:
                         status = "Low"
                         explanation = "Volatility is very low (<12). Expect potential mean reversion/complacency."
                         
                     return {
                        "current_vix": round(float(current_vix), 2),
                        "status": status,
                        "fear_level": status,
                        "explanation": explanation
                     }
            except Exception as e:
                logger.warning(f"S3 VIX Cache load failed: {e}")
            
            # 2. Use yfinance for VIX (NO Session, let YF handle it)
            # YF recent versions manage their own sessions better or reject requests.Session
            vix = yf.Ticker("^VIX")
            df = vix.history(period="1mo")
            
            # Fallback: Direct Request if DF empty
            current_vix = 0.0
            
            if not df.empty:
                current_vix = df['Close'].iloc[-1]
            else:
                logger.warning("VIX yfinance data empty. Trying Direct API...")
                try:
                    # Create session JUST for Direct API
                    session = requests.Session()
                    session.headers.update({
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    })
                    url = "https://query2.finance.yahoo.com/v8/finance/chart/%5EVIX?interval=1d&range=5d"
                    r = session.get(url, timeout=5)
                    if r.status_code == 200:
                        data = r.json()
                        meta = data['chart']['result'][0]['meta']
                        current_vix = meta['regularMarketPrice']
                        logger.info(f"Direct API VIX: {current_vix}")
                    else:
                        logger.error(f"Direct API failed: {r.status_code}")
                except Exception as e:
                    logger.error(f"Direct API Exception: {e}")
            
            if current_vix == 0.0:
                 logger.warning("VIX data not available from yfinance or direct.")
                 return {"current_vix": 0.0, "status": "Unknown", "fear_level": "Unknown", "explanation": "Data unavailable."}
            
            status = "Normal"
            explanation = "Volatility is within normal range (12-20). Standard trading rules apply."
            
            if current_vix > 30: 
                status = "Extreme Fear"
                explanation = "VIX > 30 indicates panic. \nImpact: High risk of whipsaws. Stopped out easily. Cash is preferred."
            elif current_vix > 20: 
                status = "High Volatility"
                explanation = "VIX > 20 suggests elevated risk. \nImpact: Reduce position sizes (50%). Widen stops slightly or wait for calm."
            elif current_vix < 12: 
                status = "Complacent"
                explanation = "VIX < 12 indicates complacency. \nImpact: Market may be overextended. Be careful chasing breakouts."
                
            logger.info(f"VIX Analysis: {current_vix:.2f} ({status})")
                
            return {
                "current_vix": round(float(current_vix), 2),
                "status": status,
                "fear_level": status,
                "explanation": explanation
            }
            
        except Exception as e:
            logger.error(f"Error analyzing VIX: {e}")
            return {"current_vix": 0.0, "status": "Unknown", "fear_level": "Unknown", "explanation": "Error analyzing VIX."}


    def calculate_breadth_metrics(self) -> Dict:
        """
        Calculate actual market breadth metrics using S&P 500 components.
        
        Fetches data for all S&P 500 stocks to calculate:
        - % of stocks above 50-day SMA
        - % of stocks above 200-day SMA
        - New Highs / New Lows (based on 52-week range)
        """
        try:
            # 1. Get Universe
            tickers = self.data_fetcher.fetch_sp500_tickers()
            if not tickers:
                logger.warning("Could not fetch tickers for breadth analysis.")
                return self._get_fallback_breadth()
                
            # 2. Fetch Bulk Data (1 year history for 200SMA)
            # Limit to 500 stocks to avoid massive payload if list is huge
            data = self.data_fetcher.fetch_bulk_history(tickers[:503], period="1y")
            
            if data.empty:
                logger.warning("Bulk data fetch failed for breadth analysis.")
                return self._get_fallback_breadth()
            
            # 3. Calculate Metrics
            # Accessing MultiIndex columns: data[('Close', 'AAPL')] or data['Close']['AAPL']
            # yfinance bulk download structure:
            # Columns: (PriceType, Ticker) -> e.g. ('Close', 'AAPL')
            # If group_by='ticker', then (Ticker, PriceType) -> e.g. ('AAPL', 'Close')
            # We used group_by='ticker' in updated data_fetcher
            
            stocks_above_50 = 0
            stocks_above_200 = 0
            new_52w_highs = 0
            new_52w_lows = 0
            total_valid_stocks = 0
            
            for ticker in tickers:
                try:
                    if ticker not in data.columns:
                        continue
                        
                    df_ticker = data[ticker]
                    
                    # Check we have enough data (at least 200 days for 200SMA)
                    # Use 'Close' column. Some tickers might be missing.
                    if 'Close' not in df_ticker.columns or len(df_ticker['Close'].dropna()) < 200:
                        continue
                        
                    # Calculate MAs
                    close_prices = df_ticker['Close']
                    current_price = close_prices.iloc[-1]
                    
                    sma_50 = close_prices.rolling(window=50).mean().iloc[-1]
                    sma_200 = close_prices.rolling(window=200).mean().iloc[-1]
                    
                    if pd.isna(current_price) or pd.isna(sma_50) or pd.isna(sma_200):
                        continue
                        
                    total_valid_stocks += 1
                    
                    if current_price > sma_50:
                        stocks_above_50 += 1
                    if current_price > sma_200:
                        stocks_above_200 += 1
                        
                    # Highs/Lows (looking at last 250 days ~ 52 weeks)
                    high_52 = close_prices.tail(250).max()
                    low_52 = close_prices.tail(250).min()
                    
                    # Check if today is a new high (within small threshold to account for intraday)
                    if current_price >= high_52 * 0.995:
                        new_52w_highs += 1
                    elif current_price <= low_52 * 1.005:
                        new_52w_lows += 1
                        
                except Exception:
                    continue
            
            if total_valid_stocks == 0:
                 return self._get_fallback_breadth()
                 
            pct_above_50 = (stocks_above_50 / total_valid_stocks) * 100
            pct_above_200 = (stocks_above_200 / total_valid_stocks) * 100
            
            logger.info(f"Breadth Analysis: Above50={pct_above_50:.1f}%, Above200={pct_above_200:.1f}% (Pop: {total_valid_stocks})")
            
            return {
                "pct_above_50ma": round(pct_above_50, 1),
                "pct_above_200ma": round(pct_above_200, 1),
                # No 20MA logic added yet, reuse 50 as proxy or add calculation above
                "pct_above_20ma": 0.0, 
                "new_highs": new_52w_highs,
                "new_lows": new_52w_lows,
                "universe_size": total_valid_stocks
            }
            
        except Exception as e:
            logger.error(f"Error calculating breadth: {e}")
            return self._get_fallback_breadth()

    def _get_fallback_breadth(self) -> Dict:
        """Return neutral fallback values if analysis fails"""
        return {
            "pct_above_20ma": 50.0,
            "pct_above_50ma": 50.0,
            "pct_above_200ma": 50.0,
            "new_highs": 0,
            "new_lows": 0,
            "universe_size": 0
        }

    def _get_environment_explanation(self, environment: str, trends: Dict, breadth: Dict) -> str:
        """Generate a descriptive 'Why' for the environment"""
        short = trends.get('short_term', 'Neutral')
        inter = trends.get('intermediate_term', 'Neutral')
        long_t = trends.get('long_term', 'Neutral')
        pct_50 = breadth.get('pct_above_50ma', 50.0) if isinstance(breadth, dict) else 50.0
        
        explanations = {
            "A": f"Strong Bull Market. Price is confirmed above all key moving averages (10, 21, 200). Leadership is broad with >50% of stocks above their 50-day SMA ({pct_50:.1f}%).",
            "B": f"Uptrend under Pressure. Long-term trend is up, but short-term weakness is visible ({short} / {inter}). Watch for support at the 50-day line.",
            "C": f"Downtrend / Bear Market. Price is below the 21-day EMA and Market Breadth is weak ({pct_50:.1f}% above 50SMA). Cash is the safest position.",
            "D": f"Market Correction / Rally Attempt. Price is in a long-term downtrend, but internal breadth is improving ({pct_50:.1f}% > 50SMA). Look for follow-through days.",
            "E": "Choppy / Volatile. Moving averages are conflicting or untrending. High volatility suggests waiting for a clear direction."
        }
        return explanations.get(environment, "Market conditions are mixed.")

    def _get_recommended_exposure(self, environment: str) -> str:
        """Get recommended exposure level based on environment"""
        exposure_map = {
            "A": "80-100% (Aggressive). Fully invested to capitalize on trend.",
            "B": "40-50% (Defensive). Reduce exposure; sell laggards and trim winners.",
            "C": "0-20% (Cash/Preservation). Protect capital; avoid new long positions.",
            "D": "40% (Cautious Offense). Test the waters with pilot positions.",
            "E": "20-40% (Selective). Trade smaller size; tight stops."
        }
        return exposure_map.get(environment, "Unknown")
    
    def _get_recommended_position_size(self, environment: str) -> str:
        """Get recommended position size based on environment"""
        size_map = {
            "A": "10-20%. High conviction. Pyramid into winners.",
            "B": "5%. Standard size. Be quick to cut losses.",
            "C": "0-5%. Minimal size if trading at all.",
            "D": "5%. Standard size. Wait for confirmation.",
            "E": "5% or less. Reduced sizing due to volatility."
        }
        return size_map.get(environment, "Unknown")
    
    def get_market_summary(self, analysis_result: Dict) -> str:
        """
        Generate human-readable market summary
        
        Args:
            analysis_result: Result from analyze_market()
        
        Returns:
            Formatted summary string
        """
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║           MARKET ANALYSIS SUMMARY - {analysis_result['symbol']}                  
╚══════════════════════════════════════════════════════════════╝

Date: {analysis_result['analysis_date']}
Current Price: ${analysis_result['current_price']}

MOVING AVERAGES:
├─ 10-day SMA:  ${analysis_result['moving_averages'][f'SMA_{self.short_ma}']}  {'✓ Rising' if analysis_result['ma_rising']['short'] else '✗ Falling'}
├─ 21-day EMA:  ${analysis_result['moving_averages'][f'EMA_{self.intermediate_ma}']}  {'✓ Rising' if analysis_result['ma_rising']['intermediate'] else '✗ Falling'}
└─ 200-day SMA: ${analysis_result['moving_averages'][f'SMA_{self.long_ma}']}  {'✓ Rising' if analysis_result['ma_rising']['long'] else '✗ Falling'}

TREND ANALYSIS:
├─ Short-term (10 SMA):       {analysis_result['trends']['short_term']}
├─ Intermediate (21 EMA):     {analysis_result['trends']['intermediate_term']}
└─ Long-term (200 SMA):       {analysis_result['trends']['long_term']}

MARKET ENVIRONMENT: {analysis_result['environment']}
{analysis_result['environment_description']}

Leadership: {'Strong ✓' if analysis_result['leadership_strong'] else 'Weak ✗'}

RECOMMENDATIONS:
├─ Recommended Exposure:      {analysis_result['recommended_exposure']}
└─ Recommended Position Size: {analysis_result['recommended_position_size']}

╚══════════════════════════════════════════════════════════════╝
"""
        return summary


# Example usage and testing
# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    print("Creating sample market data for testing...")
    
    # Use simple date range generation without freq='D' which caused environment issues
    dates = [datetime.now() - timedelta(days=x) for x in range(250)]
    dates.reverse() # Oldest to newest
    
    # Simulate uptrend price data
    np.random.seed(42)
    base_price = 350
    trend = np.linspace(0, 50, 250)
    noise = np.random.normal(0, 5, 250)
    prices = base_price + trend + noise
    
    sample_data = pd.DataFrame({
        'date': dates,
        'close': prices.tolist(),
        'volume': np.random.randint(50000000, 150000000, 250).tolist()
    })
    
    # Initialize analyzer
    analyzer = MarketAnalyzer()
    
    # Run market analysis (Standard)
    print("\nRunning Standard Analysis...")
    result = analyzer.analyze_market(sample_data)
    print(json.dumps(result, indent=2))
    
    # Run Breadth Analysis (Requires Internet)
    print("\nRunning Breadth Analysis (Live Data)...")
    try:
        breadth = analyzer.calculate_breadth_metrics()
        print(json.dumps(breadth, indent=2))
    except Exception as e:
        print(f"Breadth analysis failed: {e}")
    
    print("\n✅ Module 1: Market Analysis - Testing Complete!")
