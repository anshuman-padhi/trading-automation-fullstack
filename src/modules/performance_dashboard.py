"""
Module 5: Performance Dashboard
Aggregates trading statistics, metrics, and performance analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("performance_dashboard")


@dataclass
class MonthlyMetrics:
    """Monthly performance metrics"""
    month: str                         # YYYY-MM
    trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    net_profit: float = 0.0
    profit_factor: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    expectancy: float = 0.0
    return_pct: float = 0.0


@dataclass
class YearlyMetrics:
    """Yearly performance metrics"""
    year: int
    total_trades: int = 0
    total_wins: int = 0
    total_losses: int = 0
    yearly_win_rate: float = 0.0
    yearly_profit: float = 0.0
    monthly_breakdown: Dict[str, MonthlyMetrics] = field(default_factory=dict)
    best_month: Optional[str] = None
    worst_month: Optional[str] = None
    best_trade: float = 0.0
    worst_trade: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0


@dataclass
class TradeMetrics:
    """Individual trade metrics for aggregation"""
    trade_id: str
    symbol: str
    entry_date: str
    exit_date: Optional[str]
    pnl_dollars: float
    pnl_percent: float
    days_held: int
    setup_grade: str
    execution_grade: str
    quadrant: str


class PerformanceDashboard:
    """
    Performance Dashboard for trading analytics
    
    Aggregates:
    - Win rate, profit factor, expectancy
    - Best/worst trades
    - Monthly & yearly performance
    - Equity curve
    - Drawdown analysis
    - Setup & execution grades
    - Trade duration analysis
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize Performance Dashboard
        
        Args:
            initial_capital: Starting account balance
        """
        self.initial_capital = initial_capital
        self.trades: List[TradeMetrics] = []
        logger.info(f"Initialized PerformanceDashboard (Capital: ${initial_capital:,.2f})")
    
    def add_trade(self, trade: TradeMetrics) -> None:
        """Add trade for analysis"""
        self.trades.append(trade)
    
    def add_trades(self, trades: List[TradeMetrics]) -> None:
        """Add multiple trades"""
        self.trades.extend(trades)
    
    def calculate_summary_stats(self) -> Dict:
        """
        Calculate comprehensive summary statistics
        
        Returns:
            Dictionary with all summary metrics
        """
        if not self.trades:
            logger.warning("No trades to analyze")
            return self._empty_stats()
        
        closed_trades = [t for t in self.trades if t.exit_date]
        
        if not closed_trades:
            return self._empty_stats()
        
        pnls = [t.pnl_dollars for t in closed_trades]
        wins = [t for t in closed_trades if t.pnl_dollars > 0]
        losses = [t for t in closed_trades if t.pnl_dollars < 0]
        
        total_profit = sum(t.pnl_dollars for t in wins)
        total_loss = abs(sum(t.pnl_dollars for t in losses))
        
        win_rate = len(wins) / len(closed_trades) if closed_trades else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        avg_win = total_profit / len(wins) if wins else 0
        avg_loss = -total_loss / len(losses) if losses else 0
        
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        # Equity curve
        equity_curve = self._calculate_equity_curve(closed_trades)
        max_equity = max(equity_curve) if equity_curve else self.initial_capital
        min_equity = min(equity_curve) if equity_curve else self.initial_capital
        
        # Drawdown
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        max_drawdown_pct = (max_drawdown / self.initial_capital * 100) if self.initial_capital > 0 else 0
        
        return {
            "total_trades": len(closed_trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": win_rate * 100,
            "profit_factor": profit_factor,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "expectancy": expectancy,
            "total_pnl": sum(pnls),
            "total_pnl_pct": (sum(pnls) / self.initial_capital * 100) if self.initial_capital > 0 else 0,
            "best_trade": max(pnls) if pnls else 0,
            "worst_trade": min(pnls) if pnls else 0,
            "largest_win": max((t.pnl_dollars for t in wins), default=0),
            "largest_loss": min((t.pnl_dollars for t in losses), default=0),
            "gross_profit": total_profit,
            "gross_loss": total_loss,
            "avg_pnl": np.mean(pnls) if pnls else 0,
            "std_dev": np.std(pnls) if pnls else 0,
            "sharpe_ratio": self._calculate_sharpe_ratio(pnls),
            "max_equity": max_equity,
            "min_equity": min_equity,
            "max_drawdown": max_drawdown,
            "max_drawdown_pct": max_drawdown_pct,
            "consecutive_wins": self._max_consecutive_wins(closed_trades),
            "consecutive_losses": self._max_consecutive_losses(closed_trades),
            "avg_days_held": np.mean([t.days_held for t in closed_trades]) if closed_trades else 0,
            "avg_days_win": np.mean([t.days_held for t in wins]) if wins else 0,
            "avg_days_loss": np.mean([t.days_held for t in losses]) if losses else 0,
        }
    
    def calculate_monthly_stats(self) -> Dict[str, MonthlyMetrics]:
        """
        Calculate monthly performance breakdown
        
        Returns:
            Dictionary of monthly metrics by month (YYYY-MM)
        """
        monthly_trades: Dict[str, List[TradeMetrics]] = defaultdict(list)
        
        # Group trades by month
        for trade in self.trades:
            if trade.exit_date:
                month = trade.exit_date[:7]  # YYYY-MM
                monthly_trades[month].append(trade)
        
        monthly_metrics = {}
        
        for month in sorted(monthly_trades.keys()):
            trades = monthly_trades[month]
            pnls = [t.pnl_dollars for t in trades]
            wins = [t for t in trades if t.pnl_dollars > 0]
            losses = [t for t in trades if t.pnl_dollars < 0]
            
            gross_profit = sum(t.pnl_dollars for t in wins)
            gross_loss = abs(sum(t.pnl_dollars for t in losses))
            net_profit = sum(pnls)
            
            win_rate = len(wins) / len(trades) if trades else 0
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            avg_win = gross_profit / len(wins) if wins else 0
            avg_loss = -gross_loss / len(losses) if losses else 0
            
            expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
            
            monthly_metrics[month] = MonthlyMetrics(
                month=month,
                trades=len(trades),
                wins=len(wins),
                losses=len(losses),
                win_rate=win_rate * 100,
                gross_profit=gross_profit,
                gross_loss=gross_loss,
                net_profit=net_profit,
                profit_factor=profit_factor,
                largest_win=max((t.pnl_dollars for t in wins), default=0),
                largest_loss=min((t.pnl_dollars for t in losses), default=0),
                avg_win=avg_win,
                avg_loss=avg_loss,
                expectancy=expectancy,
                return_pct=(net_profit / self.initial_capital * 100) if self.initial_capital > 0 else 0
            )
        
        return monthly_metrics
    
    def calculate_yearly_stats(self) -> Dict[int, YearlyMetrics]:
        """
        Calculate yearly performance breakdown
        
        Returns:
            Dictionary of yearly metrics by year
        """
        yearly_trades: Dict[int, List[TradeMetrics]] = defaultdict(list)
        
        # Group trades by year
        for trade in self.trades:
            if trade.exit_date:
                year = int(trade.exit_date[:4])
                yearly_trades[year].append(trade)
        
        yearly_metrics = {}
        
        for year in sorted(yearly_trades.keys()):
            trades = yearly_trades[year]
            wins = [t for t in trades if t.pnl_dollars > 0]
            losses = [t for t in trades if t.pnl_dollars < 0]
            
            year_metrics = YearlyMetrics(
                year=year,
                total_trades=len(trades),
                total_wins=len(wins),
                total_losses=len(losses),
                yearly_win_rate=(len(wins) / len(trades) * 100) if trades else 0,
                yearly_profit=sum(t.pnl_dollars for t in trades),
                best_trade=max((t.pnl_dollars for t in trades), default=0),
                worst_trade=min((t.pnl_dollars for t in trades), default=0),
                consecutive_wins=self._max_consecutive_wins(trades),
                consecutive_losses=self._max_consecutive_losses(trades),
            )
            
            # Get monthly breakdown for this year
            monthly_stats = self.calculate_monthly_stats()
            year_metrics.monthly_breakdown = {
                m: stats for m, stats in monthly_stats.items()
                if m.startswith(str(year))
            }
            
            # Find best/worst months
            if year_metrics.monthly_breakdown:
                best_month = max(
                    year_metrics.monthly_breakdown.items(),
                    key=lambda x: x[1].net_profit
                )[0]
                worst_month = min(
                    year_metrics.monthly_breakdown.items(),
                    key=lambda x: x[1].net_profit
                )[0]
                year_metrics.best_month = best_month
                year_metrics.worst_month = worst_month
            
            yearly_metrics[year] = year_metrics
        
        return yearly_metrics
    
    def analyze_by_setup_grade(self) -> Dict[str, Dict]:
        """
        Analyze performance by setup grade (A, B, C, F)
        
        Returns:
            Dictionary with stats grouped by setup grade
        """
        by_grade: Dict[str, List[TradeMetrics]] = defaultdict(list)
        
        for trade in self.trades:
            if trade.exit_date:
                by_grade[trade.setup_grade].append(trade)
        
        results = {}
        
        for grade in sorted(by_grade.keys()):
            trades = by_grade[grade]
            pnls = [t.pnl_dollars for t in trades]
            wins = [t for t in trades if t.pnl_dollars > 0]
            
            results[grade] = {
                "trades": len(trades),
                "wins": len(wins),
                "losses": len(trades) - len(wins),
                "win_rate": (len(wins) / len(trades) * 100) if trades else 0,
                "total_pnl": sum(pnls),
                "avg_pnl": np.mean(pnls) if pnls else 0,
                "best_trade": max(pnls) if pnls else 0,
                "worst_trade": min(pnls) if pnls else 0,
                "profit_factor": self._calculate_profit_factor(trades),
            }
        
        return results
    
    def analyze_by_symbol(self) -> Dict[str, Dict]:
        """
        Analyze performance by stock symbol
        
        Returns:
            Dictionary with stats grouped by symbol
        """
        by_symbol: Dict[str, List[TradeMetrics]] = defaultdict(list)
        
        for trade in self.trades:
            if trade.exit_date:
                by_symbol[trade.symbol].append(trade)
        
        results = {}
        
        for symbol in sorted(by_symbol.keys()):
            trades = by_symbol[symbol]
            pnls = [t.pnl_dollars for t in trades]
            wins = [t for t in trades if t.pnl_dollars > 0]
            
            results[symbol] = {
                "trades": len(trades),
                "wins": len(wins),
                "losses": len(trades) - len(wins),
                "win_rate": (len(wins) / len(trades) * 100) if trades else 0,
                "total_pnl": sum(pnls),
                "avg_pnl": np.mean(pnls) if pnls else 0,
                "best_trade": max(pnls) if pnls else 0,
                "worst_trade": min(pnls) if pnls else 0,
            }
        
        return results
    
    def _calculate_equity_curve(self, trades: List[TradeMetrics]) -> List[float]:
        """Calculate running equity curve"""
        equity = [self.initial_capital]
        current = self.initial_capital
        
        for trade in sorted(trades, key=lambda t: t.exit_date):
            current += trade.pnl_dollars
            equity.append(current)
        
        return equity
    
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """Calculate maximum drawdown in dollars"""
        if not equity_curve:
            return 0
        
        max_drawdown = 0
        peak = equity_curve[0]
        
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            drawdown = peak - equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def _calculate_sharpe_ratio(self, pnls: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio (annualized)"""
        if not pnls or len(pnls) < 2:
            return 0
        
        returns = np.array(pnls)
        excess_return = np.mean(returns) - (risk_free_rate / 252)  # Daily risk-free rate
        std_dev = np.std(returns)
        
        if std_dev == 0:
            return 0
        
        # Annualize (252 trading days)
        sharpe = (excess_return / std_dev) * np.sqrt(252)
        
        return sharpe
    
    def _max_consecutive_wins(self, trades: List[TradeMetrics]) -> int:
        """Calculate maximum consecutive wins"""
        if not trades:
            return 0
        
        max_wins = 0
        current_wins = 0
        
        for trade in sorted(trades, key=lambda t: t.exit_date):
            if trade.pnl_dollars > 0:
                current_wins += 1
                max_wins = max(max_wins, current_wins)
            else:
                current_wins = 0
        
        return max_wins
    
    def _max_consecutive_losses(self, trades: List[TradeMetrics]) -> int:
        """Calculate maximum consecutive losses"""
        if not trades:
            return 0
        
        max_losses = 0
        current_losses = 0
        
        for trade in sorted(trades, key=lambda t: t.exit_date):
            if trade.pnl_dollars < 0:
                current_losses += 1
                max_losses = max(max_losses, current_losses)
            else:
                current_losses = 0
        
        return max_losses
    
    def _calculate_profit_factor(self, trades: List[TradeMetrics]) -> float:
        """Calculate profit factor for a trade group"""
        wins = [t for t in trades if t.pnl_dollars > 0]
        losses = [t for t in trades if t.pnl_dollars < 0]
        
        gross_profit = sum(t.pnl_dollars for t in wins)
        gross_loss = abs(sum(t.pnl_dollars for t in losses))
        
        return gross_profit / gross_loss if gross_loss > 0 else 0
    
    def _empty_stats(self) -> Dict:
        """Return empty statistics dictionary"""
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
            "total_pnl_pct": 0,
            "best_trade": 0,
            "worst_trade": 0,
            "largest_win": 0,
            "largest_loss": 0,
            "gross_profit": 0,
            "gross_loss": 0,
            "avg_pnl": 0,
            "std_dev": 0,
            "sharpe_ratio": 0,
            "max_equity": 0,
            "min_equity": 0,
            "max_drawdown": 0,
            "max_drawdown_pct": 0,
            "consecutive_wins": 0,
            "consecutive_losses": 0,
            "avg_days_held": 0,
            "avg_days_win": 0,
            "avg_days_loss": 0,
        }
    
    def print_summary_report(self) -> None:
        """Print formatted summary report"""
        stats = self.calculate_summary_stats()
        
        print("\n" + "="*70)
        print("PERFORMANCE DASHBOARD - SUMMARY REPORT")
        print("="*70)
        
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"├─ Total Trades: {stats['total_trades']}")
        print(f"├─ Winning Trades: {stats['winning_trades']}")
        print(f"├─ Losing Trades: {stats['losing_trades']}")
        print(f"├─ Win Rate: {stats['win_rate']:.1f}%")
        print(f"├─ Profit Factor: {stats['profit_factor']:.2f}")
        
        print(f"\n💰 P&L METRICS:")
        print(f"├─ Total P&L: ${stats['total_pnl']:,.2f}")
        print(f"├─ Total P&L %: {stats['total_pnl_pct']:.2f}%")
        print(f"├─ Gross Profit: ${stats['gross_profit']:,.2f}")
        print(f"├─ Gross Loss: ${stats['gross_loss']:,.2f}")
        print(f"├─ Best Trade: ${stats['best_trade']:,.2f}")
        print(f"└─ Worst Trade: ${stats['worst_trade']:,.2f}")
        
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"├─ Average Win: ${stats['avg_win']:,.2f}")
        print(f"├─ Average Loss: ${stats['avg_loss']:,.2f}")
        print(f"├─ Expectancy: ${stats['expectancy']:.2f}")
        print(f"├─ Avg P&L per Trade: ${stats['avg_pnl']:,.2f}")
        print(f"├─ Std Deviation: ${stats['std_dev']:,.2f}")
        print(f"└─ Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
        
        print(f"\n📉 DRAWDOWN & EQUITY:")
        print(f"├─ Max Drawdown: ${stats['max_drawdown']:,.2f}")
        print(f"├─ Max Drawdown %: {stats['max_drawdown_pct']:.2f}%")
        print(f"├─ Max Equity: ${stats['max_equity']:,.2f}")
        print(f"└─ Min Equity: ${stats['min_equity']:,.2f}")
        
        print(f"\n⏱️  DURATION & STREAK:")
        print(f"├─ Avg Days Held: {stats['avg_days_held']:.1f}")
        print(f"├─ Avg Days (Wins): {stats['avg_days_win']:.1f}")
        print(f"├─ Avg Days (Losses): {stats['avg_days_loss']:.1f}")
        print(f"├─ Max Consecutive Wins: {stats['consecutive_wins']}")
        print(f"└─ Max Consecutive Losses: {stats['consecutive_losses']}")
        
        print("\n" + "="*70)
    
    def print_monthly_report(self) -> None:
        """Print formatted monthly breakdown"""
        monthly = self.calculate_monthly_stats()
        
        if not monthly:
            print("No monthly data available")
            return
        
        print("\n" + "="*70)
        print("PERFORMANCE DASHBOARD - MONTHLY BREAKDOWN")
        print("="*70)
        
        for month in sorted(monthly.keys()):
            m = monthly[month]
            print(f"\n{month}:")
            print(f"├─ Trades: {m.trades} (W: {m.wins}, L: {m.losses})")
            print(f"├─ Win Rate: {m.win_rate:.1f}%")
            print(f"├─ Profit Factor: {m.profit_factor:.2f}")
            print(f"├─ Net P&L: ${m.net_profit:,.2f}")
            print(f"├─ Return: {m.return_pct:.2f}%")
            print(f"├─ Avg Win: ${m.avg_win:,.2f}")
            print(f"├─ Avg Loss: ${m.avg_loss:,.2f}")
            print(f"└─ Expectancy: ${m.expectancy:.2f}")
        
        print("\n" + "="*70)


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*70)
    print("MODULE 5: PERFORMANCE DASHBOARD - TEST")
    print("="*70)
    
    # Initialize dashboard
    dashboard = PerformanceDashboard(initial_capital=100000.0)
    
    # Create sample trades
    trades = [
        TradeMetrics("T00001", "NVDA", "2026-01-01 10:00:00", "2026-01-05 15:30:00", 1250.0, 8.33, 4, "A", "A", "✓✓"),
        TradeMetrics("T00002", "TSLA", "2026-01-02 10:00:00", "2026-01-03 09:30:00", -275.0, -2.75, 1, "B", "B", "✗✓"),
        TradeMetrics("T00003", "AMD", "2026-01-06 10:00:00", "2026-01-08 14:00:00", 1500.0, 12.50, 2, "C", "C", "✓✗"),
        TradeMetrics("T00004", "AAPL", "2026-01-09 10:00:00", "2026-01-12 11:00:00", 520.0, 4.16, 3, "B", "A", "✓✓"),
        TradeMetrics("T00005", "MSFT", "2026-01-13 10:00:00", "2026-01-14 10:30:00", -380.0, -3.04, 1, "C", "F", "✗✗"),
        TradeMetrics("T00006", "GOOGL", "2026-01-15 10:00:00", "2026-01-18 15:00:00", 890.0, 5.93, 3, "A", "B", "✓✓"),
        TradeMetrics("T00007", "META", "2026-02-01 10:00:00", "2026-02-05 12:00:00", 1100.0, 7.33, 4, "A", "A", "✓✓"),
        TradeMetrics("T00008", "NFLX", "2026-02-06 10:00:00", "2026-02-07 14:30:00", -420.0, -3.36, 1, "B", "C", "✗✓"),
        TradeMetrics("T00009", "INTC", "2026-02-08 10:00:00", "2026-02-10 15:00:00", 650.0, 5.20, 2, "B", "B", "✓✓"),
    ]
    
    # Add trades to dashboard
    dashboard.add_trades(trades)
    
    # Print summary report
    dashboard.print_summary_report()
    
    # Print monthly breakdown
    dashboard.print_monthly_report()
    
    # Analysis by setup grade
    print("\n" + "="*70)
    print("PERFORMANCE DASHBOARD - BY SETUP GRADE")
    print("="*70)
    
    by_grade = dashboard.analyze_by_setup_grade()
    for grade in sorted(by_grade.keys()):
        stats = by_grade[grade]
        print(f"\nGrade {grade}:")
        print(f"├─ Trades: {stats['trades']}")
        print(f"├─ Wins: {stats['wins']}")
        print(f"├─ Win Rate: {stats['win_rate']:.1f}%")
        print(f"├─ Total P&L: ${stats['total_pnl']:,.2f}")
        print(f"├─ Avg P&L: ${stats['avg_pnl']:,.2f}")
        print(f"└─ Profit Factor: {stats['profit_factor']:.2f}")
    
    # Analysis by symbol
    print("\n" + "="*70)
    print("PERFORMANCE DASHBOARD - BY SYMBOL")
    print("="*70)
    
    by_symbol = dashboard.analyze_by_symbol()
    for symbol in sorted(by_symbol.keys()):
        stats = by_symbol[symbol]
        print(f"\n{symbol}:")
        print(f"├─ Trades: {stats['trades']}")
        print(f"├─ Wins: {stats['wins']}")
        print(f"├─ Win Rate: {stats['win_rate']:.1f}%")
        print(f"├─ Total P&L: ${stats['total_pnl']:,.2f}")
        print(f"└─ Avg P&L: ${stats['avg_pnl']:,.2f}")
    
    # Yearly stats
    print("\n" + "="*70)
    print("PERFORMANCE DASHBOARD - YEARLY SUMMARY")
    print("="*70)
    
    yearly = dashboard.calculate_yearly_stats()
    for year in sorted(yearly.keys()):
        y = yearly[year]
        print(f"\n{year}:")
        print(f"├─ Total Trades: {y.total_trades}")
        print(f"├─ Wins: {y.total_wins}")
        print(f"├─ Win Rate: {y.yearly_win_rate:.1f}%")
        print(f"├─ Total Profit: ${y.yearly_profit:,.2f}")
        print(f"├─ Best Trade: ${y.best_trade:,.2f}")
        print(f"├─ Worst Trade: ${y.worst_trade:,.2f}")
        print(f"├─ Max Consecutive Wins: {y.consecutive_wins}")
        print(f"├─ Max Consecutive Losses: {y.consecutive_losses}")
        print(f"├─ Best Month: {y.best_month}")
        print(f"└─ Worst Month: {y.worst_month}")
    
    print("\n✅ Module 5: Performance Dashboard - Testing Complete!")
