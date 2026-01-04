# PYTHON_AWS_IMPLEMENTATION_GUIDE.md
## Local Mac Development → AWS Lambda + S3 Production
**Version: 1.0 | December 31, 2025**
**Estimated Read Time: 3 hours | Implementation Time: 20-40 hours**

---

## Architecture Overview

```
YOUR TRADING AUTOMATION ARCHITECTURE
(Mac Development → AWS Lambda Production)

┌─────────────────────────────────────────────────────────┐
│                    DEVELOPMENT PHASE                     │
│                  (Your Mac - Weeks 1-2)                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  LOCAL MAC SETUP                                 │  │
│  │  ├─ Python 3.9+ with virtual environment        │  │
│  │  ├─ Code editor: VSCode + Python extensions     │  │
│  │  ├─ Git: Version control (prepare for AWS)      │  │
│  │  ├─ Local CSV storage (data/$SYMBOL.csv)        │  │
│  │  ├─ SQLite for testing (optional, local.db)     │  │
│  │  └─ Cron scheduling (test locally first)        │  │
│  └──────────────────────────────────────────────────┘  │
│                           ↓                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  CODE DEVELOPMENT (6 Modules)                    │  │
│  │  ├─ market_analysis.py (environment classifier) │  │
│  │  ├─ stock_screener.py (watchlist generator)     │  │
│  │  ├─ position_sizer.py (risk calculator)         │  │
│  │  ├─ trade_journal.py (auto-journaling)          │  │
│  │  ├─ performance_dashboard.py (metrics)          │  │
│  │  └─ alerts_monitor.py (notifications)           │  │
│  └──────────────────────────────────────────────────┘  │
│                           ↓                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  LOCAL TESTING                                   │  │
│  │  ├─ Unit tests (pytest framework)                │  │
│  │  ├─ Integration tests (end-to-end)               │  │
│  │  ├─ Data validation (CSV output)                 │  │
│  │  └─ Calculation verification (manual vs auto)    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                 PRODUCTION PHASE                         │
│            (AWS - After Week 2+ Validation)              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  AWS S3 SETUP                                    │  │
│  │  ├─ Bucket: trading-automation-{account-id}     │  │
│  │  ├─ Folder structure:                           │  │
│  │  │  └─ data/                                    │  │
│  │  │     ├─ watchlist/ (daily updates)            │  │
│  │  │     ├─ trades/ (journal entries)             │  │
│  │  │     ├─ metrics/ (performance data)           │  │
│  │  │     └─ raw/ (API responses, archive)         │  │
│  │  └─ Versioning: Enabled (rollback capability)  │  │
│  └──────────────────────────────────────────────────┘  │
│                           ↓                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  AWS LAMBDA FUNCTIONS                            │  │
│  │  ├─ lambda_market_analysis (Sunday 6 PM UTC)   │  │
│  │  ├─ lambda_stock_screening (Daily 4:15 PM UTC) │  │
│  │  ├─ lambda_position_sizing (On-demand)          │  │
│  │  ├─ lambda_trade_journal (On-demand)            │  │
│  │  ├─ lambda_dashboard_update (After each trade)  │  │
│  │  └─ lambda_alerts_monitor (Every 5 minutes)     │  │
│  └──────────────────────────────────────────────────┘  │
│                           ↓                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  AWS EVENTBRIDGE (SCHEDULING)                    │  │
│  │  ├─ cron(0 18 ? * SUN *) → market_analysis     │  │
│  │  ├─ cron(0 21 ? * * *) → stock_screening      │  │
│  │  └─ rate(5 minutes) → alerts_monitor           │  │
│  └──────────────────────────────────────────────────┘  │
│                           ↓                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  AWS SNS / SES (NOTIFICATIONS)                   │  │
│  │  ├─ Email alerts (SES) - free tier 62k/month   │  │
│  │  ├─ SMS alerts (SNS) - optional, $0.01/SMS     │  │
│  │  └─ Lambda error notifications                  │  │
│  └──────────────────────────────────────────────────┘  │
│                           ↓                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  AWS CLOUDWATCH (MONITORING)                     │  │
│  │  ├─ Function execution logs                      │  │
│  │  ├─ Performance metrics                          │  │
│  │  ├─ Error tracking & alerts                      │  │
│  │  └─ Cost monitoring                              │  │
│  └──────────────────────────────────────────────────┘  │
│                           ↓                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  AWS OPTIONAL: RDS / DYNAMODB (If Needed)       │  │
│  │  ├─ PostgreSQL RDS (relational queries)         │  │
│  │  ├─ DynamoDB (fast key-value access)            │  │
│  │  └─ Decide after CSV + S3 proves reliable       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## PHASE 1: LOCAL MAC DEVELOPMENT (Weeks 1-2)

### Step 1: Mac Environment Setup

**1.1 Install Python & Virtual Environment**

```bash
# Check current Python version
python3 --version  # Should be 3.8+

# Navigate to your projects directory
cd ~/projects/trading-automation

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Verify activation (should show: (venv) $)
```

**1.2 Create Project Structure**

```bash
# Create folder structure
mkdir -p trading-automation/{
  src/{modules,utils,tests},
  data/{raw,processed,watchlist,trades,metrics},
  config,
  logs,
  scripts,
  aws/{lambda,terraform}
}

# Navigate to project
cd trading-automation

# Create essential files
touch .gitignore requirements.txt .env config/settings.py

# Initialize git (for version control)
git init
```

**1.3 Create .gitignore**

```bash
cat > .gitignore << 'EOF'
# Environment
venv/
.env
*.pyc
__pycache__/

# IDE
.vscode/
.idea/
*.swp

# Data (keep local, don't commit)
data/
*.csv
*.db
logs/

# AWS credentials (NEVER commit)
aws_credentials.json
.aws/credentials

# OS
.DS_Store
*.log
EOF
```

**1.4 Install Required Libraries**

```bash
# Create requirements.txt
cat > requirements.txt << 'EOF'
# Data Processing
pandas==2.0.3
numpy==1.24.3

# API & Data Sources
yfinance==0.2.32
alpha-vantage==2.3.1
requests==2.31.0

# AWS SDK
boto3==1.28.52
botocore==1.31.52

# Testing
pytest==7.4.0
pytest-cov==4.1.0

# Email/Notifications
python-dotenv==1.0.0
boto3-stubs[sns,ses,s3,events]==1.28.52

# Logging & Monitoring
python-json-logger==2.0.7

# Development
black==23.9.1
flake8==6.1.0
mypy==1.5.1
EOF

# Install all dependencies
pip install -r requirements.txt
```

**1.5 Create Configuration File**

```python
# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    
    # Data sources
    DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
    RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
    
    # API keys
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
    
    # Trading parameters (from your system)
    ENVIRONMENTS = {
        'A': {'base': 0.10, 'risk': 0.005, 'heat_limit': 0.025},
        'B': {'base': 0.08, 'risk': 0.004, 'heat_limit': 0.020},
        'C': {'base': 0.05, 'risk': 0.0025, 'heat_limit': 0.010},
        'D': {'base': 0.03, 'risk': 0.002, 'heat_limit': 0.015}
    }
    
    # Stock screening thresholds
    MIN_MARKET_CAP = 1_000_000_000  # $1B
    MIN_REVENUE_GROWTH = 0.15  # 15%
    MIN_EPS_GROWTH = 0.15  # 15%
    MIN_RS_RATING = 80
    MIN_DAILY_VOLUME = 500_000
    
    # AWS Configuration (for local testing)
    AWS_REGION = 'us-east-1'
    S3_BUCKET = os.getenv('S3_BUCKET', 'trading-automation-dev')
    
    # Notifications
    NOTIFY_EMAIL = os.getenv('NOTIFY_EMAIL')
    NOTIFY_SMS = os.getenv('NOTIFY_SMS', None)

class DevelopmentConfig(Config):
    """Development configuration (local Mac)"""
    DEBUG = True
    USE_LOCAL_CSV = True
    USE_LOCAL_DB = True

class ProductionConfig(Config):
    """Production configuration (AWS Lambda)"""
    DEBUG = False
    USE_LOCAL_CSV = False
    USE_LOCAL_DB = False
    USE_S3 = True
    USE_RDS = False  # Set to True if migrating to PostgreSQL

# Load appropriate config
ENV = os.getenv('ENVIRONMENT', 'development')
config = DevelopmentConfig() if ENV == 'development' else ProductionConfig()
```

**1.6 Create .env File (LOCAL ONLY - Never commit)**

```bash
cat > .env << 'EOF'
# Environment
ENVIRONMENT=development

# API Keys
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here

# AWS (Local development - use minimal credentials)
AWS_REGION=us-east-1
S3_BUCKET=trading-automation-dev

# Notifications
NOTIFY_EMAIL=your.email@gmail.com
NOTIFY_SMS=+1234567890  # Optional

# Trading Account (for future broker API integration)
BROKER_API_KEY=your_broker_api_key_here
ACCOUNT_ID=your_account_id_here
EOF

# Make sure .env is in .gitignore (don't commit credentials!)
echo ".env" >> .gitignore
```

---

### Step 2: Create Module 1 - Market Analysis (Local)

**File: src/modules/market_analysis.py**

```python
"""
Market Analysis Module
Classifies market environment (A/B/C/D) based on technical indicators
Runs weekly on Sunday 6 PM
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import json
import os
from config.settings import config

class MarketAnalyzer:
    """Analyzes market environment and provides sizing recommendations"""
    
    def __init__(self):
        self.analysis_date = datetime.now()
        self.results = {}
    
    def fetch_market_data(self):
        """Fetch latest market data from Yahoo Finance"""
        try:
            print(f"[{self.analysis_date}] Fetching market data...")
            
            # Fetch SPY (S&P 500)
            spy_data = yf.download('SPY', period='250d', progress=False)
            spy_50sma = spy_data['Close'].rolling(50).mean().iloc[-1]
            spy_200sma = spy_data['Close'].rolling(200).mean().iloc[-1]
            spy_price = spy_data['Close'].iloc[-1]
            
            # Fetch QQQ (Nasdaq 100)
            qqq_data = yf.download('QQQ', period='250d', progress=False)
            qqq_50sma = qqq_data['Close'].rolling(50).mean().iloc[-1]
            qqq_200sma = qqq_data['Close'].rolling(200).mean().iloc[-1]
            qqq_price = qqq_data['Close'].iloc[-1]
            
            # Fetch VIX
            vix_data = yf.download('^VIX', period='5d', progress=False)
            vix = vix_data['Close'].iloc[-1]
            
            self.results['spy'] = {
                'price': round(spy_price, 2),
                'sma_50': round(spy_50sma, 2),
                'sma_200': round(spy_200sma, 2),
                'above_50': spy_price > spy_50sma,
                'above_200': spy_price > spy_200sma
            }
            
            self.results['qqq'] = {
                'price': round(qqq_price, 2),
                'sma_50': round(qqq_50sma, 2),
                'sma_200': round(qqq_200sma, 2),
                'above_50': qqq_price > qqq_50sma,
                'above_200': qqq_price > qqq_200sma
            }
            
            self.results['vix'] = round(vix, 2)
            
            # Calculate breadth (simplified: using top tech stocks)
            breadth_pct = self._calculate_breadth()
            self.results['breadth_pct'] = breadth_pct
            
            print("✓ Market data fetched successfully")
            return True
            
        except Exception as e:
            print(f"✗ Error fetching market data: {e}")
            return False
    
    def _calculate_breadth(self):
        """Calculate breadth % (simplified version)"""
        tech_stocks = ['MSFT', 'AAPL', 'NVDA', 'TSLA', 'GOOGL', 
                       'META', 'AMZN', 'NFLX', 'AMD', 'INTC']
        above_sma50 = 0
        
        for stock in tech_stocks:
            try:
                data = yf.download(stock, period='250d', progress=False)
                if data['Close'].iloc[-1] > data['Close'].rolling(50).mean().iloc[-1]:
                    above_sma50 += 1
            except:
                pass
        
        return round((above_sma50 / len(tech_stocks)) * 100, 1)
    
    def classify_environment(self):
        """Classify market as A/B/C/D"""
        
        spy_up = self.results['spy']['above_50'] and self.results['spy']['above_200']
        qqq_up = self.results['qqq']['above_50'] and self.results['qqq']['above_200']
        breadth = self.results['breadth_pct']
        vix = self.results['vix']
        
        # Environment A: Confirmed uptrend
        if spy_up and qqq_up and breadth >= 70 and vix <= 25:
            env = 'A'
        # Environment B: Uptrend with caution
        elif self.results['spy']['above_50'] and self.results['qqq']['above_50'] and breadth >= 50 and vix <= 30:
            env = 'B'
        # Environment C: Choppy/sideways
        elif breadth >= 30 and vix <= 35:
            env = 'C'
        # Environment D: Downtrend
        else:
            env = 'D'
        
        self.results['environment'] = env
        self.results['sizing_params'] = config.ENVIRONMENTS[env]
        
        return env
    
    def save_to_csv(self):
        """Save analysis to CSV"""
        filepath = os.path.join(config.DATA_DIR, 'market_analysis.csv')
        
        # Flatten results for CSV
        row = {
            'date': self.analysis_date.isoformat(),
            'spy_price': self.results['spy']['price'],
            'spy_50sma': self.results['spy']['sma_50'],
            'spy_200sma': self.results['spy']['sma_200'],
            'qqq_price': self.results['qqq']['price'],
            'qqq_50sma': self.results['qqq']['sma_50'],
            'qqq_200sma': self.results['qqq']['sma_200'],
            'breadth_pct': self.results['breadth_pct'],
            'vix': self.results['vix'],
            'environment': self.results['environment'],
            'base_size': self.results['sizing_params']['base'],
            'risk_pct': self.results['sizing_params']['risk'],
            'heat_limit': self.results['sizing_params']['heat_limit']
        }
        
        # Append to CSV
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        else:
            df = pd.DataFrame([row])
        
        df.to_csv(filepath, index=False)
        print(f"✓ Analysis saved to {filepath}")
    
    def generate_report(self):
        """Generate human-readable report"""
        report = f"""
MARKET ENVIRONMENT ANALYSIS
Generated: {self.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}

═══════════════════════════════════════════════
PRICE & TREND ANALYSIS
═══════════════════════════════════════════════

SPY:
  Price: ${self.results['spy']['price']:.2f}
  50 SMA: ${self.results['spy']['sma_50']:.2f} - {'ABOVE ✓' if self.results['spy']['above_50'] else 'BELOW ✗'}
  200 SMA: ${self.results['spy']['sma_200']:.2f} - {'ABOVE ✓' if self.results['spy']['above_200'] else 'BELOW ✗'}

QQQ:
  Price: ${self.results['qqq']['price']:.2f}
  50 SMA: ${self.results['qqq']['sma_50']:.2f} - {'ABOVE ✓' if self.results['qqq']['above_50'] else 'ABOVE ✓'}
  200 SMA: ${self.results['qqq']['sma_200']:.2f} - {'ABOVE ✓' if self.results['qqq']['above_200'] else 'BELOW ✗'}

VOLATILITY & BREADTH:
  VIX: {self.results['vix']:.2f}
  Breadth: {self.results['breadth_pct']:.0f}% above 50 SMA

═══════════════════════════════════════════════
CLASSIFICATION & RECOMMENDATIONS
═══════════════════════════════════════════════

ENVIRONMENT: {self.results['environment']}

Base Position Size: {self.results['sizing_params']['base']*100:.0f}%
Risk Per Trade: {self.results['sizing_params']['risk']*100:.2f}%
Portfolio Heat Limit: {self.results['sizing_params']['heat_limit']*100:.2f}%

RECOMMENDATION:
"""
        if self.results['environment'] == 'A':
            report += "AGGRESSIVE - Trade 3-5 times weekly"
        elif self.results['environment'] == 'B':
            report += "NORMAL - Trade 2-3 times weekly"
        elif self.results['environment'] == 'C':
            report += "DEFENSIVE - Trade max 1 time weekly"
        else:
            report += "AVOID TRADING - Focus on capital preservation"
        
        return report
    
    def run(self):
        """Execute full market analysis"""
        print("\n" + "="*60)
        print("MARKET ANALYSIS MODULE")
        print("="*60 + "\n")
        
        if not self.fetch_market_data():
            return False
        
        self.classify_environment()
        self.save_to_csv()
        print("\n" + self.generate_report())
        
        return True

# Main execution
if __name__ == "__main__":
    analyzer = MarketAnalyzer()
    analyzer.run()
```

**Run locally to test:**
```bash
cd ~/projects/trading-automation
source venv/bin/activate
python src/modules/market_analysis.py
```

---

### Step 3: Create Module 3 - Position Sizing (Local)

**File: src/modules/position_sizer.py**

```python
"""
Position Sizing Module
Calculates trade-ready position sizes based on risk management rules
"""

import os
from config.settings import config

class PositionSizer:
    """Calculates position size with full risk verification"""
    
    def __init__(self, account_equity, environment='A'):
        self.account = account_equity
        self.environment = environment
        self.params = config.ENVIRONMENTS[environment]
    
    def calculate(self, entry_price, stop_price, edges=4, open_heat=0):
        """
        Calculate position size
        
        Args:
            entry_price: Entry price in $
            stop_price: Stop loss price in $
            edges: Number of edges (3-10)
            open_heat: Current portfolio heat in $
        
        Returns:
            dict with position details
        """
        
        # Validate inputs
        if entry_price <= 0 or stop_price <= 0:
            raise ValueError("Prices must be positive")
        if entry_price <= stop_price:
            raise ValueError("Entry must be above stop")
        if edges < 3 or edges > 10:
            raise ValueError("Edges must be 3-10")
        
        # Step 1: Base size by environment
        base_size = self.params['base']
        
        # Step 2: Adjust for edges
        edge_multiplier = {
            3: 0.50, 4: 1.00, 5: 1.10, 6: 1.20, 7: 1.30,
            8: 1.35, 9: 1.40, 10: 1.45
        }
        adjusted_size = base_size * edge_multiplier.get(edges, 1.0)
        
        # Step 3: Position size formula (dollars)
        position_value = self.account * adjusted_size
        
        # Step 4: Risk-based verification
        risk_dollars = self.account * self.params['risk']
        stop_distance = entry_price - stop_price
        max_shares_by_risk = risk_dollars / stop_distance
        risk_based_position = max_shares_by_risk * entry_price
        
        # Use smaller of the two
        final_position = min(position_value, risk_based_position)
        shares = int(final_position / entry_price)
        
        # Step 5: Heat limit check
        position_heat = shares * stop_distance
        total_heat = open_heat + position_heat
        heat_limit = self.account * self.params['heat_limit']
        
        heat_status = 'OK' if total_heat <= heat_limit else 'EXCEEDED'
        
        # Calculate profit targets
        stage1 = entry_price * 1.10  # +10%
        stage2 = entry_price * 1.20  # +20%
        stage3 = entry_price * 1.75  # +75%
        
        return {
            'entry_price': entry_price,
            'stop_price': stop_price,
            'shares': shares,
            'position_value': round(final_position, 2),
            'risk_dollars': round(position_heat, 2),
            'risk_pct': round(position_heat / self.account * 100, 3),
            'stage1_target': round(stage1, 2),
            'stage2_target': round(stage2, 2),
            'stage3_target': round(stage3, 2),
            'portfolio_heat_after': round(total_heat, 2),
            'heat_limit': round(heat_limit, 2),
            'heat_status': heat_status,
            'edges': edges,
            'environment': self.environment,
            'verification_passed': heat_status == 'OK'
        }
    
    def print_result(self, result):
        """Pretty print position sizing result"""
        print("\n" + "="*60)
        print("POSITION SIZING CALCULATOR")
        print("="*60)
        print(f"\nEntry Price: ${result['entry_price']:.2f}")
        print(f"Stop Price: ${result['stop_price']:.2f}")
        print(f"Shares: {result['shares']}")
        print(f"Position Value: ${result['position_value']:,.2f}")
        print(f"\nRisk Metrics:")
        print(f"  Risk: ${result['risk_dollars']:.2f} ({result['risk_pct']:.3f}%)")
        print(f"  Heat After Entry: ${result['portfolio_heat_after']:,.2f} / ${result['heat_limit']:,.2f}")
        print(f"  Status: {result['heat_status']} {'✓' if result['verification_passed'] else '✗'}")
        print(f"\nProfit Targets:")
        print(f"  Stage 1 (+10%): ${result['stage1_target']:.2f}")
        print(f"  Stage 2 (+20%): ${result['stage2_target']:.2f}")
        print(f"  Stage 3 (+75%): ${result['stage3_target']:.2f}")
        
        if result['verification_passed']:
            print(f"\n✓ READY TO TRADE: Buy {result['shares']} shares")
        else:
            print(f"\n✗ POSITION TOO LARGE: Heat limit exceeded")

# Test
if __name__ == "__main__":
    sizer = PositionSizer(account_equity=50000, environment='A')
    result = sizer.calculate(entry_price=100, stop_price=95, edges=5, open_heat=1000)
    sizer.print_result(result)
```

**Run to test:**
```bash
python src/modules/position_sizer.py
```

---

## Continue to PHASE 2... (create remaining modules)

Due to length, I'm providing the core foundation. Let me continue with the AWS migration and remaining modules in a separate detailed section.

---

## PHASE 2: AWS LAMBDA SETUP (Weeks 3-4)

### Step 1: Create AWS Lambda Directory Structure

**File: aws/lambda/market_analysis_handler.py**

```python
"""
AWS Lambda Handler for Market Analysis
Triggered by EventBridge: Sunday 6 PM UTC
"""

import json
import boto3
import sys
from datetime import datetime

# For Lambda, we need to include src in path
sys.path.insert(0, '/var/task/src')

from modules.market_analysis import MarketAnalyzer
from utils.aws_utils import S3Manager, EmailNotifier

s3 = S3Manager()
emailer = EmailNotifier()

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    Executes market analysis and saves to S3
    """
    
    try:
        print(f"[{datetime.now()}] Starting market analysis Lambda")
        
        # Run market analysis
        analyzer = MarketAnalyzer()
        analyzer.fetch_market_data()
        analyzer.classify_environment()
        
        # Save to S3 instead of local CSV
        s3_key = f"data/market_analysis/{datetime.now().strftime('%Y-%m-%d')}.json"
        s3.put_object(s3_key, json.dumps(analyzer.results, indent=2))
        
        # Send email notification
        subject = f"Market Analysis - {analyzer.results['environment']}"
        emailer.send_email(subject, analyzer.generate_report())
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Market analysis completed',
                'environment': analyzer.results['environment'],
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        emailer.send_email("ALERT: Market Analysis Failed", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### Step 2: Create AWS Utilities

**File: src/utils/aws_utils.py**

```python
"""
AWS Utility Functions
S3 management, SES email, SNS SMS
"""

import boto3
import json
from datetime import datetime
import os

class S3Manager:
    """Manages S3 operations"""
    
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket = os.getenv('S3_BUCKET', 'trading-automation-dev')
    
    def put_object(self, key, data):
        """Upload data to S3"""
        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType='application/json'
            )
            print(f"✓ Uploaded to S3: s3://{self.bucket}/{key}")
            return True
        except Exception as e:
            print(f"✗ S3 upload failed: {e}")
            return False
    
    def get_object(self, key):
        """Download data from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read()
        except Exception as e:
            print(f"✗ S3 download failed: {e}")
            return None
    
    def list_objects(self, prefix):
        """List objects in S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            return response.get('Contents', [])
        except Exception as e:
            print(f"✗ S3 list failed: {e}")
            return []

class EmailNotifier:
    """Sends emails via AWS SES"""
    
    def __init__(self):
        self.ses_client = boto3.client('ses')
        self.sender = os.getenv('NOTIFY_EMAIL', 'noreply@tradingautomation.com')
    
    def send_email(self, subject, body, recipient=None):
        """Send email via SES"""
        recipient = recipient or os.getenv('NOTIFY_EMAIL')
        
        try:
            self.ses_client.send_email(
                Source=self.sender,
                Destination={'ToAddresses': [recipient]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body}}
                }
            )
            print(f"✓ Email sent: {subject}")
            return True
        except Exception as e:
            print(f"✗ Email failed: {e}")
            return False

class SMSNotifier:
    """Sends SMS via AWS SNS"""
    
    def __init__(self):
        self.sns_client = boto3.client('sns')
    
    def send_sms(self, phone_number, message):
        """Send SMS via SNS"""
        try:
            self.sns_client.publish(
                PhoneNumber=phone_number,
                Message=message
            )
            print(f"✓ SMS sent to {phone_number}")
            return True
        except Exception as e:
            print(f"✗ SMS failed: {e}")
            return False
```

### Step 3: Lambda Deployment Package

**File: aws/lambda/build_and_deploy.sh**

```bash
#!/bin/bash

# Build and deploy Lambda function
set -e

FUNCTION_NAME="trading-market-analysis"
RUNTIME="python3.11"
ROLE_ARN="arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-trading-role"

echo "Building Lambda package..."

# Create deployment directory
mkdir -p build
cd build

# Copy source files
cp -r ../../../src .
cp -r ../../../config .

# Install dependencies to build directory
pip install -r ../../../requirements.txt -t . --quiet

# Create Lambda handler
cp ../market_analysis_handler.py .

# Create deployment zip
zip -r ../lambda_deployment.zip . -q

cd ..

echo "Uploading to Lambda..."

# Update Lambda function code
aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --zip-file fileb://lambda_deployment.zip \
  --region us-east-1

echo "✓ Lambda function deployed successfully!"

# Cleanup
rm -rf build lambda_deployment.zip
```

---

## PHASE 3: TESTING & VALIDATION

### Local Unit Tests

**File: src/tests/test_modules.py**

```python
"""
Unit tests for trading modules
Run with: pytest src/tests/
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.modules.market_analysis import MarketAnalyzer
from src.modules.position_sizer import PositionSizer
from config.settings import config

class TestMarketAnalyzer:
    def test_environment_classification_A(self):
        """Test Environment A classification"""
        analyzer = MarketAnalyzer()
        analyzer.results = {
            'spy': {'above_50': True, 'above_200': True},
            'qqq': {'above_50': True, 'above_200': True},
            'breadth_pct': 75,
            'vix': 18
        }
        env = analyzer.classify_environment()
        assert env == 'A'
    
    def test_environment_classification_D(self):
        """Test Environment D classification"""
        analyzer = MarketAnalyzer()
        analyzer.results = {
            'spy': {'above_50': False, 'above_200': False},
            'qqq': {'above_50': False, 'above_200': False},
            'breadth_pct': 20,
            'vix': 40
        }
        env = analyzer.classify_environment()
        assert env == 'D'

class TestPositionSizer:
    def test_position_calculation_env_a(self):
        """Test position sizing for Environment A"""
        sizer = PositionSizer(account_equity=50000, environment='A')
        result = sizer.calculate(entry_price=100, stop_price=95, edges=5)
        
        assert result['shares'] > 0
        assert result['risk_pct'] <= 0.5
        assert result['verification_passed']
    
    def test_heat_limit_exceeded(self):
        """Test heat limit enforcement"""
        sizer = PositionSizer(account_equity=50000, environment='A')
        result = sizer.calculate(
            entry_price=100, 
            stop_price=95, 
            edges=5,
            open_heat=10000  # Already at heat limit
        )
        
        assert result['heat_status'] == 'EXCEEDED'
    
    def test_invalid_inputs(self):
        """Test input validation"""
        sizer = PositionSizer(account_equity=50000, environment='A')
        
        with pytest.raises(ValueError):
            sizer.calculate(entry_price=-100, stop_price=95)
        
        with pytest.raises(ValueError):
            sizer.calculate(entry_price=95, stop_price=100)

# Run tests: pytest src/tests/test_modules.py -v
```

---

## NEXT STEPS - IMPLEMENTATION CHECKLIST

```
WEEK 1 (Local Development):
[ ] Install Python & set up virtual environment
[ ] Create project structure & configuration
[ ] Implement Module 1: Market Analysis (completed above)
[ ] Implement Module 3: Position Sizing (completed above)
[ ] Create unit tests
[ ] Test both modules locally
[ ] Verify CSV output

WEEK 2 (Remaining Modules):
[ ] Implement Module 2: Stock Screening
[ ] Implement Module 4: Trade Journal
[ ] Implement Module 5: Performance Dashboard
[ ] Implement Module 6: Alerts & Monitoring
[ ] Complete all unit tests
[ ] Integration testing

WEEK 3 (AWS Setup):
[ ] Set up AWS account & IAM roles
[ ] Create S3 bucket structure
[ ] Create Lambda functions (6 total)
[ ] Set up EventBridge schedules
[ ] Configure SES for emails
[ ] Test each Lambda function

WEEK 4 (Production Deployment):
[ ] Deploy all Lambda functions
[ ] Validate S3 data flow
[ ] Test email notifications
[ ] Monitor CloudWatch logs
[ ] Set up cost alerts
[ ] Document everything

ONGOING:
[ ] Paper trade with automation
[ ] Monitor Lambda execution metrics
[ ] Optimize performance
[ ] Plan PostgreSQL migration (if needed)
```

---

**Ready to proceed with detailed implementation of remaining modules?** Let me create the complete Module 2, 4, 5, 6 code now.
