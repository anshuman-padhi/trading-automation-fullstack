import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.modules.stock_screener import FundamentalData, TechnicalData
from src.config.constants import TREND_UP, TREND_DOWN, TREND_NEUTRAL

@pytest.fixture
def mock_price_history():
    """Create a sample 1-year price history DataFrame"""
    dates = pd.date_range(end=datetime.now(), periods=250, freq='B')
    # Create an uptrend
    closes = np.linspace(100, 150, 250) + np.random.normal(0, 2, 250)
    df = pd.DataFrame({
        'Open': closes * 0.99,
        'High': closes * 1.02,
        'Low': closes * 0.98,
        'Close': closes,
        'Volume': np.random.randint(1000000, 5000000, 250)
    }, index=dates)
    return df

@pytest.fixture
def mock_fundamental_data():
    """Create a strong fundamental data object (CANSLIM style)"""
    return FundamentalData(
        symbol="TEST",
        eps_growth=60.0,      # > 50 for max
        sales_growth=30.0,    # > 25 for max
        profit_margin=20.0,   # > 15 for max
        roe=30.0,             # > 25 for max
        debt_to_equity=0.1,   # < 0.5 for max
        dividend_yield=1.0,
        current_ratio=2.0,
        earnings_date=datetime.now() + timedelta(days=30)
    )

@pytest.fixture
def mock_technical_data():
    """Create a strong technical data object"""
    return TechnicalData(
        symbol="TEST",
        price_52w_high=160.0,
        current_price=150.0,
        price_52w_low=100.0,
        days_from_52w_high=5,
        rs_rating=90.0,
        avg_volume_20d=2000000.0,
        avg_volume_50d=1800000.0,
        volume_trend=TREND_UP,
        price_trend=TREND_UP,
        ma_50_distance=5.0,
        ma_200_distance=15.0
    )

@pytest.fixture
def mock_breadth_metrics():
    """Create sample breadth metrics for environment classification"""
    return {
        'pct_above_50ma': 75.0,
        'pct_above_200ma': 65.0,
        'new_highs': 50,
        'new_lows': 5,
        'advance_decline_ratio': 2.5
    }
