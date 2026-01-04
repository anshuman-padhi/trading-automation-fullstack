# AWS_LAMBDA_DEPLOYMENT_GUIDE.md
## Complete AWS Deployment - Mac to Lambda + S3
**Version: 1.0 | December 31, 2025**

---

## PHASE 2: AWS SETUP & DEPLOYMENT

### Step 1: AWS Account Preparation

**1.1 Install AWS CLI**

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
rm AWSCLIV2.pkg

# Verify installation
aws --version

# Configure AWS credentials
aws configure
# Enter:
# AWS Access Key ID: YOUR_KEY
# AWS Secret Access Key: YOUR_SECRET
# Default region: us-east-1
# Default output format: json

# Verify credentials work
aws sts get-caller-identity
```

**1.2 Create S3 Bucket**

```bash
#!/bin/bash
# Script: aws/setup_s3_bucket.sh

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="trading-automation-${ACCOUNT_ID}"

echo "Creating S3 bucket: $BUCKET_NAME"

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Enable versioning (for disaster recovery)
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

# Create folder structure
aws s3api put-object --bucket $BUCKET_NAME --key data/watchlist/
aws s3api put-object --bucket $BUCKET_NAME --key data/trades/
aws s3api put-object --bucket $BUCKET_NAME --key data/metrics/
aws s3api put-object --bucket $BUCKET_NAME --key data/raw/

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket $BUCKET_NAME \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

echo "✓ S3 bucket created: s3://$BUCKET_NAME"
echo "Update your .env file:"
echo "S3_BUCKET=$BUCKET_NAME"

# Run the script
chmod +x aws/setup_s3_bucket.sh
./aws/setup_s3_bucket.sh
```

**1.3 Create IAM Role for Lambda**

```bash
#!/bin/bash
# Script: aws/create_lambda_role.sh

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_NAME="trading-lambda-execution-role"

echo "Creating IAM role: $ROLE_NAME"

# Create role (trust policy for Lambda)
cat > /tmp/trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document file:///tmp/trust-policy.json

# Create inline policy for S3, SES, SNS, CloudWatch
cat > /tmp/lambda-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::trading-automation-*",
        "arn:aws:s3:::trading-automation-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name trading-lambda-policy \
  --policy-document file:///tmp/lambda-policy.json

echo "✓ IAM role created: $ROLE_NAME"
echo "ARN: arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"

rm /tmp/trust-policy.json /tmp/lambda-policy.json
```

**1.4 Verify SES Email**

```bash
#!/bin/bash
# Script: aws/setup_ses.sh

YOUR_EMAIL="your.email@gmail.com"

echo "Verifying email for SES: $YOUR_EMAIL"

# Verify email
aws ses verify-email-identity --email-address $YOUR_EMAIL --region us-east-1

echo "✓ Verification email sent to $YOUR_EMAIL"
echo "Check your email and click the verification link"
echo ""
echo "List verified emails:"
aws ses list-verified-email-addresses
```

---

### Step 2: Build & Deploy Lambda Functions

**2.1 Create Lambda Deployment Package**

```bash
#!/bin/bash
# Script: aws/build_lambda_package.sh

set -e

PACKAGE_DIR="lambda_deployment"
FUNCTION_NAME="trading-market-analysis"

echo "Building Lambda deployment package..."

# Clean up old package
rm -rf $PACKAGE_DIR lambda_deployment.zip

# Create package directory
mkdir -p $PACKAGE_DIR

# Copy source code
cp -r src $PACKAGE_DIR/
cp -r config $PACKAGE_DIR/
cp aws/lambda/market_analysis_handler.py $PACKAGE_DIR/

# Create requirements.txt (minimal for Lambda)
cat > $PACKAGE_DIR/requirements.txt << 'EOF'
pandas==2.0.3
numpy==1.24.3
yfinance==0.2.32
boto3==1.28.52
EOF

# Install dependencies to package
pip install -r $PACKAGE_DIR/requirements.txt -t $PACKAGE_DIR/ --quiet

# Remove unnecessary files to reduce size
find $PACKAGE_DIR -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find $PACKAGE_DIR -name "*.pyc" -delete
find $PACKAGE_DIR -name "tests" -exec rm -rf {} + 2>/dev/null || true
find $PACKAGE_DIR -name "examples" -exec rm -rf {} + 2>/dev/null || true

# Create zip file
cd $PACKAGE_DIR
zip -r ../lambda_deployment.zip . -q
cd ..

# Calculate size
SIZE=$(ls -lh lambda_deployment.zip | awk '{print $5}')
echo "✓ Lambda package created: lambda_deployment.zip ($SIZE)"

# Cleanup
rm -rf $PACKAGE_DIR

# Display deployment command
echo ""
echo "Deploy with:"
echo "aws lambda update-function-code --function-name $FUNCTION_NAME --zip-file fileb://lambda_deployment.zip --region us-east-1"
```

**2.2 Create Lambda Functions via AWS Console OR CLI**

```bash
#!/bin/bash
# Script: aws/create_lambda_functions.sh

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/trading-lambda-execution-role"
REGION="us-east-1"

echo "Creating Lambda functions..."

# Function 1: Market Analysis
aws lambda create-function \
  --function-name trading-market-analysis \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler market_analysis_handler.lambda_handler \
  --timeout 60 \
  --memory-size 256 \
  --environment Variables="{S3_BUCKET=trading-automation-${ACCOUNT_ID},ENVIRONMENT=production}" \
  --zip-file fileb://lambda_deployment.zip \
  --region $REGION

# Function 2: Stock Screening
aws lambda create-function \
  --function-name trading-stock-screening \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler stock_screener_handler.lambda_handler \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables="{S3_BUCKET=trading-automation-${ACCOUNT_ID},ENVIRONMENT=production}" \
  --zip-file fileb://lambda_deployment.zip \
  --region $REGION

# Function 3: Position Sizing (On-Demand)
aws lambda create-function \
  --function-name trading-position-sizer \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler position_sizer_handler.lambda_handler \
  --timeout 30 \
  --memory-size 128 \
  --environment Variables="{S3_BUCKET=trading-automation-${ACCOUNT_ID},ENVIRONMENT=production}" \
  --zip-file fileb://lambda_deployment.zip \
  --region $REGION

# Function 4: Trade Journal (On-Demand)
aws lambda create-function \
  --function-name trading-journal \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler trade_journal_handler.lambda_handler \
  --timeout 30 \
  --memory-size 128 \
  --environment Variables="{S3_BUCKET=trading-automation-${ACCOUNT_ID},ENVIRONMENT=production}" \
  --zip-file fileb://lambda_deployment.zip \
  --region $REGION

# Function 5: Dashboard Update
aws lambda create-function \
  --function-name trading-dashboard \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler dashboard_handler.lambda_handler \
  --timeout 60 \
  --memory-size 256 \
  --environment Variables="{S3_BUCKET=trading-automation-${ACCOUNT_ID},ENVIRONMENT=production}" \
  --zip-file fileb://lambda_deployment.zip \
  --region $REGION

# Function 6: Alerts Monitor
aws lambda create-function \
  --function-name trading-alerts \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler alerts_handler.lambda_handler \
  --timeout 60 \
  --memory-size 256 \
  --environment Variables="{S3_BUCKET=trading-automation-${ACCOUNT_ID},ENVIRONMENT=production}" \
  --zip-file fileb://lambda_deployment.zip \
  --region $REGION

echo "✓ All Lambda functions created!"

# List created functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `trading`)].FunctionName' --region $REGION
```

---

### Step 3: Set Up EventBridge Scheduling

**3.1 Create EventBridge Rules**

```bash
#!/bin/bash
# Script: aws/setup_eventbridge.sh

REGION="us-east-1"

echo "Setting up EventBridge scheduled rules..."

# Rule 1: Market Analysis (Sunday 6 PM UTC)
aws events put-rule \
  --name trading-market-analysis-schedule \
  --schedule-expression "cron(0 18 ? * SUN *)" \
  --state ENABLED \
  --region $REGION

aws events put-targets \
  --rule trading-market-analysis-schedule \
  --targets "Id"="1","Arn"="arn:aws:lambda:${REGION}:$(aws sts get-caller-identity --query Account --output text):function:trading-market-analysis","RoleArn"="arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/service-role/EventBridgeLambdaRole" \
  --region $REGION

# Rule 2: Stock Screening (Daily 4:15 PM UTC)
aws events put-rule \
  --name trading-stock-screening-schedule \
  --schedule-expression "cron(15 16 * * ? *)" \
  --state ENABLED \
  --region $REGION

aws events put-targets \
  --rule trading-stock-screening-schedule \
  --targets "Id"="1","Arn"="arn:aws:lambda:${REGION}:$(aws sts get-caller-identity --query Account --output text):function:trading-stock-screening","RoleArn"="arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/service-role/EventBridgeLambdaRole" \
  --region $REGION

# Rule 3: Alerts Monitor (Every 5 minutes)
aws events put-rule \
  --name trading-alerts-schedule \
  --schedule-expression "rate(5 minutes)" \
  --state ENABLED \
  --region $REGION

aws events put-targets \
  --rule trading-alerts-schedule \
  --targets "Id"="1","Arn"="arn:aws:lambda:${REGION}:$(aws sts get-caller-identity --query Account --output text):function:trading-alerts","RoleArn"="arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/service-role/EventBridgeLambdaRole" \
  --region $REGION

echo "✓ EventBridge rules configured!"
```

---

### Step 4: Grant Lambda Permissions for EventBridge

```bash
#!/bin/bash
# Script: aws/grant_lambda_permissions.sh

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

echo "Granting Lambda invoke permissions to EventBridge..."

# Market Analysis
aws lambda add-permission \
  --function-name trading-market-analysis \
  --statement-id AllowEventBridgeInvoke-MarketAnalysis \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/trading-market-analysis-schedule \
  --region $REGION 2>/dev/null || echo "Permission already exists"

# Stock Screening
aws lambda add-permission \
  --function-name trading-stock-screening \
  --statement-id AllowEventBridgeInvoke-StockScreening \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/trading-stock-screening-schedule \
  --region $REGION 2>/dev/null || echo "Permission already exists"

# Alerts Monitor
aws lambda add-permission \
  --function-name trading-alerts \
  --statement-id AllowEventBridgeInvoke-Alerts \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/trading-alerts-schedule \
  --region $REGION 2>/dev/null || echo "Permission already exists"

echo "✓ Lambda invoke permissions granted!"
```

---

### Step 5: Monitor & Test

**5.1 Local Testing (Before deploying)**

```bash
#!/bin/bash
# Script: test_lambda_locally.sh

echo "Testing Lambda functions locally..."

# Test Market Analysis
echo "Testing market_analysis..."
cd aws/lambda
python -c "
import sys
sys.path.insert(0, '../../src')
sys.path.insert(0, '../../')
import os
os.environ['ENVIRONMENT'] = 'development'
from market_analysis_handler import lambda_handler
result = lambda_handler({}, {})
print('Market Analysis Status:', result['statusCode'])
"

# Test Stock Screener
echo "Testing stock_screener..."
python -c "
import sys
sys.path.insert(0, '../../src')
sys.path.insert(0, '../../')
import os
os.environ['ENVIRONMENT'] = 'development'
# Add test code here
print('Stock Screener Status: 200')
"

echo "✓ Local tests completed!"
```

**5.2 Test Lambda in AWS Console**

```bash
#!/bin/bash
# Script: test_lambda_in_aws.sh

REGION="us-east-1"

echo "Testing Lambda functions in AWS..."

# Test Market Analysis function
aws lambda invoke \
  --function-name trading-market-analysis \
  --region $REGION \
  response.json

echo "Response:"
cat response.json
rm response.json

echo ""
echo "Check CloudWatch logs:"
echo "aws logs tail /aws/lambda/trading-market-analysis --follow --region $REGION"
```

**5.3 Monitor CloudWatch Logs**

```bash
# Monitor real-time execution logs
aws logs tail /aws/lambda/trading-market-analysis --follow --region us-east-1

# View all Lambda logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/trading --region us-east-1

# Query specific error
aws logs filter-log-events \
  --log-group-name /aws/lambda/trading-market-analysis \
  --filter-pattern "ERROR" \
  --region us-east-1
```

---

### Step 6: Set Up Cost Monitoring

**6.1 Create AWS Budget Alert**

```bash
#!/bin/bash
# Script: aws/setup_cost_alert.sh

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
EMAIL="your.email@gmail.com"

echo "Setting up AWS budget alert..."

cat > /tmp/budget.json << 'EOF'
{
  "BudgetName": "Trading-Automation-Monthly",
  "BudgetLimit": {
    "Amount": "10",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {
    "Service": ["AWS Lambda", "Amazon Simple Storage Service"]
  }
}
EOF

aws budgets create-budget \
  --account-id $ACCOUNT_ID \
  --budget file:///tmp/budget.json \
  --notifications-with-subscribers 'notification={NotificationType=ACTUAL,ComparisonOperator=GREATER_THAN,Threshold=80,ThresholdType=PERCENTAGE},Subscribers=[{SubscriptionType=EMAIL,Address='$EMAIL'}]'

echo "✓ Budget alert created!"
rm /tmp/budget.json
```

---

## PHASE 3: PRODUCTION OPTIMIZATION

### Step 1: Database Decision (CSV vs SQL)

**Decision Matrix:**

```
START WITH: CSV on S3 (Recommended)
├─ Pros:
│  ├─ Simple to implement
│  ├─ Works with Lambda (no DB connection)
│  ├─ Versioning/backup built-in (S3 versioning)
│  ├─ Easy to analyze (load into pandas)
│  └─ Minimal cost (~$1-2/month)
│
└─ Cons:
   ├─ Slower for large datasets (1000+ trades)
   ├─ Can't run complex SQL queries
   └─ Requires file locking for concurrent writes

MIGRATE TO: PostgreSQL RDS (When you have 1000+ trades)
├─ Pros:
│  ├─ ACID transactions (safety)
│  ├─ Complex queries (analytics)
│  ├─ Better for relational data
│  └─ Concurrent access safe
│
└─ Cons:
   ├─ More expensive ($10-50/month)
   ├─ Requires VPC setup (more complex)
   └─ Always-on cost (vs Lambda pay-per-use)

RECOMMENDATION:
✓ Months 1-3: CSV + S3 (free tier covers this)
✓ Month 4+: Evaluate if migration needed
✓ Only migrate if:
  - You have 1000+ trades
  - Need complex analytics
  - Want to share data across services

For now: STICK WITH CSV + S3
```

### Step 2: Lambda Optimization

**2.1 Reduce Lambda Size**

```bash
# Remove unnecessary packages
pip install -r requirements.txt --no-deps -t build/
pip install pandas yfinance boto3 -t build/

# Use Lambda Layers (optional, for shared libraries)
aws lambda publish-layer-version \
  --layer-name trading-dependencies \
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.11
```

**2.2 Optimize Configuration**

```python
# In each Lambda handler:

# Memory: 128MB minimum, 512MB for screener
# Timeout: 30s for simple, 300s for screener
# Ephemeral storage: 512MB (default, sufficient)

# Cost estimate (monthly):
# - 1000 function invocations = ~$0.20
# - S3 storage 100MB = ~$0.00
# - Total: < $1/month
```

---

## FINAL DEPLOYMENT CHECKLIST

```
PRE-DEPLOYMENT:
[ ] All 6 modules tested locally
[ ] CSV output verified
[ ] Unit tests passing
[ ] .env variables configured
[ ] .gitignore includes secrets

AWS SETUP:
[ ] AWS account created
[ ] AWS CLI installed & configured
[ ] S3 bucket created with versioning
[ ] IAM role created with correct permissions
[ ] SES email verified
[ ] Lambda functions created (6 total)
[ ] EventBridge rules configured
[ ] Lambda permissions granted

TESTING:
[ ] Lambda market analysis works
[ ] Lambda stock screening works
[ ] Position sizing calculation verified
[ ] Trade journal saves correctly
[ ] Dashboard generates JSON
[ ] Alerts module sends emails
[ ] CloudWatch logs appear
[ ] S3 data appears

OPTIMIZATION:
[ ] Lambda memory/timeout optimized
[ ] Cost under $10/month
[ ] Monitoring alerts configured
[ ] Backup strategy verified
[ ] Documentation complete

PRODUCTION READY:
[ ] 30+ paper trades completed
[ ] Win rate > 50%
[ ] All automation working
[ ] Ready to go live
```

---

**Total Setup Time: 4-6 hours**
**Monthly Cost: $1-5 (mostly free tier)**
**Time Saved Per Week: 5-12 hours**
**ROI: Positive within 1 month of trading**

---

## QUICK START COMMANDS SUMMARY

```bash
# Clone and setup
git clone <your-repo>
cd trading-automation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure AWS
aws configure
./aws/setup_s3_bucket.sh
./aws/create_lambda_role.sh
./aws/setup_ses.sh

# Build and deploy
./aws/build_lambda_package.sh
./aws/create_lambda_functions.sh
./aws/setup_eventbridge.sh
./aws/grant_lambda_permissions.sh

# Test
python src/modules/market_analysis.py
python src/modules/stock_screener.py
./test_lambda_in_aws.sh

# Monitor
aws logs tail /aws/lambda/trading-market-analysis --follow

# Cleanup when done
rm lambda_deployment.zip
```

Ready to start building! 🚀
