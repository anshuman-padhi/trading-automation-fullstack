# AWS Trading Automation Deployment Guide

**Last Updated:** January 4, 2026
**System Version:** 2.0 (Hybrid Lambda + Docker Architecture)

---

## 🏗 System Architecture

The system **utilizes** a **Hybrid Lambda Architecture** to balance cost and performance:

| Function | Type | Runtime | Why? |
|----------|------|---------|------|
| **`market-analysis-handler`** | Zip | Python 3.11 | Lightweight, I/O bound. |
| **`stock-screener-handler`** | **Docker** | Python 3.11 | Heavy memory usage (Pandas/TA-Lib), requires 5GB+ RAM. |
| **`ml-trainer-handler`** | **Docker** | Python 3.11 | ML dependencies (Scikit-learn), long execution time. |
| **`position-sizer-handler`** | Zip | Python 3.11 | Ultra-lightweight logic. |
| **`trade-journal-handler`** | Zip | Python 3.11 | Simple API operations. |
| **`dashboard-handler`** | Zip | Python 3.11 | Data aggregation. |
| **`alerts-handler`** | Zip | Python 3.11 | Low latency polling. |

---

## 🛠 Prerequisites

1.  **Tools Configured**:
    *   `aws-cli` (v2+)
    *   `podman` (for building Docker images)
    *   `uv` (for Python dependencies)
2.  **Environment Variables**:
    *   Ensure `.env` exists in root with:
        *   `ALPACA_API_KEY`
        *   `ALPACA_SECRET_KEY`
        *   `S3_BUCKET` (e.g., `trading-automation-data-904583676284`)
        *   `ACCOUNT_ID`

---

## 🚀 Deployment Instructions

### 1. Build & Push Docker Images
Because `stock-screener` and `ml-trainer` run on Docker, their images must be built and pushed to AWS ECR first.

**Command:**
```bash
./aws/scripts/build_docker.sh
```
*What this does:*
*   Logs into ECR.
*   Builds the `stock-screener` image.
*   Pushes it to your private ECR repository.

### 2. Deploy Lambda Functions
**Packages** Zip functions, **creates/updates** Lambda configs, and **wires up** the Docker images using this utility script.

**Command:**
```bash
./aws/scripts/deploy_functions.sh
```
*What this does:*
*   Packages `src/modules` into `trading-automation-deps` Layer.
*   Deploys Zip-based functions.
*   Deploys Docker-based functions (`stock-screener`, `ml-trainer`) using the image from Step 1.
*   Updates environment variables.

### 3. Configure EventBridge Schedules
**Configures** the cron jobs that drive the automation.

**Command:**
```bash
./aws/scripts/setup_eventbridge.sh
```

**Schedule Overvew:**
*   **Weekly Analysis**: Sundays @ 6:00 PM UTC (`market-analysis`)
*   **Daily Screener**: Weekdays @ 4:15 PM UTC (`stock-screener`)
*   **Daily Dashboard**: Daily @ 8:00 PM UTC (`dashboard`)
*   **Alerts**: Every 5 minutes (`alerts-monitor`)

---

## 🧪 Verification

### Check CloudWatch Logs
Go to AWS Console -> CloudWatch -> Log Groups.
Look for:
*   `/aws/lambda/market-analysis-handler`
*   `/aws/lambda/stock-screener-handler`

### Manual Trigger
You can manually trigger any function via CLI to test:

```bash
# Test Market Analysis
aws lambda invoke --function-name market-analysis-handler response.json

# Test Position Sizer (API style)
aws lambda invoke --function-name position-sizer-handler \
  --payload '{"account_size": 50000, "risk_pct": 0.01}' \
  response.json
```

---

## 🔄 Updating Code

*   **Logic Change (Python Code)**: Run `./aws/scripts/deploy_functions.sh`.
*   **Dependency Change**: Run `./aws/scripts/deploy_layer.sh` then deploy functions.
*   **Docker Change**: Run `./aws/scripts/build_docker.sh` then deploy functions.
