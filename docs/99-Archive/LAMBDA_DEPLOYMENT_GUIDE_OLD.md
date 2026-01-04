# AWS Lambda Deployment Guide
## All 6 Handlers Ready for Deployment

### 📦 Lambda Handlers Created

```
aws/lambda/
├── market_analysis_handler.py    # Module 1 - Weekly market analysis
├── stock_screener_handler.py     # Module 2 - Daily stock screening
├── position_sizer_handler.py     # Module 3 - Position sizing API
├── trade_journal_handler.py      # Module 4 - Trade recording API
├── dashboard_handler.py          # Module 5 - Performance dashboard
└── alerts_handler.py             # Module 6 - Real-time alerts
```

---

## 🚀 Deployment Steps

### Step 1: Download All Handler Files

Save the 6 generated handler files to your project:

```bash
cd /Users/anshumanpadhi/workspace/quantx/trading-automation-fullstack
mkdir -p aws/lambda
cd aws/lambda

# Download and save all 6 handlers here
```

### Step 2: Create Lambda Layer (Dependencies)

Create a Lambda Layer with your modules:

```bash
# Create layer directory structure
mkdir -p lambda-layer/python/src/modules

# Copy all 6 core modules
cp ../../src/modules/*.py lambda-layer/python/src/modules/

# Install dependencies
cd lambda-layer/python
pip install pandas numpy boto3 -t .

# Create layer zip
cd ..
zip -r trading-automation-layer.zip python/

# Upload to AWS Lambda Layers
aws lambda publish-layer-version \
    --layer-name trading-automation-layer \
    --description "Trading automation core modules" \
    --zip-file fileb://trading-automation-layer.zip \
    --compatible-runtimes python3.9 python3.10 python3.11
```

### Step 3: Create S3 Bucket for Data Storage

```bash
# Create S3 bucket
aws s3 mb s3://trading-automation-data-YOUR-ACCOUNT-ID

# Create folder structure
aws s3api put-object --bucket trading-automation-data-YOUR-ACCOUNT-ID --key market_analysis/
aws s3api put-object --bucket trading-automation-data-YOUR-ACCOUNT-ID --key screening/
aws s3api put-object --bucket trading-automation-data-YOUR-ACCOUNT-ID --key position_sizing/
aws s3api put-object --bucket trading-automation-data-YOUR-ACCOUNT-ID --key trade_journal/
aws s3api put-object --bucket trading-automation-data-YOUR-ACCOUNT-ID --key dashboard/
aws s3api put-object --bucket trading-automation-data-YOUR-ACCOUNT-ID --key alerts/
aws s3api put-object --bucket trading-automation-data-YOUR-ACCOUNT-ID --key positions/
aws s3api put-object --bucket trading-automation-data-YOUR-ACCOUNT-ID --key account/
```

### Step 4: Deploy Lambda Functions

#### Lambda 1: Market Analysis

```bash
# Create function
aws lambda create-function \
    --function-name market-analysis-handler \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-trading-role \
    --handler market_analysis_handler.lambda_handler \
    --timeout 300 \
    --memory-size 512 \
    --environment Variables="{
        S3_BUCKET=trading-automation-data-YOUR-ACCOUNT-ID,
        FROM_EMAIL=trading@yourdomain.com,
        TO_EMAIL=your-email@gmail.com,
        SES_REGION=us-east-1
    }" \
    --layers arn:aws:lambda:REGION:ACCOUNT:layer:trading-automation-layer:1 \
    --zip-file fileb://market_analysis_handler.zip
```

#### Lambda 2: Stock Screener

```bash
aws lambda create-function \
    --function-name stock-screener-handler \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-trading-role \
    --handler stock_screener_handler.lambda_handler \
    --timeout 300 \
    --memory-size 1024 \
    --environment Variables="{
        S3_BUCKET=trading-automation-data-YOUR-ACCOUNT-ID,
        FROM_EMAIL=trading@yourdomain.com,
        TO_EMAIL=your-email@gmail.com,
        STOCK_UNIVERSE=SP500
    }" \
    --layers arn:aws:lambda:REGION:ACCOUNT:layer:trading-automation-layer:1 \
    --zip-file fileb://stock_screener_handler.zip
```

#### Lambda 3: Position Sizer

```bash
aws lambda create-function \
    --function-name position-sizer-handler \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-trading-role \
    --handler position_sizer_handler.lambda_handler \
    --timeout 60 \
    --memory-size 256 \
    --environment Variables="{
        S3_BUCKET=trading-automation-data-YOUR-ACCOUNT-ID,
        ACCOUNT_SIZE=100000
    }" \
    --layers arn:aws:lambda:REGION:ACCOUNT:layer:trading-automation-layer:1 \
    --zip-file fileb://position_sizer_handler.zip
```

#### Lambda 4: Trade Journal

```bash
aws lambda create-function \
    --function-name trade-journal-handler \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-trading-role \
    --handler trade_journal_handler.lambda_handler \
    --timeout 60 \
    --memory-size 256 \
    --environment Variables="{
        S3_BUCKET=trading-automation-data-YOUR-ACCOUNT-ID,
        JOURNAL_FILE=trade_journal/journal.csv
    }" \
    --layers arn:aws:lambda:REGION:ACCOUNT:layer:trading-automation-layer:1 \
    --zip-file fileb://trade_journal_handler.zip
```

#### Lambda 5: Dashboard

```bash
aws lambda create-function \
    --function-name dashboard-handler \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-trading-role \
    --handler dashboard_handler.lambda_handler \
    --timeout 300 \
    --memory-size 512 \
    --environment Variables="{
        S3_BUCKET=trading-automation-data-YOUR-ACCOUNT-ID,
        FROM_EMAIL=trading@yourdomain.com,
        TO_EMAIL=your-email@gmail.com,
        INITIAL_CAPITAL=100000,
        JOURNAL_FILE=trade_journal/journal.csv
    }" \
    --layers arn:aws:lambda:REGION:ACCOUNT:layer:trading-automation-layer:1 \
    --zip-file fileb://dashboard_handler.zip
```

#### Lambda 6: Alerts Monitor

```bash
aws lambda create-function \
    --function-name alerts-handler \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-trading-role \
    --handler alerts_handler.lambda_handler \
    --timeout 60 \
    --memory-size 256 \
    --environment Variables="{
        S3_BUCKET=trading-automation-data-YOUR-ACCOUNT-ID,
        FROM_EMAIL=alerts@yourdomain.com,
        TO_EMAIL=your-email@gmail.com,
        POSITIONS_FILE=positions/active_positions.json,
        ACCOUNT_STATE_FILE=account/account_state.json
    }" \
    --layers arn:aws:lambda:REGION:ACCOUNT:layer:trading-automation-layer:1 \
    --zip-file fileb://alerts_handler.zip
```

### Step 5: Create EventBridge Rules

#### Rule 1: Market Analysis (Weekly - Sundays 6 PM UTC)

```bash
aws events put-rule \
    --name market-analysis-weekly \
    --schedule-expression "cron(0 18 ? * SUN *)" \
    --description "Weekly market analysis every Sunday at 6 PM UTC"

aws events put-targets \
    --rule market-analysis-weekly \
    --targets "Id"="1","Arn"="arn:aws:lambda:REGION:ACCOUNT:function:market-analysis-handler"

aws lambda add-permission \
    --function-name market-analysis-handler \
    --statement-id market-analysis-weekly \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:REGION:ACCOUNT:rule/market-analysis-weekly
```

#### Rule 2: Stock Screening (Daily - 4:15 PM UTC)

```bash
aws events put-rule \
    --name stock-screening-daily \
    --schedule-expression "cron(15 16 ? * MON-FRI *)" \
    --description "Daily stock screening at 4:15 PM UTC weekdays"

aws events put-targets \
    --rule stock-screening-daily \
    --targets "Id"="1","Arn"="arn:aws:lambda:REGION:ACCOUNT:function:stock-screener-handler"

aws lambda add-permission \
    --function-name stock-screener-handler \
    --statement-id stock-screening-daily \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:REGION:ACCOUNT:rule/stock-screening-daily
```

#### Rule 3: Dashboard Update (Daily - 8 PM UTC)

```bash
aws events put-rule \
    --name dashboard-update-daily \
    --schedule-expression "cron(0 20 * * ? *)" \
    --description "Daily dashboard update at 8 PM UTC"

aws events put-targets \
    --rule dashboard-update-daily \
    --targets "Id"="1","Arn"="arn:aws:lambda:REGION:ACCOUNT:function:dashboard-handler"

aws lambda add-permission \
    --function-name dashboard-handler \
    --statement-id dashboard-update-daily \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:REGION:ACCOUNT:rule/dashboard-update-daily
```

#### Rule 4: Alerts Monitoring (Every 5 minutes)

```bash
aws events put-rule \
    --name alerts-monitor-5min \
    --schedule-expression "cron(0/5 * * * ? *)" \
    --description "Monitor alerts every 5 minutes"

aws events put-targets \
    --rule alerts-monitor-5min \
    --targets "Id"="1","Arn"="arn:aws:lambda:REGION:ACCOUNT:function:alerts-handler"

aws lambda add-permission \
    --function-name alerts-handler \
    --statement-id alerts-monitor-5min \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:REGION:ACCOUNT:rule/alerts-monitor-5min
```

### Step 6: Create IAM Role

Create `lambda-trading-role` with these permissions:

```json
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
        "arn:aws:s3:::trading-automation-data-*",
        "arn:aws:s3:::trading-automation-data-*/*"
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
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### Step 7: Verify SES Email Addresses

```bash
# Verify sender email
aws ses verify-email-identity --email-address trading@yourdomain.com

# Verify recipient email
aws ses verify-email-identity --email-address your-email@gmail.com
```

---

## 📊 Handler Summary

| Handler | Trigger | Schedule | Purpose |
|---------|---------|----------|---------|
| market_analysis_handler | EventBridge | Sundays 6 PM UTC | Weekly market analysis |
| stock_screener_handler | EventBridge | Daily 4:15 PM UTC (weekdays) | Daily stock screening |
| position_sizer_handler | API Gateway | On-demand | Calculate position sizes |
| trade_journal_handler | API Gateway | On-demand | Record trades |
| dashboard_handler | EventBridge | Daily 8 PM UTC | Update performance dashboard |
| alerts_handler | EventBridge | Every 5 minutes | Monitor positions & send alerts |

---

## 🔧 Environment Variables

### Required for All Handlers:
- `S3_BUCKET` - Your S3 bucket name

### Email-Enabled Handlers:
- `FROM_EMAIL` - Verified SES sender email
- `TO_EMAIL` - Your email address
- `SES_REGION` - AWS region for SES (e.g., us-east-1)

### Handler-Specific:
- `ACCOUNT_SIZE` - Initial account balance (position_sizer)
- `INITIAL_CAPITAL` - Starting capital (dashboard)
- `JOURNAL_FILE` - Path to journal CSV in S3
- `POSITIONS_FILE` - Path to positions JSON in S3
- `ACCOUNT_STATE_FILE` - Path to account state JSON in S3

---

## ✅ Testing Handlers Locally

Test each handler before deploying:

```python
# test_handler.py
from market_analysis_handler import lambda_handler

event = {}
context = None

result = lambda_handler(event, context)
print(result)
```

---

## 📝 Next Steps

1. ✅ Download all 6 handler files
2. ✅ Save to `aws/lambda/` directory
3. ✅ Create Lambda Layer with dependencies
4. ✅ Deploy all 6 Lambda functions
5. ✅ Create EventBridge schedules
6. ✅ Verify SES emails
7. ✅ Test each handler
8. ✅ Monitor CloudWatch logs

---

## 💰 Estimated Costs

**Phase 1 (Weeks 1-8):**
- Lambda: ~$0.20/month
- S3: ~$0.50/month
- SES: ~$0.10/month
- **Total: $1-5/month**

---

## 🎯 Success Criteria

After deployment, you should receive:
- ✅ Weekly market analysis emails (Sundays)
- ✅ Daily stock screening emails (weekdays)
- ✅ Daily performance dashboard emails
- ✅ Real-time alerts (when triggered)
- ✅ All data backed up to S3

---

**Ready to deploy? Start with Step 1!** 🚀
