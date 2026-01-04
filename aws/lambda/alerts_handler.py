"""
AWS Lambda Handler: Alerts & Monitoring
Triggered: Every 5 minutes via EventBridge
Purpose: Monitor positions and send critical alerts
"""
import json
import os
import logging
from datetime import datetime
import boto3

# Import core module
import sys
sys.path.insert(0, '/opt/python')
from src.modules.alerts_monitor import AlertsMonitor, Position, AlertSeverity

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
ses_client = boto3.client('ses')

# Environment variables
S3_BUCKET = os.getenv('S3_BUCKET', 'trading-automation-data')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'alerts@example.com')
TO_EMAIL = os.getenv('TO_EMAIL', 'your-email@example.com')
POSITIONS_FILE = os.getenv('POSITIONS_FILE', 'positions/active_positions.json')
ACCOUNT_STATE_FILE = os.getenv('ACCOUNT_STATE_FILE', 'account/account_state.json')


def lambda_handler(event, context):
    """
    Main Lambda handler for alerts monitoring

    Returns:
        dict: Alert summary and any critical alerts
    """
    logger.info(f"Alerts Monitor Lambda triggered at {datetime.utcnow().isoformat()}Z")

    try:
        # Load account state
        account_state = load_account_state()
        account_balance = account_state.get('account_balance', 100000.0)

        # Initialize monitor
        monitor = AlertsMonitor(account_balance=account_balance)

        # Load active positions
        positions = load_active_positions()
        logger.info(f"Monitoring {len(positions)} active positions")

        for pos_data in positions:
            try:
                position = Position(
                    trade_id=pos_data['trade_id'],
                    symbol=pos_data['symbol'],
                    entry_price=float(pos_data['entry_price']),
                    current_price=float(pos_data['current_price']),
                    shares=int(pos_data['shares']),
                    entry_date=pos_data['entry_date'],
                    initial_stop=float(pos_data['initial_stop']),
                    target_price=float(pos_data.get('target_price', 0)) or None,
                    setup_grade=pos_data.get('setup_grade', 'B')
                )
                monitor.add_position(position)
            except Exception as e:
                logger.warning(f"Failed to add position {pos_data.get('symbol')}: {str(e)}")

        # Run all monitoring checks
        logger.info("Checking position alerts...")
        monitor.check_position_alerts()

        logger.info("Checking circuit breaker...")
        monitor.check_circuit_breaker()

        logger.info("Checking trade streaks...")
        recent_trades = account_state.get('recent_trades', [])
        monitor.check_trade_streak(recent_trades)

        # Get alert summary
        summary = monitor.get_alert_summary()
        logger.info(f"Alert summary: {summary}")

        # Get critical alerts
        critical_alerts = monitor.get_critical_alerts()
        high_alerts = [a for a in monitor.get_active_alerts() if a.severity == AlertSeverity.HIGH]

        # Send email for critical/high alerts
        if critical_alerts or high_alerts:
            email_subject = f"[ALERT] QuantZ Alerts - {len(critical_alerts)} Critical, {len(high_alerts)} High"
            email_body = format_alerts_email(critical_alerts, high_alerts)
            email_body_html = format_alerts_html(critical_alerts, high_alerts)
            send_email(email_subject, email_body, email_body_html)

        # Save alert summary to S3
        alert_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'summary': summary,
            'critical_alerts': [format_alert_dict(a) for a in critical_alerts],
            'high_alerts': [format_alert_dict(a) for a in high_alerts],
            'circuit_breaker_active': monitor.circuit_breaker.stop_trading
        }

        s3_key = f"alerts/{datetime.utcnow().strftime('%Y/%m/%d')}/alerts_{datetime.utcnow().strftime('%H%M%S')}.json"

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(alert_data, indent=2),
            ContentType='application/json'
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Alerts monitoring completed',
                'summary': summary,
                'critical_count': len(critical_alerts),
                'high_count': len(high_alerts),
                's3_location': f's3://{S3_BUCKET}/{s3_key}'
            })
        }

    except Exception as e:
        logger.error(f"Error in alerts monitoring: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def load_account_state():
    """Load account state from S3"""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=ACCOUNT_STATE_FILE)
        data = json.loads(response['Body'].read().decode('utf-8'))
        return data
    except s3_client.exceptions.NoSuchKey:
        logger.warning("No account state file found")
        return {'account_balance': 100000.0, 'recent_trades': []}


def load_active_positions():
    """Load active positions from S3"""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=POSITIONS_FILE)
        data = json.loads(response['Body'].read().decode('utf-8'))
        return data.get('positions', [])
    except s3_client.exceptions.NoSuchKey:
        logger.warning("No positions file found")
        return []


def format_alert_dict(alert):
    """Convert Alert object to dictionary"""
    return {
        'alert_id': alert.alert_id,
        'type': alert.alert_type.value,
        'severity': alert.severity.value,
        'title': alert.title,
        'message': alert.message,
        'timestamp': alert.timestamp,
        'symbol': alert.symbol,
        'trade_id': alert.trade_id,
        'value': alert.value,
        'threshold': alert.threshold
    }


def format_alerts_email(critical_alerts, high_alerts):
    """Format alerts as plain text"""
    report = f"""
TRADING SYSTEM ALERTS
{'=' * 70}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

"""

    if critical_alerts:
        report += f"""
🔴 CRITICAL ALERTS ({len(critical_alerts)}):
{'=' * 70}
"""
        for alert in critical_alerts:
            report += f"""
Alert ID: {alert.alert_id}
Title: {alert.title}
Message: {alert.message}
Symbol: {alert.symbol or 'N/A'}
Time: {alert.timestamp}
---
"""

    if high_alerts:
        report += f"""
🟠 HIGH PRIORITY ALERTS ({len(high_alerts)}):
{'=' * 70}
"""
        for alert in high_alerts:
            report += f"""
Alert ID: {alert.alert_id}
Title: {alert.title}
Message: {alert.message}
Symbol: {alert.symbol or 'N/A'}
Time: {alert.timestamp}
---
"""

    report += f"""
{'=' * 70}
This is an automated alert from your QuantZ Trading Lab.
Review immediately and take appropriate action.
"""
    return report

def format_alerts_html(critical_alerts, high_alerts):
    """Format alerts as HTML"""
    critical_rows = ""
    for alert in critical_alerts:
        critical_rows += f"""
        <div style="border-left: 4px solid #dc3545; padding: 10px; margin-bottom: 15px; background-color: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <strong style="color: #dc3545;">{alert.title}</strong>
                <span style="color: #6c757d; font-size: 0.9em;">{alert.timestamp}</span>
            </div>
            <p style="margin: 5px 0;">{alert.message}</p>
            <div style="font-size: 0.9em; color: #6c757d; margin-top: 5px;">
                Symbol: <strong>{alert.symbol or 'N/A'}</strong> | ID: {alert.alert_id}
            </div>
        </div>
        """
        
    high_rows = ""
    for alert in high_alerts:
        high_rows += f"""
        <div style="border-left: 4px solid #ffc107; padding: 10px; margin-bottom: 15px; background-color: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <strong style="color: #d39e00;">{alert.title}</strong>
                <span style="color: #6c757d; font-size: 0.9em;">{alert.timestamp}</span>
            </div>
            <p style="margin: 5px 0;">{alert.message}</p>
            <div style="font-size: 0.9em; color: #6c757d; margin-top: 5px;">
                Symbol: <strong>{alert.symbol or 'N/A'}</strong> | ID: {alert.alert_id}
            </div>
        </div>
        """

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 800px; margin: 0 auto; background-color: #fff; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 0;">Trading System Alerts</h2>
            <p style="color: #6c757d; font-size: 0.9em;">Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            
            {f'<h3 style="color: #dc3545; margin-top: 20px;">🔴 Critical Alerts ({len(critical_alerts)})</h3>' + critical_rows if critical_alerts else ''}
            
            {f'<h3 style="color: #ffc107; margin-top: 20px;">🟠 High Priority Alerts ({len(high_alerts)})</h3>' + high_rows if high_alerts else ''}
            
            <p style="margin-top: 30px; font-size: 0.8em; color: #999; text-align: center;">
                Automated Alert | QuantZ Trading Lab<br>
                <em>Review immediately and take appropriate action.</em>
            </p>
        </div>
    </body>
    </html>
    """
    return html


def send_email(subject, body, body_html=None):
    """Send email via SES"""
    try:
        message = {
            'Subject': {'Data': subject, 'Charset': 'UTF-8'},
            'Body': {'Text': {'Data': body, 'Charset': 'UTF-8'}}
        }
        if body_html:
            message['Body']['Html'] = {'Data': body_html, 'Charset': 'UTF-8'}
            
        ses_client.send_email(
            Source=FROM_EMAIL,
            Destination={'ToAddresses': [TO_EMAIL]},
            Message=message
        )
        logger.info(f"Alert email sent to {TO_EMAIL}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)
