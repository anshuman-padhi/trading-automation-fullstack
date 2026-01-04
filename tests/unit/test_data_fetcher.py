import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.modules.data_fetcher import DataFetcher
from datetime import datetime

class TestDataFetcher:
    
    @pytest.fixture
    def fetcher(self):
        with patch('src.modules.data_fetcher.StockHistoricalDataClient'):
             return DataFetcher(api_key="test", secret_key="test")

    @patch('src.modules.data_fetcher.requests.get')
    def test_fetch_sp500_tickers(self, mock_get, fetcher):
        # Mock Wiki Response
        mock_response = MagicMock()
        mock_response.text = '<html><table><tr><th>Symbol</th></tr><tr><td>MMM</td></tr><tr><td>ABT</td></tr></table></html>'
        mock_get.return_value = mock_response
        
        # Mock pd.read_html
        with patch('src.modules.data_fetcher.pd.read_html') as mock_read_html:
            mock_read_html.return_value = [pd.DataFrame({'Symbol': ['MMM', 'ABT']})]
            
            tickers = fetcher.fetch_sp500_tickers()
            assert len(tickers) == 2
            assert 'MMM' in tickers

    @patch('src.modules.data_fetcher.requests.get')
    def test_fetch_nasdaq100_tickers(self, mock_get, fetcher):
        # Mock Wiki Response
        mock_response = MagicMock()
        mock_response.text = '<html></html>'
        mock_get.return_value = mock_response
        
        with patch('src.modules.data_fetcher.pd.read_html') as mock_read_html:
            mock_read_html.return_value = [pd.DataFrame({'Ticker': ['AAPL', 'MSFT']})]
            
            tickers = fetcher.fetch_nasdaq100_tickers()
            assert len(tickers) == 2
            assert 'AAPL' in tickers

    def test_fetch_key_etfs(self, fetcher):
        etfs = fetcher.fetch_key_etfs()
        assert 'SPY' in etfs
        assert 'QQQ' in etfs
        assert len(etfs) > 10

    def test_process_technical_data(self, fetcher):
        # Create mock DataFrame
        dates = pd.date_range(end=datetime.now(), periods=250)
        df = pd.DataFrame({
            'Close': [100 + i for i in range(250)],
            'Volume': [1000000] * 250,
            'High': [105 + i for i in range(250)],
            'Low': [95 + i for i in range(250)],
            'Open': [100 + i for i in range(250)]
        }, index=dates)
        
        # Test internal processing logic
        tech = fetcher._process_technical_data('TEST', df)
        
        assert tech.symbol == 'TEST'
        assert tech.current_price > 0
        assert tech.ma_50_distance is not None
        assert tech.rs_rating == 50.0 

    def test_fetch_price_history_alpaca(self, fetcher):
        # Mock Alpaca Client Response
        mock_bar = MagicMock()
        mock_bar.timestamp = pd.Timestamp.now()
        mock_bar.open = 100
        mock_bar.high = 110
        mock_bar.low = 90
        mock_bar.close = 105
        mock_bar.volume = 1000
        
        mock_response = MagicMock()
        mock_response.data = {'AAPL': [mock_bar]}
        
        fetcher.client.get_stock_bars.return_value = mock_response
        
        df = fetcher.fetch_price_history('AAPL', days=10)
        
        assert not df.empty
        assert 'close' in df.columns # Should be lowercase
        assert df['close'].iloc[0] == 105
