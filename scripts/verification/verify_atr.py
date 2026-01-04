import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modules.position_sizer import PositionSizer, PositionInput

def verify_atr_logic():
    print("🚀 Verifying ATR-based Position Sizing")
    
    sizer = PositionSizer()
    entry_price = 150.0
    atr = 5.0 # Average true range
    
    # 1. Test Helper Calculation
    stop_2x = sizer.calculate_volatility_stop(entry_price, atr, multiplier=2.0)
    print(f"\n1. Helper Check: Entry {entry_price}, ATR {atr}")
    print(f"   2x ATR Stop: {stop_2x} (Expected 140.0)")
    assert stop_2x == 140.0, "Helper calculation failed"
    
    # 2. Test Good Stop (2.0 ATR)
    print("\n2. Testing Valid Stop (2.0 ATR)")
    input_valid = PositionInput(
        account_size=100000,
        entry_price=entry_price,
        stop_loss_price=140.0, # 10 pt risk, exactly 2 ATR
        atr=atr
    )
    result_valid = sizer.size_position(input_valid)
    print(result_valid)
    is_valid, msg = sizer.validate_position(result_valid)
    print(f"   Validation: {msg}")
    assert result_valid.atr_risk_multiple == 2.0
    
    # 3. Test Tight Stop (0.5 ATR) - Should Warn
    print("\n3. Testing Tight Stop (0.5 ATR)")
    input_tight = PositionInput(
        account_size=100000,
        entry_price=entry_price,
        stop_loss_price=147.5, # 2.5 pt risk, 0.5 ATR
        atr=atr
    )
    result_tight = sizer.size_position(input_tight)
    print(result_tight)
    # Note: validate_position returns True but logs warning. We can't check log easily here, 
    # but we can check the calculated multiple.
    print(f"   ATR Multiple: {result_tight.atr_risk_multiple}")
    assert result_tight.atr_risk_multiple == 0.5
    
    # 4. Test Loose Stop (4.0 ATR)
    print("\n4. Testing Loose Stop (4.0 ATR)")
    input_loose = PositionInput(
        account_size=100000,
        entry_price=entry_price,
        stop_loss_price=130.0, # 20 pt risk, 4 ATR
        atr=atr
    )
    result_loose = sizer.size_position(input_loose)
    print(result_loose)
    print(f"   ATR Multiple: {result_loose.atr_risk_multiple}")
    assert result_loose.atr_risk_multiple == 4.0

if __name__ == "__main__":
    verify_atr_logic()
