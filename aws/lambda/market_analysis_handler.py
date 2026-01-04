"""
AWS Lambda Handler: Market Analysis
Triggered: Weekly (Sundays 6 PM UTC) via EventBridge
Purpose: Analyze market environment and send weekly report
"""
import json
import os
# Set cache directory to writable location for yfinance
os.environ['XDG_CACHE_HOME'] = '/tmp/.cache'

import logging
from datetime import datetime
import boto3

# Import core module
import sys
from src.modules.market_analysis import MarketAnalyzer
from src.modules.data_fetcher import DataFetcher

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
ses_client = boto3.client('ses')

# Environment variables
S3_BUCKET = os.getenv('S3_BUCKET', 'trading-automation-data')
SES_REGION = os.getenv('SES_REGION', 'us-east-1')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'anshupadhi@gmail.com')
TO_EMAIL = os.getenv('TO_EMAIL', 'anshupadhi@gmail.com')


def lambda_handler(event, context):
    """
    Main Lambda handler for market analysis

    Returns:
        dict: Response with statusCode and analysis results
    """
    logger.info(f"Market Analysis Lambda triggered at {datetime.utcnow().isoformat()}Z")
    logger.info(f"Event: {json.dumps(event)}")

    try:
        # Initialize DataFetcher and Analyzer
        data_fetcher = DataFetcher()
        analyzer = MarketAnalyzer(data_fetcher=data_fetcher)

        # Network Diagnostic (Alpaca)
        try:
            # Simple check if we can reach Alpaca
            # (Implicit in data_fetcher init but good to log)
             if not data_fetcher.client:
                 logger.warning("Alpaca Client failed to initialize.")
        except Exception as e:
            logger.error(f"Dependency check failed: {e}")

        # Perform market analysis
        logger.info("Running market environment analysis...")
        environment = analyzer.analyze_market_environment()

        logger.info("Running breadth analysis...")
        breadth = analyzer.calculate_breadth_metrics()

        logger.info("Calculating VIX metrics...")
        vix_analysis = analyzer.analyze_vix()

        # Combine results
        analysis_results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "market_environment": environment,
            "breadth_metrics": breadth,
            "vix_analysis": vix_analysis
        }

        # Save to S3
        s3_key = f"market_analysis/{datetime.utcnow().strftime('%Y/%m/%d')}/analysis.json"
        logger.info(f"Saving results to S3: s3://{S3_BUCKET}/{s3_key}")

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(analysis_results, indent=2),
            ContentType='application/json'
        )

        # Send email report
        email_subject = f"Weekly Market Analysis - {environment['regime']} Market"
        email_body_text = format_email_report_text(analysis_results)
        email_body_html = format_email_report_html(analysis_results)

        logger.info(f"Sending email to {TO_EMAIL}...")
        send_email(email_subject, email_body_text, email_body_html)

        logger.info("Market analysis completed successfully")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Market analysis completed',
                'environment': environment['regime'],
                's3_location': f's3://{S3_BUCKET}/{s3_key}'
            })
        }

    except Exception as e:
        logger.error(f"Error in market analysis: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def format_email_report_text(results):
    """Format analysis results as plain text email"""
    env = results['market_environment']
    breadth = results['breadth_metrics']
    vix = results['vix_analysis']

    report = f"""
WEEKLY MARKET ANALYSIS REPORT
{'=' * 70}
Date: {results['timestamp']}

MARKET ENVIRONMENT: {env['regime']}
Reasoning: {env.get('explanation', '')}
Position Sizing: {env['position_size_pct']}%
Market Confidence: {env['confidence']}

BREADTH METRICS:
- Stocks Above 20-day MA: {breadth.get('pct_above_20ma', 0):.1f}%
- Stocks Above 50-day MA: {breadth.get('pct_above_50ma', 0):.1f}%
- Stocks Above 200-day MA: {breadth.get('pct_above_200ma', 0):.1f}%
- New Highs vs New Lows: {breadth.get('new_highs', 0)} vs {breadth.get('new_lows', 0)}

VIX ANALYSIS:
- Current VIX: {vix.get('current_vix', 0):.2f}
- VIX Status: {vix.get('status', 'Unknown')}
- Market Fear Level: {vix.get('fear_level', 'Unknown')}
- Impact: {vix.get('explanation', 'N/A')}

RECOMMENDATION:
Exposure Guidance: {env.get('exposure_guidance', 'N/A')}
Position Sizing: {env.get('recommendation', 'Continue monitoring market conditions.')}

{'=' * 70}
This is an automated report from your QuantZ Trading System.
"""
    return report

def format_email_report_html(results):
    """Format analysis results as HTML email"""
    env = results['market_environment']
    breadth = results['breadth_metrics']
    vix = results['vix_analysis']
    
    # Colors
    regime = env['regime']
    regime_color = "#28a745" if "Bull" in regime else "#dc3545" if "Bear" in regime else "#ffc107"
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px;">Weekly Market Analysis Report</h2>
            <p style="color: #7f8c8d;">Date: {results['timestamp']}</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h3 style="margin-top: 0;">Market Environment: <span style="background-color: {regime_color}; color: white; padding: 3px 8px; border-radius: 3px;">{env['regime']}</span></h3>
                <p><strong>Why?</strong> {env.get('explanation', 'Analysis of price action and breadth indicates this regime.')}</p>
                <p><strong>Position Sizing:</strong> {env['position_size_pct']}%</p>
                <p><strong>Confidence:</strong> {env['confidence']}</p>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <div style="width: 48%;">
                    <h3 style="border-bottom: 1px solid #ddd; padding-bottom: 5px;">Breadth Metrics</h3>
                    <ul style="list-style-type: none; padding-left: 0;">
                        <li style="padding: 5px 0; border-bottom: 1px solid #eee;">Above 20-day MA: <strong>{breadth.get('pct_above_20ma', 0):.1f}%</strong></li>
                        <li style="padding: 5px 0; border-bottom: 1px solid #eee;">Above 50-day MA: <strong>{breadth.get('pct_above_50ma', 0):.1f}%</strong></li>
                        <li style="padding: 5px 0; border-bottom: 1px solid #eee;">Above 200-day MA: <strong>{breadth.get('pct_above_200ma', 0):.1f}%</strong></li>
                        <li style="padding: 5px 0; border-bottom: 1px solid #eee;">New Highs/Lows: <strong>{breadth.get('new_highs', 0)} / {breadth.get('new_lows', 0)}</strong></li>
                    </ul>
                </div>
                
                    <div style="width: 48%;">
                    <h3 style="border-bottom: 1px solid #ddd; padding-bottom: 5px;">VIX Analysis</h3>
                    <ul style="list-style-type: none; padding-left: 0;">
                        <li style="padding: 5px 0; border-bottom: 1px solid #eee;">Current VIX: <strong>{vix.get('current_vix', 0):.2f}</strong></li>
                        <li style="padding: 5px 0; border-bottom: 1px solid #eee;">Status: <strong>{vix.get('status', 'Unknown')}</strong></li>
                        <li style="padding: 5px 0; border-bottom: 1px solid #eee;">Fear Level: <strong>{vix.get('fear_level', 'Unknown')}</strong></li>
                    </ul>
                    <p style="font-size: 0.9em; background-color: #f8f9fa; padding: 10px; border-radius: 4px;">
                        <strong>Impact:</strong> {vix.get('explanation', '')}
                    </p>
                </div>
            </div>
            
            <div style="background-color: #e9ecef; padding: 15px; border-left: 4px solid #007bff; margin-bottom: 20px;">
                <h3 style="margin-top: 0; color: #007bff;">Strategic Recommendation</h3>
                <p><strong>Proposed Exposure:</strong> {env.get('exposure_guidance', 'N/A')}</p>
                <p><strong>Position Size:</strong> {env.get('recommendation', 'N/A')}</p>
                <p style="font-size: 0.9em; margin-top: 10px;"><em>Use this guidance to adjust portfolio risk. In choppy markets, reduce size and take profits quickly. In bull markets, pyramid into strength.</em></p>
            </div>
            
            <p style="font-size: 0.8em; color: #999; text-align: center; margin-top: 30px;">
                Automated Report | QuantZ Trading Lab
            </p>
        </div>
    </body>
    </html>
    """
    return html


def send_email(subject, body_text, body_html=None):
    """Send email via SES"""
    try:
        message = {
            'Subject': {'Data': subject, 'Charset': 'UTF-8'},
            'Body': {
                'Text': {'Data': body_text, 'Charset': 'UTF-8'}
            }
        }
        
        if body_html:
            message['Body']['Html'] = {'Data': body_html, 'Charset': 'UTF-8'}
            
        ses_client.send_email(
            Source=FROM_EMAIL,
            Destination={'ToAddresses': [TO_EMAIL]},
            Message=message
        )
        logger.info(f"Email sent successfully to {TO_EMAIL}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)
        raise
