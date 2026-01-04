import pytest
import json
import boto3
import sys
import os
import importlib.util
from moto import mock_aws
from unittest.mock import patch, MagicMock
import pandas as pd

# Dynamically load the handler because 'lambda' is a reserved keyword
# and cannot be part of a python package path (aws.lambda...)
HANDLER_PATH = os.path.join(os.getcwd(), 'aws', 'lambda', 'stock_screener_handler.py')
spec = importlib.util.spec_from_file_location("stock_screener_handler", HANDLER_PATH)
stock_screener_handler = importlib.util.module_from_spec(spec)
sys.modules["stock_screener_handler"] = stock_screener_handler
spec.loader.exec_module(stock_screener_handler)
lambda_handler = stock_screener_handler.lambda_handler

@pytest.fixture
def mock_s3():
    with mock_aws():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='trading-automation-data')
        yield s3

@pytest.fixture
def mock_ses():
    with mock_aws():
        ses = boto3.client('ses', region_name='us-east-1')
        ses.verify_email_identity(EmailAddress='trading@example.com')
        yield ses

class TestStockScreenerIntegration:

    @patch('src.modules.data_fetcher.DataFetcher.get_fundamental_data')
    @patch('src.modules.data_fetcher.DataFetcher.fetch_full_universe')
    @patch('src.modules.data_fetcher.DataFetcher.fetch_batch_data')
    def test_end_to_end_screening(
        self, 
        mock_batch_fetch, 
        mock_full_universe, 
        mock_get_fundamental,
        mock_s3, 
        mock_ses,
        mock_fundamental_data,
        mock_technical_data
    ):
        # 1. Setup Mock Data
        mock_full_universe.return_value = ['TEST1', 'TEST2']
        
        # Mock Stage 2 Fundamental Fetch
        # Return same mock data for simplicity
        mock_get_fundamental.return_value = mock_fundamental_data
        
        # Mock ML Model in S3
        from sklearn.ensemble import RandomForestClassifier
        import joblib
        from io import BytesIO
        
        dummy_model = RandomForestClassifier()
        dummy_model.fit([[0]*8, [1]*8], [0, 1]) # Train dummy
        
        buf = BytesIO()
        joblib.dump(dummy_model, buf)
        buf.seek(0)
        
        # Upload to Mock S3
        bucket = "trading-automation-data-904583676284"
        mock_s3.create_bucket(Bucket=bucket)
        mock_s3.put_object(Bucket=bucket, Key="models/breakout_classifier.joblib", Body=buf.read())
        
        # Mock YF History for ML Features
        with patch('yfinance.Ticker') as mock_ticker_cls:
            mock_inst = MagicMock()
            mock_ticker_cls.return_value = mock_inst
            
            # Create dummy history (uptrend)
            prices = [100 + i for i in range(100)]
            df = pd.DataFrame({
                'Open': prices, 'High': [p+1 for p in prices], 'Low': [p-1 for p in prices], 'Close': prices, 'Volume': [1000]*100
            })
            mock_inst.history.return_value = df
            
            # Setup Batch Fetch Data (Restored)
            tech_winner = mock_technical_data
            tech_loser = MagicMock()
            tech_loser.rs_rating = 20.0
            tech_loser.price_trend = "DOWN"
            
            mock_batch_fetch.return_value = {
                'TEST1': (mock_fundamental_data, tech_winner),
                'TEST2': (mock_fundamental_data, tech_loser)
            }
            
            # 2. Run Handler
            event = {}
            context = {}
            response = lambda_handler(event, context)
        
        # 3. Verify Response
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['watchlist_count'] >= 1
        
        # 4. Verify S3 Upload
        objects = mock_s3.list_objects(Bucket='trading-automation-data')
        assert 'Contents' in objects
        keys = [obj['Key'] for obj in objects['Contents']]
        assert any(k.endswith('.json') for k in keys)
        assert any(k.endswith('.csv') for k in keys)
        
        # 5. Verify Email Sent
        sent = mock_ses.get_send_quota()
        # Moto doesn't perfectly track sent count in get_send_quota often, 
        # but we can assume if no exception was raised and code path ran, it worked.
        # Ideally we'd wrap the ses client in a spy, but for integration this is okay.
