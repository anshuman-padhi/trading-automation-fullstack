"""
AWS Lambda handler for Module 6: Alerts & Monitoring

- Triggered by EventBridge every 5 minutes
- Loads current positions & account state (placeholder: from S3)
- Runs AlertsMonitor checks (positions, circuit breaker, streaks)
- Sends email notifications via SES for new HIGH/CRITICAL alerts
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

import boto3

# Import your module 6 core logic
from src.modules.alerts_monitor import (
    AlertsMonitor,
    Position,
    AlertSeverity,
    AlertType,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ==========
# ENV VARS
# ==========

SES_REGION = os.getenv("SES_REGION", "us-east-1")
ALERTS_FROM_EMAIL = os.getenv("ALERTS_FROM_EMAIL", "alerts@example.com")
ALERTS_TO_EMAIL = os.getenv("ALERTS_TO_EMAIL", "you@example.com")
POSITIONS_S3_BUCKET = os.getenv("POSITIONS_S3_BUCKET", "your-positions-bucket")
POSITIONS_S3_KEY = os.getenv("POSITIONS_S3_KEY", "positions/active_positions.json")
ACCOUNT_STATE_S3_BUCKET = os.getenv("ACCOUNT_STATE_S3_BUCKET", "your-account-bucket")
ACCOUNT_STATE_S3_KEY = os.getenv("ACCOUNT_STATE_S3_KEY", "account/account_state.json")

ses_client = boto3.client("ses", region_name=SES_REGION)
s3_client = boto3.client("s3")


# ==========
# HELPERS
# ==========

def load_json_from_s3(bucket: str, key: str) -> Dict[str, Any]:
    """Load JSON object from S3 (helper)."""
    try:
        resp = s3_client.get_object(Bucket=bucket, Key=key)
        data = resp["Body"].read()
        return json.loads(data)
    except s3_client.exceptions.NoSuchKey:
        logger.warning(f"S3 object not found: s3://{bucket}/{key}")
        return {}
    except Exception as e:
        logger.error(f"Error loading s3://{bucket}/{key}: {e}", exc_info=True)
        return {}


def send_alert_email(subject: str, body_text: str, body_html: str) -> None:
    """Send alert via SES."""
    try:
        ses_client.send_email(
            Source=ALERTS_FROM_EMAIL,
            Destination={"ToAddresses": [ALERTS_TO_EMAIL]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            },
        )
        logger.info(f"Alert email sent to {ALERTS_TO_EMAIL}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send SES email: {e}", exc_info=True)


def build_email_for_alerts(alerts: List[Dict[str, Any]]) -> (str, str, str):
    """Build subject, text body, html body for a batch of alerts."""
    if not alerts:
        return "", "", ""

    # Use highest severity for subject
    severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    highest = sorted(alerts, key=lambda a: severity_order.index(a["severity"]))[0]

    subject = f"[{highest['severity']}] Trading Alerts ({len(alerts)} new)"

    lines = []
    for a in alerts:
        lines.append(
            f"[{a['severity']}] {a['title']} - {a['message']} "
            f"(ID: {a['alert_id']}, Time: {a['timestamp']})"
        )

    body_text = "New trading alerts:\n\n" + "\n".join(lines)

    # Simple HTML version
    html_items = []
    for a in alerts:
        html_items.append(
            f"<li><strong>[{a['severity']}] {a['title']}</strong><br/>"
            f"{a['message']}<br/>"
            f"<em>ID: {a['alert_id']} | Time: {a['timestamp']}</em></li>"
        )

    body_html = (
        "<html><body>"
        "<h2>New Trading Alerts</h2>"
        "<ul>"
        + "".join(html_items) +
        "</ul>"
        "</body></html>"
    )

    return subject, body_text, body_html


# ==========
# LAMBDA HANDLER
# ==========

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Entry point for AWS Lambda.

    EventBridge schedule: every 5 minutes.
    Responsibilities:
    - Load current positions & account balance from S3 (or other data source)
    - Run AlertsMonitor checks
    - Email any new HIGH/CRITICAL alerts
    - Return summary for logging/monitoring
    """
    logger.info(f"alerts_handler invoked at {datetime.utcnow().isoformat()}Z")
    logger.info(f"Event: {json.dumps(event)}")

    # 1) Load account state
    account_state = load_json_from_s3(ACCOUNT_STATE_S3_BUCKET, ACCOUNT_STATE_S3_KEY)
    account_balance = float(account_state.get("account_balance", 100000.0))

    # 2) Initialize AlertsMonitor
    monitor = AlertsMonitor(account_balance=account_balance)

    # 3) Load positions
    positions_data = load_json_from_s3(POSITIONS_S3_BUCKET, POSITIONS_S3_KEY)
    positions_list = positions_data.get("positions", [])

    for p in positions_list:
        try:
            pos = Position(
                trade_id=p["trade_id"],
                symbol=p["symbol"],
                entry_price=float(p["entry_price"]),
                current_price=float(p["current_price"]),
                shares=int(p["shares"]),
                entry_date=p["entry_date"],   # "YYYY-MM-DD HH:MM:SS"
                initial_stop=float(p["initial_stop"]),
                target_price=float(p["target_price"]) if p.get("target_price") else None,
                setup_grade=p.get("setup_grade", "B"),
            )
            monitor.add_position(pos)
        except KeyError as e:
            logger.error(f"Missing key in position data: {e} | data={p}")
        except Exception as e:
            logger.error(f"Error creating Position from data {p}: {e}", exc_info=True)

    # 4) Run position-based alerts
    monitor.check_position_alerts()

    # 5) Run circuit breaker checks
    monitor.check_circuit_breaker()

    # 6) Win/loss streak (if you save recent trades in account_state)
    recent_trades = account_state.get("recent_trades", [])
    if recent_trades:
        monitor.check_trade_streak(recent_trades)

    # 7) Collect active alerts
    active_alerts = monitor.get_active_alerts()

    # Convert Alert dataclasses to dicts for SES & response
    alert_dicts: List[Dict[str, Any]] = []
    for a in active_alerts:
        alert_dicts.append(
            {
                "alert_id": a.alert_id,
                "type": a.alert_type.value,
                "severity": a.severity.value,
                "title": a.title,
                "message": a.message,
                "timestamp": a.timestamp,
                "symbol": a.symbol,
                "trade_id": a.trade_id,
                "value": a.value,
                "threshold": a.threshold,
            }
        )

    # 8) Email only new HIGH/CRITICAL alerts (simple: all active HIGH/CRITICAL)
    important_alerts = [
        a for a in alert_dicts
        if a["severity"] in ("CRITICAL", "HIGH")
    ]

    if important_alerts:
        subject, body_text, body_html = build_email_for_alerts(important_alerts)
        if subject:
            send_alert_email(subject, body_text, body_html)

    # 9) Build summary for logs / CloudWatch / debugging
    summary = monitor.get_alert_summary()
    logger.info(f"Alerts summary: {json.dumps(summary)}")

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Alerts handler executed",
                "summary": summary,
                "alerts": alert_dicts,
            }
        ),
    }
