#!/bin/bash
# Deploy all 6 Lambda functions

set -e

# Load .env if it exists
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Configuration
REGION="us-east-1"
# Ensure Alpaca Keys are present
if [ -z "$ALPACA_API_KEY" ] || [ -z "$ALPACA_SECRET_KEY" ]; then
    echo "⚠️  WARNING: ALPACA_API_KEY or ALPACA_SECRET_KEY not set in environment."
    echo "   Using placeholders. Please update Lambda configuration manually if deployment succeeds."
    ALPACA_API_KEY="placeholder"
    ALPACA_SECRET_KEY="placeholder"
fi

PANDAS_LAYER_ARN="arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python311:12"
LAYER_ARN="arn:aws:lambda:us-east-1:904583676284:layer:trading-automation-deps:21"
ROLE_ARN="arn:aws:iam::904583676284:role/lambda-trading-automation-role"
S3_BUCKET="trading-automation-data-904583676284"
FROM_EMAIL="anshupadhi@gmail.com"
TO_EMAIL="anshupadhi@gmail.com"
ACCOUNT_ID="904583676284"
REPO_NAME="stock-screener"
IMAGE_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:latest"

echo "🚀 Deploying Lambda functions..."
echo "📂 Working Directory: $(pwd)"

# Function 1: Market Analysis
echo "📊 Deploying market-analysis-handler..."
./aws/scripts/build_lambda_package.sh market_analysis

aws lambda create-function \
    --function-name market-analysis-handler \
    --runtime python3.11 \
    --role ${ROLE_ARN} \
    --handler market_analysis_handler.lambda_handler \
    --timeout 300 \
    --memory-size 512 \
    --environment Variables="{
        S3_BUCKET=${S3_BUCKET},
        FROM_EMAIL=${FROM_EMAIL},
        TO_EMAIL=${TO_EMAIL},
        SES_REGION=${REGION},
        ALPACA_API_KEY=${ALPACA_API_KEY},
        ALPACA_SECRET_KEY=${ALPACA_SECRET_KEY}
    }" \
    --layers ${PANDAS_LAYER_ARN} ${LAYER_ARN} \
    --zip-file fileb://aws/lambda/packages/market_analysis.zip \
    --region ${REGION} || \
{
    aws lambda update-function-code \
        --function-name market-analysis-handler \
        --zip-file fileb://aws/lambda/packages/market_analysis.zip \
        --region ${REGION}
    

    
    echo "Waiting for update to settle..."
    sleep 10
    
    aws lambda update-function-configuration \
        --function-name market-analysis-handler \
        --environment Variables="{
            S3_BUCKET=${S3_BUCKET},
            FROM_EMAIL=${FROM_EMAIL},
            TO_EMAIL=${TO_EMAIL},
            SES_REGION=${REGION},
            ALPACA_API_KEY=${ALPACA_API_KEY},
            ALPACA_SECRET_KEY=${ALPACA_SECRET_KEY}
        }" \
        --region ${REGION}
}

# Function 2: Stock Screener (Docker Image)
echo "🐳 Building and Pushing Docker Image..."

# ECR Login
aws ecr get-login-password --region ${REGION} | podman login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Build & Push
podman build --platform linux/amd64 -t ${REPO_NAME}:latest -f aws/lambda/Dockerfile .
podman tag ${REPO_NAME}:latest ${IMAGE_URI}
podman push ${IMAGE_URI}

echo "🔍 Deploying stock-screener-handler (Docker Image)..."

aws lambda create-function \
    --function-name stock-screener-handler \
    --package-type Image \
    --code ImageUri=${IMAGE_URI} \
    --role ${ROLE_ARN} \
    --timeout 300 \
    --memory-size 5120 \
    --environment Variables="{
        S3_BUCKET=${S3_BUCKET},
        FROM_EMAIL=${FROM_EMAIL},
        TO_EMAIL=${TO_EMAIL},
        STOCK_UNIVERSE=SP500,
        ALPACA_API_KEY=${ALPACA_API_KEY},
        ALPACA_SECRET_KEY=${ALPACA_SECRET_KEY}
    }" \
    --region ${REGION} || \
{
    aws lambda update-function-code \
        --function-name stock-screener-handler \
        --image-uri ${IMAGE_URI} \
        --region ${REGION}
        
    echo "Waiting for update to settle..."
    sleep 10
    
    aws lambda update-function-configuration \
        --function-name stock-screener-handler \
        --environment Variables="{
        S3_BUCKET=${S3_BUCKET},
        FROM_EMAIL=${FROM_EMAIL},
        TO_EMAIL=${TO_EMAIL},
        STOCK_UNIVERSE=SP500,
        ALPACA_API_KEY=${ALPACA_API_KEY},
        ALPACA_SECRET_KEY=${ALPACA_SECRET_KEY}
    }" \
    --region ${REGION}
}

# Function: ML Trainer (Docker Image)
echo "🧠 Deploying ml-trainer-handler (Docker Image)..."

aws lambda create-function \
    --function-name ml-trainer-handler \
    --package-type Image \
    --code ImageUri=${IMAGE_URI} \
    --role ${ROLE_ARN} \
    --image-config Command="ml_trainer_handler.lambda_handler" \
    --timeout 900 \
    --memory-size 3008 \
    --environment Variables="{
        S3_BUCKET=${S3_BUCKET},
        FROM_EMAIL=${FROM_EMAIL},
        TO_EMAIL=${TO_EMAIL},
        SES_REGION=${REGION},
        ALPACA_API_KEY=${ALPACA_API_KEY},
        ALPACA_SECRET_KEY=${ALPACA_SECRET_KEY}
    }" \
    --region ${REGION} || \
aws lambda update-function-code \
    --function-name ml-trainer-handler \
    --image-uri ${IMAGE_URI} \
    --region ${REGION}

    echo "Waiting for update to settle..."
    sleep 30

aws lambda update-function-configuration \
    --function-name ml-trainer-handler \
    --image-config Command="ml_trainer_handler.lambda_handler" \
    --environment Variables="{
        S3_BUCKET=${S3_BUCKET},
        FROM_EMAIL=${FROM_EMAIL},
        TO_EMAIL=${TO_EMAIL},
        SES_REGION=${REGION},
        ALPACA_API_KEY=${ALPACA_API_KEY},
        ALPACA_SECRET_KEY=${ALPACA_SECRET_KEY}
    }" \
    --region ${REGION}

# Function 3: Position Sizer
echo "📐 Deploying position-sizer-handler..."
./aws/scripts/build_lambda_package.sh position_sizer

aws lambda create-function \
    --function-name position-sizer-handler \
    --runtime python3.11 \
    --role ${ROLE_ARN} \
    --handler position_sizer_handler.lambda_handler \
    --timeout 60 \
    --memory-size 256 \
    --environment Variables="{
        S3_BUCKET=${S3_BUCKET},
        ACCOUNT_SIZE=100000
    }" \
    --layers ${PANDAS_LAYER_ARN} ${LAYER_ARN} \
    --zip-file fileb://aws/lambda/packages/position_sizer.zip \
    --region ${REGION} || \
aws lambda update-function-code \
    --function-name position-sizer-handler \
    --zip-file fileb://aws/lambda/packages/position_sizer.zip \
    --region ${REGION}

# Function 4: Trade Journal
echo "📓 Deploying trade-journal-handler..."
./aws/scripts/build_lambda_package.sh trade_journal

aws lambda create-function \
    --function-name trade-journal-handler \
    --runtime python3.11 \
    --role ${ROLE_ARN} \
    --handler trade_journal_handler.lambda_handler \
    --timeout 60 \
    --memory-size 256 \
    --environment Variables="{
        S3_BUCKET=${S3_BUCKET},
        JOURNAL_FILE=trade_journal/journal.csv
    }" \
    --layers ${PANDAS_LAYER_ARN} ${LAYER_ARN} \
    --zip-file fileb://aws/lambda/packages/trade_journal.zip \
    --region ${REGION} || \
aws lambda update-function-code \
    --function-name trade-journal-handler \
    --zip-file fileb://aws/lambda/packages/trade_journal.zip \
    --region ${REGION}

# Function 5: Dashboard
echo "📈 Deploying dashboard-handler..."
./aws/scripts/build_lambda_package.sh dashboard

aws lambda create-function \
    --function-name dashboard-handler \
    --runtime python3.11 \
    --role ${ROLE_ARN} \
    --handler dashboard_handler.lambda_handler \
    --timeout 300 \
    --memory-size 512 \
    --environment Variables="{
        S3_BUCKET=${S3_BUCKET},
        FROM_EMAIL=${FROM_EMAIL},
        TO_EMAIL=${TO_EMAIL},
        INITIAL_CAPITAL=100000,
        JOURNAL_FILE=trade_journal/journal.csv
    }" \
    --layers ${PANDAS_LAYER_ARN} ${LAYER_ARN} \
    --zip-file fileb://aws/lambda/packages/dashboard.zip \
    --region ${REGION} || \
aws lambda update-function-code \
    --function-name dashboard-handler \
    --zip-file fileb://aws/lambda/packages/dashboard.zip \
    --region ${REGION}

# Function 6: Alerts Monitor
echo "🚨 Deploying alerts-handler..."
./aws/scripts/build_lambda_package.sh alerts

aws lambda create-function \
    --function-name alerts-handler \
    --runtime python3.11 \
    --role ${ROLE_ARN} \
    --handler alerts_handler.lambda_handler \
    --timeout 60 \
    --memory-size 256 \
    --environment Variables="{
        S3_BUCKET=${S3_BUCKET},
        FROM_EMAIL=${FROM_EMAIL},
        TO_EMAIL=${TO_EMAIL},
        POSITIONS_FILE=positions/active_positions.json,
        ACCOUNT_STATE_FILE=account/account_state.json
    }" \
    --layers ${PANDAS_LAYER_ARN} ${LAYER_ARN} \
    --zip-file fileb://aws/lambda/packages/alerts.zip \
    --region ${REGION} || \
aws lambda update-function-code \
    --function-name alerts-handler \
    --zip-file fileb://aws/lambda/packages/alerts.zip \
    --region ${REGION}

echo "🔄 Updating Lambda configurations (Layers for generic functions only)..."
for func in market-analysis-handler position-sizer-handler trade-journal-handler dashboard-handler alerts-handler; do
    echo "   Updating config for $func..."
    aws lambda update-function-configuration --function-name $func --layers ${PANDAS_LAYER_ARN} ${LAYER_ARN} --region ${REGION}
done

echo "✅ All Lambda functions deployed and configured!"