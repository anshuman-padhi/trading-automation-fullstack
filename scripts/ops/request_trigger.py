
import sys
import os
import logging
from unittest.mock import MagicMock, patch

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Add project root to path so Handler can find src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Also add 'src' directly if handler expects it in /opt/python/src... 
# Handler does: sys.path.insert(0, '/opt/python') then 'from src.modules...'
# So if we map '/opt/python' to project_root, it works.
sys.path.insert(0, project_root)

# Mock Environment Variables
os.environ['S3_BUCKET'] = 'trading-automation-data-904583676284'
os.environ['FROM_EMAIL'] = 'test@example.com'
os.environ['TO_EMAIL'] = 'test@example.com'
os.environ['STOCK_UNIVERSE'] = 'SP500'

# Mock SES to capture Email
class MockSES:
    def send_email(self, Source, Destination, Message):
        print("\n" + "="*50)
        print("📧 EMAIL CAPTURED (MOCKED)")
        print(f"To: {Destination['ToAddresses']}")
        print(f"Subject: {Message['Subject']['Data']}")
        print("-" * 50)
        print(Message['Body']['Text']['Data'])
        print("="*50 + "\n")

# Import Handler (Using importlib to handle path issues if needed, or just standard import)
try:
    # We need to mock boto3.client('ses') inside the handler module BEFORE importing it if it initializes at top level.
    # The handler initializes clients at top level: s3_client = boto3.client('s3')
    
    with patch('boto3.client') as mock_client:
        def side_effect(service_name, **kwargs):
            if service_name == 'ses':
                return MockSES()
            # Return real S3 client if possible, or Mock if we want offline.
            # We want REAL S3 to download the model! (Unless we mock model download too).
            # If user has AWS creds, real S3 is better to verify Model Download works.
            if service_name == 's3':
                # Return REAL boto3 client
                import boto3 as real_boto3
                return real_boto3.Session().client('s3')
            return MagicMock()
            
        mock_client.side_effect = side_effect
        
        # Now import handler dynamically (to avoid 'lambda' keyword issue)
        import importlib.util
        handler_path = os.path.join(project_root, 'aws', 'lambda', 'stock_screener_handler.py')
        spec = importlib.util.spec_from_file_location("stock_screener_handler", handler_path)
        stock_screener_handler = importlib.util.module_from_spec(spec)
        sys.modules["stock_screener_handler"] = stock_screener_handler
        spec.loader.exec_module(stock_screener_handler)
        lambda_handler = stock_screener_handler.lambda_handler
        
        print("🚀 Triggering Manual Screening...")
        
        # Override Universe to smaller set for Speed?
        # The handler calls fetcher.fetch_full_universe().
        # We can patch DataFetcher.fetch_full_universe to return top 5 stocks for speed test.
        with patch('src.modules.data_fetcher.DataFetcher.fetch_full_universe') as mock_universe:
            # Let's pick 5 high volume stocks to ensure we get data
            mock_universe.return_value = ['NVDA', 'AMD', 'META', 'TSLA', 'AAPL', 'MSFT', 'AMZN'] 
            
            response = lambda_handler({}, {})
            
            print(f"Status Code: {response['statusCode']}")
            print(f"Response: {response['body']}")

except Exception as e:
    print(f"Execution Error: {e}")
    import traceback
    traceback.print_exc()
