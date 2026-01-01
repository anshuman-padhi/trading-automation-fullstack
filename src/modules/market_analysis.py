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
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

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
    
    def __init__(self, index_symbol: str = MARKET_INDEX):
        """
        Initialize Market Analyzer
        
        Args:
            index_symbol: Market index to analyze (default: QQQ)
        """
        self.index_symbol = index_symbol
        self.short_ma = SHORT_TERM_MA
        self.intermediate_ma = INTERMEDIATE_MA
        self.long_ma = LONG_TERM_MA
        
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
        
        return bool(slope > 0)  # Convert numpy bool to Python bool
    
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
        leadership_strong: bool = True
    ) -> str:
        """
        Classify market environment into A, B, C, D, or E
        
        Args:
            short_trend: Short-term trend
            intermediate_trend: Intermediate trend
            long_trend: Long-term trend
            leadership_strong: Whether leadership is strong
        
        Returns:
            Market environment grade (A, B, C, D, E)
        """
        # A: All timeframes up, strong leadership
        if (short_trend == TREND_UP and 
            intermediate_trend == TREND_UP and 
            long_trend == TREND_UP and 
            leadership_strong):
            return "A"
        
        # B: Long-term up, short-term down, leaders weakening
        elif (long_trend == TREND_UP and 
              (short_trend == TREND_DOWN or intermediate_trend == TREND_DOWN)):
            return "B"
        
        # C: Long-term downtrend, lack of leadership
        elif long_trend == TREND_DOWN and not leadership_strong:
            return "C"
        
        # D: Long-term down, short-term up, developing leadership
        elif (long_trend == TREND_DOWN and 
              (short_trend == TREND_UP or intermediate_trend == TREND_UP)):
            return "D"
        
        # E: Choppy/mixed signals
        else:
            return "E"
    
    def analyze_market(self, price_data: pd.DataFrame) -> Dict:
        """
        Perform complete market analysis
        
        Args:
            price_data: DataFrame with columns: ['date', 'close', 'volume']
        
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Starting market analysis for {self.index_symbol}")
        
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
        # TODO: Add actual leadership analysis (for now, simplified)
        leadership_strong = bool(short_trend == TREND_UP and 
                                intermediate_trend == TREND_UP)
        
        environment = self.classify_market_environment(
            short_trend, intermediate_trend, long_trend, leadership_strong
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
            "leadership_strong": leadership_strong,
            "recommended_exposure": self._get_recommended_exposure(environment),
            "recommended_position_size": self._get_recommended_position_size(environment)
        }
        
        logger.info(f"Market analysis complete: Environment {environment}")
        
        return result
    
    def _get_recommended_exposure(self, environment: str) -> str:
        """Get recommended exposure level based on environment"""
        exposure_map = {
            "A": "80-100% (aggressive)",
            "B": "40-50% (defensive)",
            "C": "0-20% (preservation)",
            "D": "40% (cautious offense)",
            "E": "20-40% (selective)"
        }
        return exposure_map.get(environment, "Unknown")
    
    def _get_recommended_position_size(self, environment: str) -> str:
        """Get recommended position size based on environment"""
        size_map = {
            "A": "10% (up to 20% for best names)",
            "B": "5%",
            "C": "0-5% (minimal)",
            "D": "5%",
            "E": "5% or less"
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
if __name__ == "__main__":
    # Create sample data for testing
    print("Creating sample market data for testing...")
    
    dates = pd.date_range(end=datetime.now(), periods=250, freq='D')
    
    # Simulate uptrend price data
    np.random.seed(42)
    base_price = 350
    trend = np.linspace(0, 50, 250)
    noise = np.random.normal(0, 5, 250)
    prices = base_price + trend + noise
    
    sample_data = pd.DataFrame({
        'date': dates,
        'close': prices,
        'volume': np.random.randint(50000000, 150000000, 250)
    })
    
    # Initialize analyzer
    analyzer = MarketAnalyzer()
    
    # Run analysis
    result = analyzer.analyze_market(sample_data)
    
    # Print results
    print("\n" + "="*70)
    print("MARKET ANALYSIS RESULT (Sample Data)")
    print("="*70)
    print(json.dumps(result, indent=2))
    
    print("\n" + analyzer.get_market_summary(result))
    
    print("\n✅ Module 1: Market Analysis - Testing Complete!")
