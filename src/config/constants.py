"""
Constants for trading automation system
"""

# Market Conditions
MARKET_CONDITIONS = {
    "A": "Strong Uptrend - All timeframes up, strong leadership",
    "B": "Long-term up, Short-term down, Leaders weakening",
    "C": "Long-term downtrend, Lack of leadership",
    "D": "Long-term down, Short-term up, Developing leadership",
    "E": "Choppy - Mixed signals, Unreliable leadership"
}

# Position Sizing by Environment
ENVIRONMENT_POSITION_SIZE = {
    "A": 0.08,  # 8% per position in strong uptrend
    "B": 0.06,  # 6% in mixed conditions
    "C": 0.04,  # 4% in downtrend
    "D": 0.02   # 2% in recovery phase
}

# Risk Management
MAX_PORTFOLIO_RISK = 0.02  # 2% of portfolio per trade
MAX_DAILY_LOSS = 0.05      # 5% max daily loss
MAX_DRAWDOWN = 0.20        # 20% max drawdown threshold

# Trend Definitions
TREND_UP = "UP"
TREND_DOWN = "DOWN"
TREND_NEUTRAL = "NEUTRAL"

# Moving Average Periods
MA_PERIODS = {
    "short": 10,
    "intermediate": 21,
    "long": 200
}
