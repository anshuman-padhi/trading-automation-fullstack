"""
Configuration settings for trading automation system
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Detect if running in Lambda
if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    DATA_DIR = Path("/tmp/data")
    LOGS_DIR = Path("/tmp/logs")
else:
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_DATA_BUCKET = os.getenv("S3_DATA_BUCKET", "trading-automation-data")
S3_BACKUP_BUCKET = os.getenv("S3_BACKUP_BUCKET", "trading-automation-backups")

# Email Configuration
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "your-email@example.com")
SES_SENDER_EMAIL = os.getenv("SES_SENDER_EMAIL", "noreply@example.com")

# Trading Configuration
MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "0.10"))
MAX_POSITIONS = int(os.getenv("MAX_POSITIONS", "5"))
DEFAULT_RISK_PERCENT = float(os.getenv("DEFAULT_RISK_PERCENT", "0.01"))

# Market Analysis Configuration
MARKET_INDEX = "QQQ"  # Nasdaq ETF
SHORT_TERM_MA = 10    # 10-day SMA
INTERMEDIATE_MA = 21   # 21-day EMA
LONG_TERM_MA = 200    # 200-day SMA

# Feature Flags
ENABLE_PAPER_TRADING = os.getenv("ENABLE_PAPER_TRADING", "true").lower() == "true"
ENABLE_EMAIL_ALERTS = os.getenv("ENABLE_EMAIL_ALERTS", "true").lower() == "true"
ENABLE_REAL_TRADING = os.getenv("ENABLE_REAL_TRADING", "false").lower() == "true"
