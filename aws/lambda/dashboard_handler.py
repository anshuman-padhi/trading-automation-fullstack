"""
AWS Lambda Handler: Performance Dashboard
Triggered: Daily (8 PM UTC) via EventBridge or on-demand
Purpose: Generate performance statistics and dashboard data
"""
import json
import os
import logging
from datetime import datetime
import boto3

# Import core module
import sys
sys.path.insert(0, '/opt/python')
from src.modules.performance_dashboard import PerformanceDashboard, TradeMetrics

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
ses_client = boto3.client('ses')

# Environment variables
S3_BUCKET = os.getenv('S3_BUCKET', 'trading-automation-data')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'trading@example.com')
TO_EMAIL = os.getenv('TO_EMAIL', 'your-email@example.com')
INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', '100000'))
JOURNAL_FILE = os.getenv('JOURNAL_FILE', 'trade_journal/journal.csv')


def lambda_handler(event, context):
    """
    Main Lambda handler for performance dashboard

    Returns:
        dict: Dashboard statistics and metrics
    """
    logger.info(f"Dashboard Lambda triggered at {datetime.utcnow().isoformat()}Z")

    try:
        # Load trade journal from S3
        trades = load_trades_from_s3()
        logger.info(f"Loaded {len(trades)} trades from journal")

        # Initialize dashboard
        dashboard = PerformanceDashboard(initial_capital=INITIAL_CAPITAL)

        # Add trades to dashboard
        for trade in trades:
            try:
                trade_metric = TradeMetrics(
                    trade_id=trade['trade_id'],
                    symbol=trade['symbol'],
                    entry_date=trade['entry_date'],
                    exit_date=trade.get('exit_date'),
                    pnl_dollars=float(trade.get('pnl_dollars', 0)),
                    pnl_percent=float(trade.get('pnl_percent', 0)),
                    days_held=int(trade.get('days_held', 0)),
                    setup_grade=trade.get('setup_grade', 'B'),
                    execution_grade=trade.get('execution_grade', 'B'),
                    quadrant=trade.get('quadrant', '✗✗')
                )
                dashboard.add_trade(trade_metric)
            except Exception as e:
                logger.warning(f"Failed to add trade {trade.get('trade_id')}: {str(e)}")

        # Calculate statistics
        logger.info("Calculating summary statistics...")
        summary_stats = dashboard.calculate_summary_stats()

        logger.info("Calculating monthly statistics...")
        monthly_stats = dashboard.calculate_monthly_stats()

        logger.info("Calculating yearly statistics...")
        yearly_stats = dashboard.calculate_yearly_stats()

        logger.info("Analyzing by setup grade...")
        grade_analysis = dashboard.analyze_by_setup_grade()

        # Combine all results
        dashboard_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'summary': summary_stats,
            'monthly': {k: v.__dict__ for k, v in monthly_stats.items()},
            'yearly': {k: v.__dict__ for k, v in yearly_stats.items()},
            'by_grade': grade_analysis
        }

        # Save to S3
        s3_key = f"dashboard/{datetime.utcnow().strftime('%Y/%m/%d')}/dashboard.json"

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(dashboard_data, indent=2, default=str),
            ContentType='application/json'
        )

        logger.info(f"Dashboard data saved to S3: {s3_key}")

        # Send email report if triggered by schedule
        if event.get('source') == 'aws.events':
            email_subject = f"Daily Performance Report - {datetime.utcnow().strftime('%Y-%m-%d')}"
            email_body = format_performance_email(summary_stats, monthly_stats)
            email_body_html = format_performance_html(summary_stats, monthly_stats)
            send_email(email_subject, email_body, email_body_html)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Dashboard updated successfully',
                'total_trades': summary_stats['total_trades'],
                'win_rate': summary_stats['win_rate'],
                'total_pnl': summary_stats['total_pnl'],
                's3_location': f's3://{S3_BUCKET}/{s3_key}'
            })
        }

    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def load_trades_from_s3():
    """Load trades from S3 journal"""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=JOURNAL_FILE)
        csv_content = response['Body'].read().decode('utf-8')

        # Parse CSV (simplified - use pandas in production)
        import csv
        from io import StringIO

        reader = csv.DictReader(StringIO(csv_content))
        trades = list(reader)

        return trades

    except s3_client.exceptions.NoSuchKey:
        logger.warning("No journal file found in S3")
        return []


def format_performance_email(summary, monthly):
    """Format performance stats as email"""
    current_month = datetime.utcnow().strftime('%Y-%m')
    month_stats = monthly.get(current_month)

    report = f"""
DAILY PERFORMANCE REPORT
{'=' * 70}
Date: {datetime.utcnow().strftime('%Y-%m-%d')}

OVERALL STATISTICS:
- Total Trades: {summary['total_trades']}
- Win Rate: {summary['win_rate']:.1f}%
- Profit Factor: {summary['profit_factor']:.2f}
- Expectancy: ${summary['expectancy']:.2f}

- Total P&L: ${summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:.2f}%)
- Best Trade: ${summary['best_trade']:,.2f}
- Worst Trade: ${summary['worst_trade']:,.2f}

- Avg Win: ${summary['avg_win']:,.2f}
- Avg Loss: ${summary['avg_loss']:,.2f}
- Max Drawdown: ${summary['max_drawdown']:,.2f} ({summary['max_drawdown_pct']:.1f}%)
"""

    if month_stats:
        report += f"""
CURRENT MONTH ({current_month}):
- Trades: {month_stats.trades}
- Wins/Losses: {month_stats.wins}/{month_stats.losses}
- Win Rate: {month_stats.win_rate:.1f}%
- Net Profit: ${month_stats.net_profit:,.2f}
- Return: {month_stats.return_pct:.2f}%
"""

    report += f"""
{'=' * 70}
Full dashboard available in S3.
"""
    return report


def format_performance_html(summary, monthly):
    """Format performance stats as HTML"""
    current_month = datetime.utcnow().strftime('%Y-%m')
    month_stats = monthly.get(current_month)
    
    pnl_color = "#28a745" if summary['total_pnl'] >= 0 else "#dc3545"
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px;">Daily Performance Dashboard</h2>
            <p style="color: #7f8c8d;">Date: {datetime.utcnow().strftime('%Y-%m-%d')}</p>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px; background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                <div style="text-align: center;">
                    <div style="font-size: 0.9em; color: #6c757d;">Total P&L</div>
                    <div style="font-size: 1.5em; font-weight: bold; color: {pnl_color};">${summary['total_pnl']:,.2f}</div>
                    <div style="font-size: 0.8em; color: {pnl_color};">{summary['total_pnl_pct']:.2f}%</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.9em; color: #6c757d;">Win Rate</div>
                    <div style="font-size: 1.5em; font-weight: bold;">{summary['win_rate']:.1f}%</div>
                    <div style="font-size: 0.8em; color: #6c757d;">{summary['total_trades']} Trades</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.9em; color: #6c757d;">Profit Factor</div>
                    <div style="font-size: 1.5em; font-weight: bold;">{summary['profit_factor']:.2f}</div>
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <div style="width: 48%;">
                    <h3 style="border-bottom: 1px solid #ddd; padding-bottom: 5px;">Key Metrics</h3>
                    <ul style="list-style-type: none; padding-left: 0;">
                        <li style="padding: 5px 0; border-bottom: 1px solid #eee;">Expectancy: <strong>${summary['expectancy']:.2f}</strong></li>
                        <li style="padding: 5px 0; border-bottom: 1px solid #eee;">Avg Win: <strong style="color: #28a745;">${summary['avg_win']:,.2f}</strong></li>
                        <li style="padding: 5px 0; border-bottom: 1px solid #eee;">Avg Loss: <strong style="color: #dc3545;">${summary['avg_loss']:,.2f}</strong></li>
                        <li style="padding: 5px 0; border-bottom: 1px solid #eee;">Max Drawdown: <strong style="color: #dc3545;">${summary['max_drawdown']:,.2f} ({summary['max_drawdown_pct']:.1f}%)</strong></li>
                    </ul>
                </div>
                
                <div style="width: 48%;">
                    <h3 style="border-bottom: 1px solid #ddd; padding-bottom: 5px;">Current Month ({current_month})</h3>
                    {'<ul style="list-style-type: none; padding-left: 0;">' + 
                      f'<li style="padding: 5px 0; border-bottom: 1px solid #eee;">Net Profit: <strong>${month_stats.net_profit:,.2f}</strong></li>' +
                      f'<li style="padding: 5px 0; border-bottom: 1px solid #eee;">Return: <strong>{month_stats.return_pct:.2f}%</strong></li>' +
                      f'<li style="padding: 5px 0; border-bottom: 1px solid #eee;">Win Rate: <strong>{month_stats.win_rate:.1f}%</strong></li>' +
                      '</ul>' if month_stats else '<p>No trades yet this month.</p>'}
                </div>
            </div>
            
            <p style="font-size: 0.8em; color: #999; text-align: center; margin-top: 30px;">
                Automated Report | QuantZ Trading Lab
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
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)
