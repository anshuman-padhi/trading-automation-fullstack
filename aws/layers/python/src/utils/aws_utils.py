"""
AWS utilities for interacting with AWS services
"""
import boto3
import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class S3Manager:
    """Manage S3 bucket operations"""
    
    def __init__(self, region: str = "us-east-1"):
        """
        Initialize S3 Manager
        
        Args:
            region: AWS region
        """
        self.s3_client = boto3.client('s3', region_name=region)
        self.region = region
        logger.info(f"Initialized S3Manager for region: {region}")
    
    def upload_json(
        self, 
        bucket: str, 
        key: str, 
        data: Dict[str, Any]
    ) -> bool:
        """
        Upload JSON data to S3
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            data: Dictionary to upload
        
        Returns:
            True if successful, False otherwise
        """
        try:
            json_str = json.dumps(data, indent=2, default=str)
            self.s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=json_str,
                ContentType='application/json'
            )
            logger.info(f"Uploaded to S3: s3://{bucket}/{key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            return False
    
    def download_json(self, bucket: str, key: str) -> Optional[Dict]:
        """
        Download JSON data from S3
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
        
        Returns:
            Dictionary or None if failed
        """
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            data = json.loads(response['Body'].read().decode('utf-8'))
            logger.info(f"Downloaded from S3: s3://{bucket}/{key}")
            return data
        except Exception as e:
            logger.error(f"Failed to download from S3: {e}")
            return None


class SESManager:
    """Manage SES email operations"""
    
    def __init__(self, region: str = "us-east-1", sender: str = "noreply@example.com"):
        """
        Initialize SES Manager
        
        Args:
            region: AWS region
            sender: Sender email address
        """
        self.ses_client = boto3.client('ses', region_name=region)
        self.sender = sender
        self.region = region
        logger.info(f"Initialized SESManager with sender: {sender}")
    
    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> bool:
        """
        Send email via SES
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            body: Email body
            is_html: Whether body is HTML
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ses_client.send_email(
                Source=self.sender,
                Destination={'ToAddresses': [recipient]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {
                        'Html' if is_html else 'Text': {'Data': body}
                    }
                }
            )
            logger.info(f"Email sent to {recipient}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


class EventBridgeManager:
    """Manage EventBridge scheduling"""
    
    def __init__(self, region: str = "us-east-1"):
        """Initialize EventBridge Manager"""
        self.events_client = boto3.client('events', region_name=region)
        self.region = region
        logger.info(f"Initialized EventBridgeManager for region: {region}")
    
    def put_rule(
        self,
        rule_name: str,
        schedule_expression: str,
        description: str = "",
        enabled: bool = True
    ) -> bool:
        """
        Create or update EventBridge rule
        
        Args:
            rule_name: Rule name
            schedule_expression: Cron or rate expression
            description: Rule description
            enabled: Whether rule is enabled
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.events_client.put_rule(
                Name=rule_name,
                ScheduleExpression=schedule_expression,
                State='ENABLED' if enabled else 'DISABLED',
                Description=description
            )
            logger.info(f"Created EventBridge rule: {rule_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create rule: {e}")
            return False
