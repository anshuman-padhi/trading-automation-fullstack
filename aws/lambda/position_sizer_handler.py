"""
AWS Lambda Handler: Position Sizing
Triggered: On-demand via API Gateway
Purpose: Calculate position size based on risk parameters
"""
import json
import os
import logging
from datetime import datetime
import boto3

# Import core module
import sys
from dataclasses import asdict

# Import core module
sys.path.insert(0, '/opt/python')
from src.modules.position_sizer import PositionSizer, PositionInput

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')

# Environment variables
S3_BUCKET = os.getenv('S3_BUCKET', 'trading-automation-data')
DEFAULT_ACCOUNT_SIZE = float(os.getenv('ACCOUNT_SIZE', '100000'))


def lambda_handler(event, context):
    """
    Main Lambda handler for position sizing

    Expected event body:
    {
        "symbol": "AAPL",
        "entry_price": 150.00,
        "stop_loss": 145.00,
        "market_environment": "B",
        "setup_grade": "A",
        "edge_count": 5,
        "account_size": 100000
    }

    Returns:
        dict: Position sizing calculation results
    """
    logger.info(f"Position Sizer Lambda triggered at {datetime.utcnow().isoformat()}Z")

    try:
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event

        # Extract parameters
        symbol = body.get('symbol')
        entry_price = float(body.get('entry_price'))
        stop_loss = float(body.get('stop_loss'))
        market_env = body.get('market_environment', 'B')
        setup_grade = body.get('setup_grade', 'B')  # Note: setup_grade currently unused in PositionSizer logic but kept for consistency
        edge_count = int(body.get('edge_count', 3))
        account_size = float(body.get('account_size', DEFAULT_ACCOUNT_SIZE))

        logger.info(f"Calculating position size for {symbol}")
        logger.info(f"Entry: ${entry_price}, Stop: ${stop_loss}, Env: {market_env}, Account: ${account_size:,.2f}")

        # Initialize position sizer
        sizer = PositionSizer()

        # Create input object
        position_input = PositionInput(
            account_size=account_size,
            entry_price=entry_price,
            stop_loss_price=stop_loss,
            market_environment=market_env,
            num_edges=edge_count
        )

        # Calculate position
        position_output = sizer.size_position(position_input)
        
        # Convert dataclass to dict
        result = asdict(position_output)

        # Add metadata
        result['symbol'] = symbol
        result['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        result['account_size'] = account_size

        # Save to S3 for audit trail
        s3_key = f"position_sizing/{datetime.utcnow().strftime('%Y/%m/%d')}/{symbol}_{datetime.utcnow().strftime('%H%M%S')}.json"

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(result, indent=2),
            ContentType='application/json'
        )

        logger.info(f"Position sizing calculated: {result['shares']} shares, ${result['position_size']:,.2f}")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }

    except Exception as e:
        logger.error(f"Error calculating position size: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
