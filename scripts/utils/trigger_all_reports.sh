#!/bin/bash
set -e
echo "🚀 Triggering Reports (Final Attempt)..."

# 1. Market Analysis
echo "📊 Invoking Market Analysis..."
aws lambda invoke --function-name market-analysis-handler --region us-east-1 response_market.json

# 2. Stock Screener
echo "🔍 Invoking Stock Screener..."
aws lambda invoke --function-name stock-screener-handler --region us-east-1 response_screener.json

# 3. Dashboard
echo "📈 Invoking Dashboard..."
aws lambda invoke --function-name dashboard-handler --region us-east-1 --payload '{"source": "aws.events"}' response_dashboard.json

# 4. ML Trainer
echo "🧠 Invoking ML Trainer..."
aws lambda invoke --function-name ml-trainer-handler --region us-east-1 response_ml.json

echo "✅ All invoked. Validating..."
cat response_market.json
echo -e "\n"
cat response_screener.json
echo -e "\n"
cat response_dashboard.json
echo -e "\n"
cat response_ml.json

rm response_*.json
