"""
Module 3: Position Sizer
Calculates optimal position sizes based on risk management rules
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Tuple, Optional
import logging
from dataclasses import dataclass

from src.config.settings import (
    DEFAULT_RISK_PERCENT, MAX_POSITION_SIZE, MAX_POSITIONS
)
from src.config.constants import ENVIRONMENT_POSITION_SIZE
from src.utils.logger import setup_logger

logger = setup_logger("position_sizer", "position_sizer.log")


@dataclass
class PositionInput:
    """Input parameters for position sizing"""
    account_size: float                    # Total account value
    entry_price: float                     # Stock entry price
    stop_loss_price: float                 # Stop loss price
    market_environment: str = "A"          # Market environment (A-E)
    num_edges: int = 3                     # Number of edges present (1-10)
    target_price: Optional[float] = None   # Optional profit target
    atr: Optional[float] = None            # Average True Range (Volatility)
    
    @property
    def price_risk(self) -> float:
        """Risk per share in dollars"""
        return abs(self.entry_price - self.stop_loss_price)
    
    @property
    def risk_percent(self) -> float:
        """Risk as percentage of entry price"""
        if self.entry_price == 0:
            return 0
        return (self.price_risk / self.entry_price) * 100


@dataclass
class PositionOutput:
    """Output from position sizing calculation"""
    shares: int                            # Number of shares to buy
    position_size: float                   # Position size in dollars
    portfolio_percent: float               # Position as % of portfolio
    reward_to_risk: float                  # Reward/risk ratio
    max_loss: float                        # Max loss in dollars
    recommended_target: Optional[float]    # Recommended profit target
    edge_multiplier: float                 # Edge multiplier (1.0-2.0)
    environment_sizing: float              # Environment-based sizing %
    atr_risk_multiple: Optional[float] = None  # Risk expressed as multiples of ATR
    
    def __str__(self) -> str:
        """String representation"""
        atr_info = f"\n├─ ATR Risk Multiple: {self.atr_risk_multiple:.1f}x" if self.atr_risk_multiple else ""
        return f"""
Position Sizing Recommendation:
├─ Shares to Buy: {self.shares} shares
├─ Position Size: ${self.position_size:,.2f}
├─ Portfolio %: {self.portfolio_percent:.2f}%
├─ Risk Amount: ${self.max_loss:,.2f}
├─ Edge Multiplier: {self.edge_multiplier:.2f}x
├─ Environment Sizing: {self.environment_sizing:.1%}
├─ Reward/Risk Ratio: {self.reward_to_risk:.2f}:1{atr_info}
"""


class PositionSizer:
    """
    Calculates optimal position sizes based on:
    - Account size and risk tolerance
    - Market environment (A-E grading)
    - Number of edges present
    - Risk/reward ratio
    - Portfolio constraints
    """
    
    def __init__(
        self,
        default_risk_percent: float = DEFAULT_RISK_PERCENT,
        max_position_size: float = MAX_POSITION_SIZE,
        max_positions: int = MAX_POSITIONS
    ):
        """
        Initialize Position Sizer
        
        Args:
            default_risk_percent: Default risk per trade (0.01 = 1%)
            max_position_size: Max position as % of portfolio (0.10 = 10%)
            max_positions: Max concurrent positions
        """
        self.default_risk_percent = default_risk_percent
        self.max_position_size = max_position_size
        self.max_positions = max_positions
        
        logger.info(
            f"Initialized PositionSizer: "
            f"risk={default_risk_percent*100}%, "
            f"max_size={max_position_size*100}%, "
            f"max_positions={max_positions}"
        )
    
    def get_environment_sizing(self, environment: str) -> float:
        """
        Get position sizing multiplier based on market environment
        
        Args:
            environment: Market environment (A, B, C, D, E)
        
        Returns:
            Sizing multiplier (0.02 to 0.08)
        """
        return ENVIRONMENT_POSITION_SIZE.get(environment, 0.05)
    
    def get_edge_multiplier(self, num_edges: int) -> float:
        """
        Get multiplier based on number of edges
        
        More edges = higher confidence = larger position
        
        Args:
            num_edges: Number of edges present (1-10)
        
        Returns:
            Edge multiplier (1.0 to 2.0)
        """
        # Minimum 1.0x at 1 edge, maximum 2.0x at 5+ edges
        if num_edges < 1:
            return 1.0
        elif num_edges >= 5:
            return 2.0
        else:
            # Linear interpolation: 1.0 + (0.25 * edges)
            return 1.0 + (0.25 * (num_edges - 1))
    
    def calculate_reward_to_risk(
        self,
        entry_price: float,
        stop_loss: float,
        target_price: Optional[float] = None
    ) -> Tuple[float, Optional[float]]:
        """
        Calculate reward to risk ratio
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            target_price: Optional target price
        
        Returns:
            Tuple of (ratio, adjusted_target) or (ratio, None)
        """
        risk = abs(entry_price - stop_loss)
        
        if risk == 0:
            return 1.0, None
        
        # If target provided, use it
        if target_price:
            reward = abs(target_price - entry_price)
            ratio = reward / risk
            return ratio, target_price
        
        # Otherwise, recommend 2:1 reward/risk minimum
        recommended_reward = risk * 2
        recommended_target = entry_price + recommended_reward
        
        return 2.0, recommended_target
    
    def calculate_shares(
        self,
        account_size: float,
        entry_price: float,
        stop_loss: float,
        risk_amount: float
    ) -> int:
        """
        Calculate number of shares based on risk
        
        Formula: Shares = Risk Amount / Price Risk per Share
        
        Args:
            account_size: Total account value
            entry_price: Stock entry price
            stop_loss: Stop loss price
            risk_amount: Maximum loss in dollars
        
        Returns:
            Number of shares (whole shares only)
        """
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            logger.warning("Price risk is zero, cannot calculate shares")
            return 0
        
        shares = risk_amount / price_risk
        return int(shares)  # Round down to whole shares
    
    def calculate_volatility_stop(
        self,
        entry_price: float,
        atr: float,
        multiplier: float = 2.0
    ) -> float:
        """
        Calculate suggested stop loss based on ATR
        
        Args:
            entry_price: Entry price
            atr: Average True Range
            multiplier: ATR multiplier (default 2.0)
            
        Returns:
            Suggested stop loss price
        """
        return entry_price - (atr * multiplier)

    def size_position(self, position_input: PositionInput) -> PositionOutput:
        """
        Calculate optimal position size
        
        Args:
            position_input: PositionInput object with all parameters
        
        Returns:
            PositionOutput with sizing recommendations
        """
        logger.info(
            f"Sizing position: ${position_input.entry_price} "
            f"Environment={position_input.market_environment}, "
            f"Edges={position_input.num_edges}"
        )
        
        # 1. Get environment-based sizing
        environment_sizing = self.get_environment_sizing(
            position_input.market_environment
        )
        
        # 2. Get edge multiplier
        edge_multiplier = self.get_edge_multiplier(position_input.num_edges)
        
        # 3. Calculate effective position size
        effective_size = (
            self.default_risk_percent * 
            (environment_sizing / 0.05) * 
            edge_multiplier
        )
        
        # 4. Cap at maximum position size
        position_percent = min(effective_size, self.max_position_size)
        
        # 5. Calculate risk amount in dollars
        risk_amount = position_input.account_size * position_percent
        
        # 6. Calculate shares
        shares = self.calculate_shares(
            position_input.account_size,
            position_input.entry_price,
            position_input.stop_loss_price,
            risk_amount
        )
        
        # 7. Calculate actual position size
        position_size = shares * position_input.entry_price
        
        # 8. Calculate reward to risk
        reward_to_risk, recommended_target = self.calculate_reward_to_risk(
            position_input.entry_price,
            position_input.stop_loss_price,
            position_input.target_price
        )
        
        # 9. Calculate ATR Risk Multiple (if ATR provided)
        atr_risk_multiple = None
        if position_input.atr and position_input.atr > 0:
            atr_risk_multiple = position_input.price_risk / position_input.atr
        
        # 10. Build output
        result = PositionOutput(
            shares=shares,
            position_size=position_size,
            portfolio_percent=position_percent * 100,
            reward_to_risk=reward_to_risk,
            max_loss=risk_amount,
            recommended_target=recommended_target,
            edge_multiplier=edge_multiplier,
            environment_sizing=environment_sizing,
            atr_risk_multiple=atr_risk_multiple
        )
        
        logger.info(f"Position sized: {shares} shares, ${position_size:,.2f}")
        
        return result
    
    def validate_position(
        self,
        position_output: PositionOutput,
        current_positions: int = 0
    ) -> Tuple[bool, str]:
        """
        Validate position against constraints
        
        Args:
            position_output: PositionOutput from sizing
            current_positions: Current number of open positions
        
        Returns:
            Tuple of (is_valid, message)
        """
        # Check position count
        if current_positions >= self.max_positions:
            return False, (
                f"Max positions ({self.max_positions}) already open. "
                f"Close existing positions first."
            )
        
        # Check position size
        if position_output.portfolio_percent > self.max_position_size * 100:
            return False, (
                f"Position size {position_output.portfolio_percent:.2f}% "
                f"exceeds max {self.max_position_size*100:.2f}%"
            )
        
        # Check shares
        if position_output.shares == 0:
            return False, "Position too small - results in 0 shares"

        # Check ATR limits
        if position_output.atr_risk_multiple:
            if position_output.atr_risk_multiple < 1.0:
                 logger.warning(f"Stop loss is too tight ({position_output.atr_risk_multiple:.1f} ATR). Recommended > 1.0 ATR")
            elif position_output.atr_risk_multiple > 3.0:
                 logger.warning(f"Stop loss is too wide ({position_output.atr_risk_multiple:.1f} ATR). Recommended < 3.0 ATR")
        
        return True, "Position validated successfully"
    
    def get_position_summary(
        self,
        position_input: PositionInput,
        position_output: PositionOutput
    ) -> Dict:
        """
        Get comprehensive position summary
        
        Args:
            position_input: Input parameters
            position_output: Output sizing
        
        Returns:
            Dictionary with full position details
        """
        return {
            "input": {
                "account_size": position_input.account_size,
                "entry_price": position_input.entry_price,
                "stop_loss_price": position_input.stop_loss_price,
                "market_environment": position_input.market_environment,
                "num_edges": position_input.num_edges,
                "price_risk": position_input.price_risk,
                "risk_percent": position_input.risk_percent
            },
            "output": {
                "shares": position_output.shares,
                "position_size": position_output.position_size,
                "portfolio_percent": position_output.portfolio_percent,
                "max_loss": position_output.max_loss,
                "reward_to_risk": position_output.reward_to_risk,
                "recommended_target": position_output.recommended_target,
                "edge_multiplier": position_output.edge_multiplier,
                "environment_sizing": position_output.environment_sizing
            }
        }


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*70)
    print("MODULE 3: POSITION SIZER - TEST")
    print("="*70)
    
    # Initialize sizer
    sizer = PositionSizer(
        default_risk_percent=0.01,  # 1% risk per trade
        max_position_size=0.10,     # 10% max position
        max_positions=5             # 5 max positions
    )
    
    # Test Case 1: Strong environment, multiple edges
    print("\n\n📊 TEST CASE 1: Environment A (Strong), 4 Edges")
    print("-" * 70)
    
    input1 = PositionInput(
        account_size=100000,
        entry_price=150.00,
        stop_loss_price=145.00,
        market_environment="A",
        num_edges=4,
        target_price=165.00
    )
    
    output1 = sizer.size_position(input1)
    print(output1)
    print(f"Summary: {sizer.get_position_summary(input1, output1)}")
    
    is_valid, msg = sizer.validate_position(output1, current_positions=0)
    print(f"Validation: {msg} ✓" if is_valid else f"Validation: {msg} ✗")
    
    # Test Case 2: Weak environment, 2 edges
    print("\n\n📊 TEST CASE 2: Environment C (Weak), 2 Edges")
    print("-" * 70)
    
    input2 = PositionInput(
        account_size=100000,
        entry_price=75.00,
        stop_loss_price=72.00,
        market_environment="C",
        num_edges=2
    )
    
    output2 = sizer.size_position(input2)
    print(output2)
    print(f"Summary: {sizer.get_position_summary(input2, output2)}")
    
    # Test Case 3: Medium environment, 3 edges
    print("\n\n📊 TEST CASE 3: Environment B (Medium), 3 Edges")
    print("-" * 70)
    
    input3 = PositionInput(
        account_size=100000,
        entry_price=200.00,
        stop_loss_price=195.00,
        market_environment="B",
        num_edges=3,
        target_price=220.00
    )
    
    output3 = sizer.size_position(input3)
    print(output3)
    print(f"Summary: {sizer.get_position_summary(input3, output3)}")
    
    # Comparison
    print("\n\n" + "="*70)
    print("COMPARISON: Different Environments, Same Stock")
    print("="*70)
    print(f"{'Environment':<15} {'Shares':<10} {'Position Size':<18} {'Max Loss':<15}")
    print("-" * 70)
    print(f"{'A (Strong)':<15} {output1.shares:<10} ${output1.position_size:>15,.2f} ${output1.max_loss:>13,.2f}")
    print(f"{'B (Medium)':<15} {output3.shares:<10} ${output3.position_size:>15,.2f} ${output3.max_loss:>13,.2f}")
    print(f"{'C (Weak)':<15} {output2.shares:<10} ${output2.position_size:>15,.2f} ${output2.max_loss:>13,.2f}")
    
    print("\n✅ Module 3: Position Sizer - Testing Complete!")
