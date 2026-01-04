"""
Module 4: Trade Journal
Records entry/exit trades, calculates P&L, and provides trade analysis
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
import logging

from src.utils.logger import setup_logger

logger = setup_logger("trade_journal", "trade_journal.log")


class TradeStatus(str, Enum):
    """Trade status enumeration"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"


class SetupGrade(str, Enum):
    """Setup quality grades"""
    A = "A"  # Excellent setup, multiple edges
    B = "B"  # Good setup, several edges
    C = "C"  # Fair setup, basic edges
    F = "F"  # Poor setup, avoid


class ExecutionGrade(str, Enum):
    """Execution quality grades"""
    A = "A"  # Excellent execution
    B = "B"  # Good execution
    C = "C"  # Fair execution
    F = "F"  # Poor execution


class Quadrant(str, Enum):
    """Trade outcome quadrant"""
    WIN_SETUP = "✓✓"        # Win + Good setup
    WIN_NO_SETUP = "✓✗"     # Win but poor setup
    LOSS_SETUP = "✗✓"       # Loss but good setup
    LOSS_SETUP_FAIL = "✗✗"  # Loss + Poor setup


@dataclass
class TradeEntry:
    """Trade entry information"""
    symbol: str
    entry_date: str                    # YYYY-MM-DD HH:MM:SS
    entry_price: float
    shares: int
    setup_grade: SetupGrade
    execution_grade: ExecutionGrade
    setup_description: str             # e.g., "Range breakout from base"
    edges_present: int                 # 1-10 edges
    initial_stop: float
    target_price: Optional[float] = None
    notes: str = ""


@dataclass
class TradeExit:
    """Trade exit information"""
    exit_date: str                     # YYYY-MM-DD HH:MM:SS
    exit_price: float
    shares_exited: int                 # May be partial exit
    exit_reason: str                   # "Profit target", "Stop loss", etc.
    notes: str = ""


@dataclass
class Trade:
    """Complete trade record"""
    trade_id: str                      # UUID or sequential ID
    symbol: str
    status: TradeStatus = TradeStatus.OPEN
    entry: Optional[TradeEntry] = None
    exits: List[TradeExit] = field(default_factory=list)
    
    # Calculated fields (updated on exit)
    pnl_dollars: float = 0.0
    pnl_percent: float = 0.0
    days_held: int = 0
    quadrant: Optional[Quadrant] = None
    max_profit: float = 0.0            # Peak profit during trade
    max_loss: float = 0.0              # Peak loss during trade
    created_at: str = ""
    closed_at: Optional[str] = None


class TradeJournal:
    """
    Trading journal for recording and analyzing trades
    
    Tracks:
    - Entry/exit prices and dates
    - Position size and risk
    - Setup and execution grades
    - P&L calculations
    - Trade quadrant classification
    - Historical performance
    """
    
    def __init__(self):
        """Initialize Trade Journal"""
        self.trades: Dict[str, Trade] = {}
        self.trade_counter = 0
        logger.info("Initialized TradeJournal")
    
    def create_trade_id(self) -> str:
        """
        Generate unique trade ID
        
        Returns:
            Trade ID (T0001, T0002, etc.)
        """
        self.trade_counter += 1
        return f"T{self.trade_counter:05d}"
    
    def record_entry(
        self,
        symbol: str,
        entry_price: float,
        shares: int,
        setup_grade: str,
        execution_grade: str,
        setup_description: str,
        edges_present: int,
        initial_stop: float,
        target_price: Optional[float] = None,
        notes: str = ""
    ) -> Trade:
        """
        Record trade entry
        
        Args:
            symbol: Stock symbol
            entry_price: Entry price
            shares: Number of shares
            setup_grade: Setup quality (A, B, C, F)
            execution_grade: Execution quality (A, B, C, F)
            setup_description: Description of setup
            edges_present: Number of edges (1-10)
            initial_stop: Stop loss price
            target_price: Optional profit target
            notes: Additional notes
        
        Returns:
            Trade object
        """
        trade_id = self.create_trade_id()
        
        entry = TradeEntry(
            symbol=symbol,
            entry_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            entry_price=entry_price,
            shares=shares,
            setup_grade=SetupGrade(setup_grade),
            execution_grade=ExecutionGrade(execution_grade),
            setup_description=setup_description,
            edges_present=edges_present,
            initial_stop=initial_stop,
            target_price=target_price,
            notes=notes
        )
        
        trade = Trade(
            trade_id=trade_id,
            symbol=symbol,
            entry=entry,
            status=TradeStatus.OPEN,
            created_at=entry.entry_date
        )
        
        self.trades[trade_id] = trade
        
        logger.info(
            f"Trade entry recorded: {trade_id} {symbol} "
            f"{shares}@${entry_price} | Stop: ${initial_stop}"
        )
        
        return trade
    
    def record_exit(
        self,
        trade_id: str,
        exit_price: float,
        shares_exited: int,
        exit_reason: str = "Manual exit",
        notes: str = ""
    ) -> Optional[Trade]:
        """
        Record trade exit (full or partial)
        
        Args:
            trade_id: Trade ID to exit
            exit_price: Exit price
            shares_exited: Shares being exited
            exit_reason: Reason for exit
            notes: Additional notes
        
        Returns:
            Updated Trade object or None if trade not found
        """
        if trade_id not in self.trades:
            logger.warning(f"Trade not found: {trade_id}")
            return None
        
        trade = self.trades[trade_id]
        
        if trade.entry is None:
            logger.warning(f"Trade has no entry: {trade_id}")
            return None
        
        # Record exit
        exit_record = TradeExit(
            exit_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            exit_price=exit_price,
            shares_exited=shares_exited,
            exit_reason=exit_reason,
            notes=notes
        )
        
        trade.exits.append(exit_record)
        
        # Calculate P&L for this exit
        self._calculate_pnl(trade)
        
        # Update status
        total_shares_exited = sum(exit.shares_exited for exit in trade.exits)
        if total_shares_exited >= trade.entry.shares:
            trade.status = TradeStatus.CLOSED
            trade.closed_at = exit_record.exit_date
        else:
            trade.status = TradeStatus.PARTIAL
        
        logger.info(
            f"Trade exit recorded: {trade_id} {shares_exited}@${exit_price} | "
            f"P&L: ${trade.pnl_dollars:.2f} ({trade.pnl_percent:.2f}%)"
        )
        
        return trade
    
    def _calculate_pnl(self, trade: Trade) -> None:
        """
        Calculate P&L for trade
        
        Args:
            trade: Trade object to calculate P&L for
        """
        if not trade.entry or not trade.exits:
            return
        
        entry_cost = trade.entry.entry_price * trade.entry.shares
        
        # Calculate realized P&L from exits
        total_exit_proceeds = 0
        total_shares_exited = 0
        
        for exit in trade.exits:
            total_exit_proceeds += exit.exit_price * exit.shares_exited
            total_shares_exited += exit.shares_exited
        
        # Calculate P&L
        trade.pnl_dollars = total_exit_proceeds - (
            trade.entry.entry_price * total_shares_exited
        )
        
        if total_shares_exited > 0:
            trade.pnl_percent = (trade.pnl_dollars / 
                                (trade.entry.entry_price * total_shares_exited)) * 100
        
        # Calculate days held
        if trade.closed_at:
            entry_dt = datetime.strptime(
                trade.entry.entry_date, "%Y-%m-%d %H:%M:%S"
            )
            exit_dt = datetime.strptime(
                trade.closed_at, "%Y-%m-%d %H:%M:%S"
            )
            trade.days_held = (exit_dt - entry_dt).days
        
        # Classify quadrant
        self._classify_quadrant(trade)
    
    def _classify_quadrant(self, trade: Trade) -> None:
        """
        Classify trade into quadrant
        
        ✓✓: Winner with good setup
        ✓✗: Winner with poor setup
        ✗✓: Loser with good setup (learned something)
        ✗✗: Loser with poor setup (should avoid)
        
        Args:
            trade: Trade to classify
        """
        if not trade.entry:
            return
        
        # Determine if win or loss
        is_winner = trade.pnl_dollars > 0
        
        # Determine if good setup
        is_good_setup = trade.entry.setup_grade in [SetupGrade.A, SetupGrade.B]
        
        if is_winner and is_good_setup:
            trade.quadrant = Quadrant.WIN_SETUP
        elif is_winner and not is_good_setup:
            trade.quadrant = Quadrant.WIN_NO_SETUP
        elif not is_winner and is_good_setup:
            trade.quadrant = Quadrant.LOSS_SETUP
        else:
            trade.quadrant = Quadrant.LOSS_SETUP_FAIL
    
    def get_trade(self, trade_id: str) -> Optional[Trade]:
        """Get trade by ID"""
        return self.trades.get(trade_id)
    
    def get_all_trades(self) -> List[Trade]:
        """Get all trades"""
        return list(self.trades.values())
    
    def get_closed_trades(self) -> List[Trade]:
        """Get only closed trades"""
        return [t for t in self.trades.values() 
                if t.status == TradeStatus.CLOSED]
    
    def get_open_trades(self) -> List[Trade]:
        """Get only open trades"""
        return [t for t in self.trades.values() 
                if t.status == TradeStatus.OPEN]
    
    def calculate_statistics(
        self,
        trades: Optional[List[Trade]] = None
    ) -> Dict:
        """
        Calculate trading statistics
        
        Args:
            trades: List of trades (default: all closed trades)
        
        Returns:
            Dictionary with trading statistics
        """
        if trades is None:
            trades = self.get_closed_trades()
        
        if not trades:
            logger.warning("No trades for statistics calculation")
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "profit_factor": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "expectancy": 0,
                "total_pnl": 0,
                "best_trade": 0,
                "worst_trade": 0
            }
        
        pnls = [t.pnl_dollars for t in trades]
        winning_trades = [t for t in trades if t.pnl_dollars > 0]
        losing_trades = [t for t in trades if t.pnl_dollars < 0]
        
        total_wins = sum(t.pnl_dollars for t in winning_trades)
        total_losses = abs(sum(t.pnl_dollars for t in losing_trades))
        
        win_rate = len(winning_trades) / len(trades) if trades else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        avg_win = total_wins / len(winning_trades) if winning_trades else 0
        avg_loss = -total_losses / len(losing_trades) if losing_trades else 0
        
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        return {
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate * 100,
            "profit_factor": profit_factor,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "expectancy": expectancy,
            "total_pnl": sum(pnls),
            "best_trade": max(pnls) if pnls else 0,
            "worst_trade": min(pnls) if pnls else 0,
            "avg_pnl": np.mean(pnls) if pnls else 0,
            "std_dev": np.std(pnls) if pnls else 0
        }
    
    def get_quadrant_analysis(
        self,
        trades: Optional[List[Trade]] = None
    ) -> Dict:
        """
        Analyze trades by quadrant
        
        Args:
            trades: List of trades (default: all closed trades)
        
        Returns:
            Dictionary with quadrant breakdown
        """
        if trades is None:
            trades = self.get_closed_trades()
        
        quadrants = {
            Quadrant.WIN_SETUP: [],
            Quadrant.WIN_NO_SETUP: [],
            Quadrant.LOSS_SETUP: [],
            Quadrant.LOSS_SETUP_FAIL: []
        }
        
        for trade in trades:
            if trade.quadrant:
                quadrants[trade.quadrant].append(trade)
        
        return {
            "win_good_setup": len(quadrants[Quadrant.WIN_SETUP]),
            "win_poor_setup": len(quadrants[Quadrant.WIN_NO_SETUP]),
            "loss_good_setup": len(quadrants[Quadrant.LOSS_SETUP]),
            "loss_poor_setup": len(quadrants[Quadrant.LOSS_SETUP_FAIL]),
            "trades_by_quadrant": {
                str(q): [asdict(t) for t in trades]
                for q, trades in quadrants.items()
            }
        }
    
    def export_to_csv(self, filepath: str) -> bool:
        """
        Export trades to CSV
        
        Args:
            filepath: Path to save CSV
        
        Returns:
            True if successful, False otherwise
        """
        try:
            records = []
            for trade in self.get_closed_trades():
                if trade.entry and trade.exits:
                    for exit in trade.exits:
                        records.append({
                            'trade_id': trade.trade_id,
                            'symbol': trade.symbol,
                            'entry_date': trade.entry.entry_date,
                            'entry_price': trade.entry.entry_price,
                            'shares': trade.entry.shares,
                            'setup_grade': trade.entry.setup_grade.value,
                            'execution_grade': trade.entry.execution_grade.value,
                            'edges_present': trade.entry.edges_present,
                            'initial_stop': trade.entry.initial_stop,
                            'target_price': trade.entry.target_price,
                            'exit_date': exit.exit_date,
                            'exit_price': exit.exit_price,
                            'shares_exited': exit.shares_exited,
                            'exit_reason': exit.exit_reason,
                            'pnl_dollars': trade.pnl_dollars,
                            'pnl_percent': trade.pnl_percent,
                            'days_held': trade.days_held,
                            'quadrant': str(trade.quadrant) if trade.quadrant else "",
                        })
            
            df = pd.DataFrame(records)
            df.to_csv(filepath, index=False)
            logger.info(f"Exported {len(records)} trades to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export trades: {e}")
            return False
    
    def get_trade_summary(self, trade: Trade) -> str:
        """
        Get formatted trade summary
        
        Args:
            trade: Trade object
        
        Returns:
            Formatted summary string
        """
        if not trade.entry:
            return "No entry recorded"
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                    TRADE SUMMARY - {trade.trade_id}                    
╚══════════════════════════════════════════════════════════════╝

SYMBOL: {trade.symbol}
STATUS: {trade.status.value}

ENTRY:
├─ Date/Time: {trade.entry.entry_date}
├─ Price: ${trade.entry.entry_price:.2f}
├─ Shares: {trade.entry.shares}
├─ Position Value: ${trade.entry.entry_price * trade.entry.shares:,.2f}
├─ Stop Loss: ${trade.entry.initial_stop:.2f}
└─ Target: {f"${trade.entry.target_price:.2f}" if trade.entry.target_price else "N/A"}

SETUP & EXECUTION:
├─ Setup Grade: {trade.entry.setup_grade.value}
├─ Execution Grade: {trade.entry.execution_grade.value}
├─ Edges Present: {trade.entry.edges_present}
├─ Setup Type: {trade.entry.setup_description}
└─ Notes: {trade.entry.notes or 'None'}

"""
        
        if trade.exits:
            summary += "EXIT(S):\n"
            for i, exit in enumerate(trade.exits, 1):
                summary += f"├─ Exit {i}:\n"
                summary += f"│  ├─ Date/Time: {exit.exit_date}\n"
                summary += f"│  ├─ Price: ${exit.exit_price:.2f}\n"
                summary += f"│  ├─ Shares: {exit.shares_exited}\n"
                summary += f"│  └─ Reason: {exit.exit_reason}\n"
            
            summary += f"\nP&L:\n"
            summary += f"├─ Dollars: ${trade.pnl_dollars:,.2f}\n"
            summary += f"├─ Percent: {trade.pnl_percent:.2f}%\n"
            summary += f"├─ Days Held: {trade.days_held}\n"
            summary += f"└─ Quadrant: {trade.quadrant}\n"
        
        summary += "\n╚══════════════════════════════════════════════════════════════╝\n"
        
        return summary


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*70)
    print("MODULE 4: TRADE JOURNAL - TEST")
    print("="*70)
    
    journal = TradeJournal()
    
    # Test Case 1: Winning trade with good setup
    print("\n\n📔 TEST CASE 1: Winning Trade (Good Setup)")
    print("-" * 70)
    
    trade1 = journal.record_entry(
        symbol="NVDA",
        entry_price=150.00,
        shares=100,
        setup_grade="A",
        execution_grade="A",
        setup_description="Range breakout from base with 4 edges",
        edges_present=4,
        initial_stop=145.00,
        target_price=165.00,
        notes="Strong earnings catalyst, RS at 90"
    )
    
    print(journal.get_trade_summary(trade1))
    
    # Record exit
    trade1 = journal.record_exit(
        trade_id=trade1.trade_id,
        exit_price=162.50,
        shares_exited=100,
        exit_reason="Took profit at target",
        notes="Clean exit"
    )
    
    print(journal.get_trade_summary(trade1))
    
    # Test Case 2: Losing trade with good setup (learning trade)
    print("\n\n📔 TEST CASE 2: Losing Trade (Good Setup - Learning Trade)")
    print("-" * 70)
    
    trade2 = journal.record_entry(
        symbol="TSLA",
        entry_price=200.00,
        shares=50,
        setup_grade="B",
        execution_grade="B",
        setup_description="Pullback to 21 EMA in uptrend",
        edges_present=3,
        initial_stop=195.00,
        target_price=215.00,
        notes="Good risk/reward 3:1"
    )
    
    # Hit stop loss
    trade2 = journal.record_exit(
        trade_id=trade2.trade_id,
        exit_price=194.50,
        shares_exited=50,
        exit_reason="Stop loss hit",
        notes="Gap down on market news"
    )
    
    print(journal.get_trade_summary(trade2))
    
    # Test Case 3: Winning trade with poor setup (lucky win)
    print("\n\n📔 TEST CASE 3: Winning Trade (Poor Setup - Lucky Win)")
    print("-" * 70)
    
    trade3 = journal.record_entry(
        symbol="AMD",
        entry_price=120.00,
        shares=75,
        setup_grade="C",
        execution_grade="C",
        setup_description="Breakout (below trend)",
        edges_present=1,
        initial_stop=117.00,
        target_price=128.00,
        notes="Weak setup, taken anyway"
    )
    
    trade3 = journal.record_exit(
        trade_id=trade3.trade_id,
        exit_price=130.00,
        shares_exited=75,
        exit_reason="Unexpected earnings beat",
        notes="Lucky - better to have avoided"
    )
    
    print(journal.get_trade_summary(trade3))
    
    # Statistics
    print("\n\n" + "="*70)
    print("TRADING STATISTICS")
    print("="*70)
    
    stats = journal.calculate_statistics()
    print(f"\nTotal Trades: {stats['total_trades']}")
    print(f"Winning Trades: {stats['winning_trades']}")
    print(f"Losing Trades: {stats['losing_trades']}")
    print(f"Win Rate: {stats['win_rate']:.1f}%")
    print(f"Profit Factor: {stats['profit_factor']:.2f}")
    print(f"Average Win: ${stats['avg_win']:.2f}")
    print(f"Average Loss: ${stats['avg_loss']:.2f}")
    print(f"Expectancy: ${stats['expectancy']:.2f}")
    print(f"Total P&L: ${stats['total_pnl']:.2f}")
    print(f"Best Trade: ${stats['best_trade']:.2f}")
    print(f"Worst Trade: ${stats['worst_trade']:.2f}")
    
    # Quadrant analysis
    print("\n\n" + "="*70)
    print("QUADRANT ANALYSIS")
    print("="*70)
    
    quadrants = journal.get_quadrant_analysis()
    print(f"\n✓✓ (Win + Good Setup): {quadrants['win_good_setup']} trades")
    print(f"✓✗ (Win + Poor Setup): {quadrants['win_poor_setup']} trades")
    print(f"✗✓ (Loss + Good Setup): {quadrants['loss_good_setup']} trades (learning)")
    print(f"✗✗ (Loss + Poor Setup): {quadrants['loss_poor_setup']} trades (avoid)")
    
    print("\n✅ Module 4: Trade Journal - Testing Complete!")
