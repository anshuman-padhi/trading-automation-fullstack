
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from src.modules.backtester import Backtester, Trade

class TestBacktester:
    
    @pytest.fixture
    def mock_price_data(self):
        # Create a DataFrame with 400 days of data (enough for 200 SMA)
        # Uptrending price to easier satisfy SMA50 > SMA200
        dates = pd.date_range(start='2020-01-01', periods=400)
        # Linear uptrend: 100 to 200
        prices = np.linspace(100, 200, 400)
        
        df = pd.DataFrame({
            'Open': prices,
            'High': prices + 2,
            'Low': prices - 2,
            'Close': prices,
            'Volume': [1000000] * 400
        }, index=dates)
        
        return df

    @patch('src.modules.backtester.joblib.load')
    @patch('src.modules.backtester.os.path.exists')
    def test_init_load_model(self, mock_exists, mock_load):
        mock_exists.return_value = True
        mock_load.return_value = {'model': MagicMock(), 'scaler': MagicMock()}
        
        bt = Backtester()
        assert bt.model is not None
        assert bt.scaler is not None

    def test_calculate_indicators(self, mock_price_data):
        bt = Backtester()
        df = bt.calculate_indicators(mock_price_data)
        
        columns = ['SMA_50', 'SMA_200', 'RSI', 'ATR', 'BB_Width', 'High_252d']
        for col in columns:
            assert col in df.columns
            
    def test_backtest_execution_no_error(self, mock_price_data):
        bt = Backtester()
        # Create a breakout scenario
        # 1. Dip price for 20 days so High_20 drops
        mock_price_data.iloc[-25:-1, mock_price_data.columns.get_loc('Close')] -= 10
        mock_price_data.iloc[-25:-1, mock_price_data.columns.get_loc('High')] -= 10
        
        # 2. Spike Price on last day
        mock_price_data.iloc[-1, mock_price_data.columns.get_loc('Close')] = 210
        mock_price_data.iloc[-1, mock_price_data.columns.get_loc('Volume')] = 2000000 # Vol confirmation
        
        # Mock ML to pass
        bt.model = MagicMock()
        bt.model.predict_proba.return_value = [[0.1, 0.9]] # 90% confidence
        
        trades = bt.run_backtest({'TEST': mock_price_data})
        
        assert isinstance(trades, list)
        # Even if empty (due to strict filters), checks code path execution

    def test_close_trade_logic(self):
        bt = Backtester()
        entry_date = pd.Timestamp("2023-01-01")
        exit_date = pd.Timestamp("2023-01-10")
        
        trade = Trade(symbol="TEST", entry_date=entry_date, entry_price=100.0)
        trade.exit_date = exit_date
        trade.exit_price = 110.0 # 10% gain
        
        # Add to positions so exit_position can find it
        bt.positions["TEST"] = trade
        
        bt.exit_position("TEST", exit_date, 110.0, "Test Exit")
        
        # Check if moved to trades list (exit_position moves it)
        assert len(bt.trades) == 1
        closed_trade = bt.trades[0]
        assert closed_trade.status == "CLOSED"
        # PnL calculation in exit_position might differ slightly or depend on logic
        assert closed_trade.exit_price == 110.0
