import pytest
from src.modules.stock_screener import CANSLIMScreener

class TestStockScreener:
    
    @pytest.fixture
    def screener(self):
        return CANSLIMScreener()

    def test_calculate_fundamental_score(self, screener, mock_fundamental_data):
        score, _ = screener.calculate_fundamental_score(mock_fundamental_data)
        # Should be high score (3/3) based on mock data
        assert score == 3.0

    def test_calculate_technical_score(self, screener, mock_technical_data):
        score, _ = screener.calculate_technical_score(mock_technical_data)
        # High RS (90) + Uptrend + Above MAs -> Should be 3/3
        assert score == 3.0

    def test_screen_stock_grade_a(self, screener, mock_fundamental_data, mock_technical_data):
        result = screener.screen_stock(mock_fundamental_data, mock_technical_data)
        
        assert result.symbol == "TEST"
        assert result.grade == "A"
        assert result.total_score >= 5.0

    def test_screen_stock_failure(self, screener, mock_fundamental_data, mock_technical_data):
        # Ruin the technicals
        mock_technical_data.price_trend = "DOWN"
        mock_technical_data.rs_rating = 20.0
        
        # Ruin the fundamentals (since mock is perfect now)
        mock_fundamental_data.eps_growth = 5.0
        mock_fundamental_data.roe = 5.0
        
        result = screener.screen_stock(mock_fundamental_data, mock_technical_data)
        
        # Should be C or D grade
        assert result.grade in ["C", "D", "E"]
        assert result.total_score < 70
