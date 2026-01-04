import pytest
from src.modules.position_sizer import PositionSizer, PositionInput

class TestPositionSizer:
    
    @pytest.fixture
    def sizer(self):
        return PositionSizer(default_risk_percent=0.01, max_position_size=0.10)

    def test_calculate_risk_shares(self, sizer):
        # 100k account, 1% risk = $1000 risk
        # Entry 100, Stop 90 = $10 risk/share
        # Expected: 1000 / 10 = 100 shares
        shares = sizer.calculate_shares(100000, 100, 90, 1000)
        assert shares == 100

    def test_environment_sizing_impact(self, sizer):
        # Env A = Normal (Multiplier ~1.0 or higher)
        a_sizing = sizer.get_environment_sizing("A")
        # Env C = Reduced
        c_sizing = sizer.get_environment_sizing("C")
        
        assert a_sizing > c_sizing

    def test_edge_multiplier(self, sizer):
        m_low = sizer.get_edge_multiplier(1)
        m_high = sizer.get_edge_multiplier(5)
        
        assert m_low == 1.0
        assert m_high == 2.0

    def test_atr_stop_calculation(self, sizer):
        entry = 150
        atr = 5
        multiplier = 2.0
        
        expected_stop = 150 - (5 * 2) # 140
        stop = sizer.calculate_volatility_stop(entry, atr, multiplier)
        assert stop == 140.0

    def test_full_sizing_logic(self, sizer):
        inp = PositionInput(
            account_size=100000,
            entry_price=100,
            stop_loss_price=95,
            market_environment="A",
            num_edges=3,
            atr=2.5 # Risk is 5.0, ATR is 2.5 -> 2x ATR (Good)
        )
        
        result = sizer.size_position(inp)
        
        assert result.shares > 0
        assert result.atr_risk_multiple == 2.0
        
        # Validation
        valid, msg = sizer.validate_position(result)
        assert valid
