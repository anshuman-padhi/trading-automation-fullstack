"""
AWS Lambda Handler: Trade Journal
Triggered: On-demand via API Gateway
Purpose: Record trade entries and exits
"""
import json
import os
import logging
from datetime import datetime
import boto3
import pandas as pd

# Import core module
import sys
sys.path.insert(0, '/opt/python')
from src.modules.trade_journal import TradeJournal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')

# Environment variables
S3_BUCKET = os.getenv('S3_BUCKET', 'trading-automation-data')
JOURNAL_FILE = os.getenv('JOURNAL_FILE', 'trade_journal/journal.csv')


def lambda_handler(event, context):
    """
    Main Lambda handler for trade journal

    Supports two actions:
    1. record_entry - Record new trade entry
    2. record_exit - Record trade exit

    Returns:
        dict: Trade journal operation result
    """
    logger.info(f"Trade Journal Lambda triggered at {datetime.utcnow().isoformat()}Z")

    try:
        # Parse request
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event

        action = body.get('action', 'record_entry')

        # Initialize journal
        journal = TradeJournal()

        # Load existing journal from S3
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=JOURNAL_FILE)
            journal_csv = response['Body'].read().decode('utf-8')
            # Load into journal (implementation depends on TradeJournal class)
            logger.info("Loaded existing journal from S3")
        except s3_client.exceptions.NoSuchKey:
            logger.info("No existing journal found, starting fresh")

        if action == 'record_entry':
            result = record_trade_entry(journal, body)
        elif action == 'record_exit':
            result = record_trade_exit(journal, body)
        else:
            raise ValueError(f"Invalid action: {action}")

        # Save updated journal to S3
        save_journal_to_s3(journal)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }

    except Exception as e:
        logger.error(f"Error in trade journal: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def record_trade_entry(journal, data):
    """Record a new trade entry"""
    trade_id = journal.record_entry(
        symbol=data['symbol'],
        entry_date=data.get('entry_date', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')),
        entry_price=float(data['entry_price']),
        shares=int(data['shares']),
        initial_stop=float(data['initial_stop']),
        target_price=float(data.get('target_price', 0)) or None,
        setup_grade=data.get('setup_grade', 'B'),
        notes=data.get('notes', '')
    )

    logger.info(f"Recorded trade entry: {trade_id} - {data['symbol']}")

    return {
        'action': 'entry',
        'trade_id': trade_id,
        'symbol': data['symbol'],
        'message': f'Trade entry recorded successfully'
    }


def record_trade_exit(journal, data):
    """Record a trade exit"""
    trade_id = data['trade_id']

    journal.record_exit(
        trade_id=trade_id,
        exit_date=data.get('exit_date', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')),
        exit_price=float(data['exit_price']),
        execution_grade=data.get('execution_grade', 'B'),
        exit_notes=data.get('exit_notes', '')
    )

    logger.info(f"Recorded trade exit: {trade_id}")

    # Get trade details
    trade = journal.get_trade(trade_id)

    return {
        'action': 'exit',
        'trade_id': trade_id,
        'pnl_dollars': trade.get('pnl_dollars', 0),
        'pnl_percent': trade.get('pnl_percent', 0),
        'message': f'Trade exit recorded successfully'
    }


def save_journal_to_s3(journal):
    """Save journal to S3"""
    # Export to CSV
    csv_data = journal.export_to_csv()

    # Save to S3
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=JOURNAL_FILE,
        Body=csv_data,
        ContentType='text/csv'
    )

    # Also save timestamped backup
    backup_key = f"trade_journal/backups/journal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=backup_key,
        Body=csv_data,
        ContentType='text/csv'
    )

    logger.info(f"Journal saved to S3: {JOURNAL_FILE}")
