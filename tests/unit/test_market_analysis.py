import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.modules.market_analysis import MarketAnalyzer
from src.config.constants import TREND_UP, TREND_DOWN, TREND_NEUTRAL

class TestMarketAnalyzer:
    
    @pytest.fixture
    def mock_fetcher(self):
        return MagicMock()

    @pytest.fixture
    def analyzer(self, mock_fetcher):
        return MarketAnalyzer(data_fetcher=mock_fetcher)
    
    @pytest.fixture
    def mock_price_history(self):
        dates = pd.date_range(end=pd.Timestamp.now(), periods=250)
        df = pd.DataFrame({
            'close': [100 + i for i in range(250)],
            'volume': [1000000] * 250
        }, index=dates)
        return df

    def test_calculate_moving_averages(self, analyzer, mock_price_history):
        df = analyzer.calculate_moving_averages(mock_price_history)
        assert 'SMA_10' in df.columns
        assert 'EMA_21' in df.columns
        assert 'SMA_200' in df.columns
        assert not df['SMA_200'].isnull().all()

    def test_determine_trend(self, analyzer):
        # Uptrend
        trend = analyzer.determine_trend(150, 140, True)
        assert trend == TREND_UP
        
        # Downtrend
        trend = analyzer.determine_trend(130, 140, False)
        assert trend == TREND_DOWN
        
        # Neutral/Mixed
        trend = analyzer.determine_trend(140, 150, True)
        assert trend == TREND_NEUTRAL

    def test_classify_market_environment_bull(self, analyzer):
        # Grade A: All Up + Strong Breadth
        env = analyzer.classify_market_environment(
            TREND_UP, TREND_UP, TREND_UP, 
            leadership_strong=True, 
            breadth_metrics={'pct_above_50ma': 60.0} 
        )
        assert env == "A"

    def test_classify_market_environment_bear(self, analyzer):
        # Grade C: All Down
        env = analyzer.classify_market_environment(
            TREND_DOWN, TREND_DOWN, TREND_DOWN, 
            leadership_strong=False, 
            breadth_metrics={'pct_above_50ma': 20.0}
        )
        assert env == "C"

    def test_analyze_market_environment_integration(self, analyzer, mock_fetcher, mock_price_history):
        # Mock Data Fetcher Returns
        mock_fetcher.fetch_price_history.return_value = mock_price_history
        mock_fetcher.fetch_sp500_tickers.return_value = ['AAPL']
        mock_fetcher.fetch_bulk_history.return_value = pd.DataFrame() # Empty triggers fallback
        
        # Run analysis
        result = analyzer.analyze_market_environment()
        
        assert result['metrics']['environment'] in ['A', 'B', 'C', 'D', 'E']
        assert len(result['regime']) > 0
        assert result['metrics']['current_price'] > 0
        mock_fetcher.fetch_price_history.assert_called_once()
