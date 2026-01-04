"""
Module 6: Alerts & Monitoring
Real-time monitoring of positions, circuit breakers, and alert management
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("alerts_monitor")


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "CRITICAL"  # Immediate action required
    HIGH = "HIGH"          # Urgent review needed
    MEDIUM = "MEDIUM"      # Important notification
    LOW = "LOW"            # Informational


class AlertType(str, Enum):
    """Types of alerts"""
    DRAWDOWN_WARNING = "DRAWDOWN_WARNING"           # Account drawdown exceeding threshold
    DRAWDOWN_CRITICAL = "DRAWDOWN_CRITICAL"         # Circuit breaker triggered
    POSITION_LOSS = "POSITION_LOSS"                 # Individual position loss threshold
    POSITION_PROFIT = "POSITION_PROFIT"             # Position profit target reached
    WIN_STREAK = "WIN_STREAK"                       # Consecutive wins streak
    LOSS_STREAK = "LOSS_STREAK"                     # Consecutive losses streak
    VOLATILITY_SPIKE = "VOLATILITY_SPIKE"           # Market volatility increased
    SIZING_MISMATCH = "SIZING_MISMATCH"             # Position size vs. rules
    EXECUTION_QUALITY = "EXECUTION_QUALITY"         # Poor execution detected
    RISK_BREACH = "RISK_BREACH"                     # Risk parameters exceeded


@dataclass
class Alert:
    """Individual alert record"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: str
    symbol: Optional[str] = None
    trade_id: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    dismissed: bool = False
    dismissed_at: Optional[str] = None
    dismissed_by: Optional[str] = None


@dataclass
class Position:
    """Active trading position"""
    trade_id: str
    symbol: str
    entry_price: float
    current_price: float
    shares: int
    entry_date: str
    initial_stop: float
    target_price: Optional[float] = None
    setup_grade: str = "B"

    def get_current_pnl(self) -> float:
        """Get current unrealized P&L in dollars"""
        return (self.current_price - self.entry_price) * self.shares

    def get_current_pnl_pct(self) -> float:
        """Get current unrealized P&L in percent"""
        if self.entry_price == 0:
            return 0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100

    def is_at_stop(self) -> bool:
        """Check if position is at or below stop loss"""
        return self.current_price <= self.initial_stop

    def is_at_target(self) -> bool:
        """Check if position is at or above target"""
        if not self.target_price:
            return False
        return self.current_price >= self.target_price

    def days_held(self) -> int:
        """Get days held"""
        entry_dt = datetime.strptime(self.entry_date, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        return (now - entry_dt).days


@dataclass
class CircuitBreaker:
    """Circuit breaker for drawdown protection"""
    max_drawdown_pct: float      # Maximum allowed drawdown %
    max_daily_loss: float         # Maximum allowed daily loss $
    max_monthly_loss: float       # Maximum allowed monthly loss $
    stop_trading: bool = False    # If True, halt new trades
    stop_reason: Optional[str] = None
    triggered_at: Optional[str] = None


class AlertsMonitor:
    """
    Real-time alerts and monitoring system

    Monitors:
    - Circuit breakers (drawdown protection)
    - Individual position P&L
    - Win/loss streaks
    - Market volatility
    - Position sizing compliance
    - Risk parameter breaches
    """

    def __init__(self, account_balance: float = 100000.0):
        """
        Initialize Alerts Monitor

        Args:
            account_balance: Current account balance
        """
        self.account_balance = account_balance
        self.initial_balance = account_balance
        self.positions: Dict[str, Position] = {}
        self.alerts: List[Alert] = []
        self.alert_counter = 0

        # Circuit breaker settings
        self.circuit_breaker = CircuitBreaker(
            max_drawdown_pct=20.0,      # Stop trading if down 20%
            max_daily_loss=2000.0,       # Stop if down $2k/day
            max_monthly_loss=10000.0     # Stop if down $10k/month
        )

        # Alert thresholds
        self.position_loss_threshold = 5.0  # Alert if loss > 5%
        self.position_profit_threshold = 10.0  # Alert if profit > 10%
        self.loss_streak_threshold = 3  # Alert after 3 consecutive losses
        self.win_streak_threshold = 5  # Alert after 5 consecutive wins

        logger.info(f"Initialized AlertsMonitor (Balance: ${account_balance:,.2f})")

    def create_alert_id(self) -> str:
        """Generate unique alert ID"""
        self.alert_counter += 1
        return f"ALR{self.alert_counter:05d}"

    def add_position(self, position: Position) -> None:
        """Add active position for monitoring"""
        self.positions[position.trade_id] = position
        logger.info(f"Position added: {position.symbol} ({position.trade_id})")

    def remove_position(self, trade_id: str) -> None:
        """Remove closed position from monitoring"""
        if trade_id in self.positions:
            del self.positions[trade_id]
            logger.info(f"Position removed: {trade_id}")

    def update_position_price(self, trade_id: str, current_price: float) -> None:
        """Update current price for a position"""
        if trade_id in self.positions:
            self.positions[trade_id].current_price = current_price

    def update_account_balance(self, new_balance: float) -> None:
        """Update account balance"""
        self.account_balance = new_balance

    def check_position_alerts(self) -> List[Alert]:
        """Check individual position P&L alerts"""
        new_alerts = []

        for trade_id, position in self.positions.items():
            pnl_pct = position.get_current_pnl_pct()
            pnl_dollars = position.get_current_pnl()

            # Check position loss alert
            if pnl_pct < -self.position_loss_threshold:
                alert = self._create_alert(
                    alert_type=AlertType.POSITION_LOSS,
                    severity=AlertSeverity.HIGH,
                    title=f"Position Loss Alert: {position.symbol}",
                    message=f"{position.symbol} position down {pnl_pct:.2f}% (${pnl_dollars:,.2f})",
                    symbol=position.symbol,
                    trade_id=trade_id,
                    value=pnl_pct,
                    threshold=-self.position_loss_threshold
                )
                new_alerts.append(alert)

            # Check stop loss hit
            if position.is_at_stop():
                alert = self._create_alert(
                    alert_type=AlertType.POSITION_LOSS,
                    severity=AlertSeverity.CRITICAL,
                    title=f"STOP LOSS HIT: {position.symbol}",
                    message=f"{position.symbol} has hit stop loss at ${position.initial_stop:.2f}. Exit immediately!",
                    symbol=position.symbol,
                    trade_id=trade_id,
                    value=position.current_price,
                    threshold=position.initial_stop
                )
                new_alerts.append(alert)

            # Check profit target alert
            if position.is_at_target():
                alert = self._create_alert(
                    alert_type=AlertType.POSITION_PROFIT,
                    severity=AlertSeverity.MEDIUM,
                    title=f"Profit Target Reached: {position.symbol}",
                    message=f"{position.symbol} has reached target ${position.target_price:.2f}. Consider taking profits.",
                    symbol=position.symbol,
                    trade_id=trade_id,
                    value=pnl_pct,
                    threshold=self.position_profit_threshold
                )
                new_alerts.append(alert)

            # Check position profit threshold (but not at target)
            if pnl_pct > self.position_profit_threshold and not position.is_at_target():
                alert = self._create_alert(
                    alert_type=AlertType.POSITION_PROFIT,
                    severity=AlertSeverity.LOW,
                    title=f"Position Profit: {position.symbol}",
                    message=f"{position.symbol} position up {pnl_pct:.2f}% (${pnl_dollars:,.2f})",
                    symbol=position.symbol,
                    trade_id=trade_id,
                    value=pnl_pct,
                    threshold=self.position_profit_threshold
                )
                new_alerts.append(alert)

        self.alerts.extend(new_alerts)
        return new_alerts

    def check_circuit_breaker(self) -> Optional[Alert]:
        """Check circuit breaker conditions"""
        drawdown = self.initial_balance - self.account_balance
        drawdown_pct = (drawdown / self.initial_balance) * 100

        # Check drawdown threshold
        if drawdown_pct >= self.circuit_breaker.max_drawdown_pct:
            self.circuit_breaker.stop_trading = True
            self.circuit_breaker.triggered_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.circuit_breaker.stop_reason = f"Account drawdown {drawdown_pct:.2f}%"

            alert = self._create_alert(
                alert_type=AlertType.DRAWDOWN_CRITICAL,
                severity=AlertSeverity.CRITICAL,
                title="CIRCUIT BREAKER TRIGGERED",
                message=f"Account drawdown {drawdown_pct:.2f}% (${drawdown:,.2f}). STOP TRADING IMMEDIATELY!",
                value=drawdown_pct,
                threshold=self.circuit_breaker.max_drawdown_pct
            )
            self.alerts.append(alert)
            logger.critical(f"Circuit breaker triggered: {alert.message}")
            return alert

        # Check warning level (80% of max)
        if drawdown_pct >= self.circuit_breaker.max_drawdown_pct * 0.8:
            alert = self._create_alert(
                alert_type=AlertType.DRAWDOWN_WARNING,
                severity=AlertSeverity.HIGH,
                title="Drawdown Warning",
                message=f"Account drawdown {drawdown_pct:.2f}% (${drawdown:,.2f}). Approaching circuit breaker!",
                value=drawdown_pct,
                threshold=self.circuit_breaker.max_drawdown_pct * 0.8
            )
            self.alerts.append(alert)
            return alert

        return None

    def check_trade_streak(self, recent_trades: List[Dict]) -> Optional[Alert]:
        """Check for win/loss streaks"""
        if not recent_trades:
            return None

        # Calculate streak
        streak = 0
        streak_type = None

        for trade in reversed(recent_trades):
            if trade.get('pnl_dollars', 0) > 0:
                if streak_type == 'win' or streak_type is None:
                    streak_type = 'win'
                    streak += 1
                else:
                    break
            else:
                if streak_type == 'loss' or streak_type is None:
                    streak_type = 'loss'
                    streak += 1
                else:
                    break

        # Alert on significant streaks
        if streak_type == 'loss' and streak >= self.loss_streak_threshold:
            alert = self._create_alert(
                alert_type=AlertType.LOSS_STREAK,
                severity=AlertSeverity.MEDIUM,
                title=f"Loss Streak: {streak} Trades",
                message=f"{streak} consecutive losing trades. Review strategy and take a break.",
                value=streak,
                threshold=self.loss_streak_threshold
            )
            self.alerts.append(alert)
            return alert

        if streak_type == 'win' and streak >= self.win_streak_threshold:
            alert = self._create_alert(
                alert_type=AlertType.WIN_STREAK,
                severity=AlertSeverity.LOW,
                title=f"Win Streak: {streak} Trades",
                message=f"{streak} consecutive winning trades! Maintain discipline and risk management.",
                value=streak,
                threshold=self.win_streak_threshold
            )
            self.alerts.append(alert)
            return alert

        return None

    def check_position_sizing(self, position: Position, expected_max_pnl: float) -> Optional[Alert]:
        """Check if position sizing matches risk rules"""
        actual_pnl = position.get_current_pnl()

        # If actual loss significantly exceeds expected, alert
        if actual_pnl < -expected_max_pnl * 1.5:
            alert = self._create_alert(
                alert_type=AlertType.SIZING_MISMATCH,
                severity=AlertSeverity.HIGH,
                title=f"Position Sizing Mismatch: {position.symbol}",
                message=f"{position.symbol} loss ${actual_pnl:,.2f} exceeds expected max ${expected_max_pnl:,.2f}",
                symbol=position.symbol,
                trade_id=position.trade_id,
                value=actual_pnl,
                threshold=-expected_max_pnl
            )
            self.alerts.append(alert)
            return alert

        return None

    def check_execution_quality(self, position: Position) -> Optional[Alert]:
        """Check execution quality based on entry price vs market"""
        entry_slippage_pct = ((position.current_price - position.entry_price) / position.entry_price) * 100

        # Alert if significant slippage at entry
        if entry_slippage_pct < -3.0:  # More than 3% adverse move immediately
            alert = self._create_alert(
                alert_type=AlertType.EXECUTION_QUALITY,
                severity=AlertSeverity.MEDIUM,
                title=f"Poor Execution: {position.symbol}",
                message=f"{position.symbol} slipped {entry_slippage_pct:.2f}% at entry. Review execution process.",
                symbol=position.symbol,
                trade_id=position.trade_id,
                value=entry_slippage_pct,
                threshold=-3.0
            )
            self.alerts.append(alert)
            return alert

        return None

    def dismiss_alert(self, alert_id: str, dismissed_by: str = "user") -> bool:
        """Dismiss an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.dismissed = True
                alert.dismissed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                alert.dismissed_by = dismissed_by
                logger.info(f"Alert dismissed: {alert_id}")
                return True
        return False

    def get_active_alerts(self) -> List[Alert]:
        """Get all active (non-dismissed) alerts"""
        return [a for a in self.alerts if not a.dismissed]

    def get_critical_alerts(self) -> List[Alert]:
        """Get all critical severity alerts"""
        return [a for a in self.get_active_alerts() 
                if a.severity == AlertSeverity.CRITICAL]

    def get_alerts_by_type(self, alert_type: AlertType) -> List[Alert]:
        """Get alerts by type"""
        return [a for a in self.get_active_alerts() if a.alert_type == alert_type]

    def get_alerts_by_symbol(self, symbol: str) -> List[Alert]:
        """Get alerts for specific symbol"""
        return [a for a in self.get_active_alerts() if a.symbol == symbol]

    def get_alert_summary(self) -> Dict:
        """Get summary of all alerts"""
        active = self.get_active_alerts()

        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active),
            "critical": len([a for a in active if a.severity == AlertSeverity.CRITICAL]),
            "high": len([a for a in active if a.severity == AlertSeverity.HIGH]),
            "medium": len([a for a in active if a.severity == AlertSeverity.MEDIUM]),
            "low": len([a for a in active if a.severity == AlertSeverity.LOW]),
            "circuit_breaker_active": self.circuit_breaker.stop_trading,
            "positions_monitored": len(self.positions),
        }

    def _create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        symbol: Optional[str] = None,
        trade_id: Optional[str] = None,
        value: Optional[float] = None,
        threshold: Optional[float] = None,
    ) -> Alert:
        """Create and log an alert"""
        alert = Alert(
            alert_id=self.create_alert_id(),
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol=symbol,
            trade_id=trade_id,
            value=value,
            threshold=threshold
        )

        logger.warning(f"[{severity.value}] {title}: {message}")

        return alert

    def print_alert_summary(self) -> None:
        """Print alert summary report"""
        summary = self.get_alert_summary()

        print("\n" + "="*70)
        print("ALERTS MONITOR - SUMMARY REPORT")
        print("="*70)

        print(f"\n📊 ALERT STATISTICS:")
        print(f"├─ Total Alerts (All Time): {summary['total_alerts']}")
        print(f"├─ Active Alerts: {summary['active_alerts']}")
        print(f"├─ Critical: {summary['critical']}")
        print(f"├─ High: {summary['high']}")
        print(f"├─ Medium: {summary['medium']}")
        print(f"└─ Low: {summary['low']}")

        print(f"\n🛡️  CIRCUIT BREAKER:")
        print(f"├─ Active: {summary['circuit_breaker_active']}")
        print(f"├─ Max Drawdown: {self.circuit_breaker.max_drawdown_pct:.1f}%")
        print(f"├─ Current Balance: ${self.account_balance:,.2f}")
        print(f"├─ Initial Balance: ${self.initial_balance:,.2f}")
        current_dd = ((self.initial_balance - self.account_balance) / self.initial_balance) * 100
        print(f"└─ Current Drawdown: {current_dd:.2f}%")

        print(f"\n📍 POSITION MONITORING:")
        print(f"├─ Positions Tracked: {summary['positions_monitored']}")

        for trade_id, position in self.positions.items():
            pnl = position.get_current_pnl()
            pnl_pct = position.get_current_pnl_pct()
            status = "🟢" if pnl > 0 else "🔴"
            print(f"├─ {status} {position.symbol} ({trade_id}): ${pnl:,.2f} ({pnl_pct:.2f}%)")

        print("\n" + "="*70)

    def print_active_alerts(self) -> None:
        """Print all active alerts"""
        active = self.get_active_alerts()

        if not active:
            print("\n✅ No active alerts")
            return

        print("\n" + "="*70)
        print("ALERTS MONITOR - ACTIVE ALERTS")
        print("="*70)

        for alert in sorted(active, key=lambda a: a.severity.value):
            severity_icon = {
                AlertSeverity.CRITICAL: "🔴",
                AlertSeverity.HIGH: "🟠",
                AlertSeverity.MEDIUM: "🟡",
                AlertSeverity.LOW: "🔵",
            }

            icon = severity_icon.get(alert.severity, "⚪")

            print(f"\n{icon} [{alert.severity.value}] {alert.title}")
            print(f"   ID: {alert.alert_id}")
            print(f"   Message: {alert.message}")
            print(f"   Time: {alert.timestamp}")

            if alert.symbol:
                print(f"   Symbol: {alert.symbol}")
            if alert.value is not None and alert.threshold is not None:
                print(f"   Value: {alert.value:.2f} (Threshold: {alert.threshold:.2f})")

        print("\n" + "="*70)


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*70)
    print("MODULE 6: ALERTS & MONITORING - TEST")
    print("="*70)

    # Initialize monitor
    monitor = AlertsMonitor(account_balance=100000.0)

    # Add positions
    positions = [
        Position(
            trade_id="T00001",
            symbol="NVDA",
            entry_price=150.00,
            current_price=152.50,
            shares=100,
            entry_date="2026-01-01 10:00:00",
            initial_stop=145.00,
            target_price=165.00,
            setup_grade="A"
        ),
        Position(
            trade_id="T00002",
            symbol="TSLA",
            entry_price=200.00,
            current_price=193.00,
            shares=50,
            entry_date="2026-01-02 10:00:00",
            initial_stop=195.00,
            target_price=220.00,
            setup_grade="B"
        ),
        Position(
            trade_id="T00003",
            symbol="AMD",
            entry_price=120.00,
            current_price=130.50,
            shares=75,
            entry_date="2026-01-06 10:00:00",
            initial_stop=115.00,
            target_price=140.00,
            setup_grade="A"
        ),
    ]

    for pos in positions:
        monitor.add_position(pos)

    print("\n\n✅ TEST CASE 1: Position Alerts")
    print("-" * 70)
    monitor.check_position_alerts()

    print("\n\n✅ TEST CASE 2: Circuit Breaker (Normal)")
    print("-" * 70)
    monitor.check_circuit_breaker()

    print("\n\n✅ TEST CASE 3: Circuit Breaker (Drawdown Warning)")
    print("-" * 70)
    monitor.update_account_balance(82000.0)  # 18% drawdown
    monitor.check_circuit_breaker()

    print("\n\n✅ TEST CASE 4: Trade Streak Alert")
    print("-" * 70)
    recent_trades = [
        {'pnl_dollars': -275.0},
        {'pnl_dollars': -380.0},
        {'pnl_dollars': -420.0},
        {'pnl_dollars': 650.0},
    ]
    monitor.check_trade_streak(recent_trades)

    print("\n\n✅ TEST CASE 5: Position Sizing Check")
    print("-" * 70)
    monitor.check_position_sizing(positions[1], expected_max_pnl=500.0)

    print("\n\n✅ TEST CASE 6: Execution Quality Check")
    print("-" * 70)
    monitor.check_execution_quality(positions[1])

    # Print reports
    monitor.print_alert_summary()
    monitor.print_active_alerts()

    # Dismiss some alerts
    print("\n\n✅ TEST CASE 7: Dismiss Alerts")
    print("-" * 70)
    active = monitor.get_active_alerts()
    if active:
        monitor.dismiss_alert(active[0].alert_id, "test_user")
        print(f"Dismissed alert: {active[0].alert_id}")

    # Final reports
    print("\n\nFinal Summary (after dismissal):")
    monitor.print_alert_summary()

    print("\n✅ Module 6: Alerts & Monitoring - Testing Complete!")
