#!/bin/bash
# Setup EventBridge rules for automated execution

REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Rule 1: Market Analysis (Weekly - Sundays 6 AM SGT / Sat 10 PM UTC)
aws events put-rule \
    --name market-analysis-weekly \
    --schedule-expression "cron(0 22 ? * SAT *)" \
    --description "Weekly market analysis every Saturday at 10 PM UTC (Sunday 6 AM SGT)" \
    --region ${REGION}

aws events put-targets \
    --rule market-analysis-weekly \
    --targets "Id"="1","Arn"="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:market-analysis-handler" \
    --region ${REGION}

aws lambda add-permission \
    --function-name market-analysis-handler \
    --statement-id market-analysis-weekly \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/market-analysis-weekly \
    --region ${REGION}

echo "✅ Market Analysis schedule created"

# Rule 2: Stock Screening (Daily - 6 AM SGT / 10 PM UTC Mon-Fri)
# Runs Mon-Fri UTC 22:00 (Tue-Sat SGT 06:00) to capture Mon-Fri market closes
aws events put-rule \
    --name stock-screening-daily \
    --schedule-expression "cron(0 22 ? * MON-FRI *)" \
    --description "Daily stock screening at 10 PM UTC (6 AM SGT next day)" \
    --region ${REGION}

aws events put-targets \
    --rule stock-screening-daily \
    --targets "Id"="1","Arn"="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:stock-screener-handler" \
    --region ${REGION}

aws lambda add-permission \
    --function-name stock-screener-handler \
    --statement-id stock-screening-daily \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/stock-screening-daily \
    --region ${REGION}

echo "✅ Stock Screening schedule created"

# Rule 3: Dashboard Update (Daily - 8 PM SGT / 12 PM UTC)
aws events put-rule \
    --name dashboard-update-daily \
    --schedule-expression "cron(0 12 * * ? *)" \
    --description "Daily dashboard update at 12 PM UTC (8 PM SGT)" \
    --region ${REGION}

aws events put-targets \
    --rule dashboard-update-daily \
    --targets "Id"="1","Arn"="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:dashboard-handler" \
    --region ${REGION}

aws lambda add-permission \
    --function-name dashboard-handler \
    --statement-id dashboard-update-daily \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/dashboard-update-daily \
    --region ${REGION}

echo "✅ Dashboard schedule created"

# Rule 4: Alerts Monitoring (Every 5 minutes)
aws events put-rule \
    --name alerts-monitor-5min \
    --schedule-expression "cron(0/5 * * * ? *)" \
    --description "Monitor alerts every 5 minutes" \
    --region ${REGION}

aws events put-targets \
    --rule alerts-monitor-5min \
    --targets "Id"="1","Arn"="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:alerts-handler" \
    --region ${REGION}

aws lambda add-permission \
    --function-name alerts-handler \
    --statement-id alerts-monitor-5min \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/alerts-monitor-5min \
    --region ${REGION}

echo "✅ Alerts monitoring schedule created"

# Rule 5: ML Retraining (Weekly - Sunday 00:00 UTC / 8:00 AM SGT)
aws events put-rule \
    --name ml-training-weekly \
    --schedule-expression "cron(0 0 ? * SUN *)" \
    --description "Weekly ML Model Retraining" \
    --region ${REGION}

aws events put-targets \
    --rule ml-training-weekly \
    --targets "Id"="1","Arn"="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:ml-trainer-handler" \
    --region ${REGION}

aws lambda add-permission \
    --function-name ml-trainer-handler \
    --statement-id ml-training-weekly \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/ml-training-weekly \
    --region ${REGION}

echo "✅ ML Training schedule created"

echo ""
echo "🎉 All EventBridge schedules created successfully!"