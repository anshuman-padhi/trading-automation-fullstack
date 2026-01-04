# QuantZ Trading Automation System 🚀

Comprehensive automated trading system deploying a Momentum + Regime-Based Strategy on AWS.

## 📚 Documentation
> **[Start Here for Detailed Strategy & Deployment Guide](docs/00-START-HERE/README.md)**

*   **Strategy Bible**: [Complete Optimized Trading System](docs/05-Reference/COMPLETE-OPTIMIZED-TRADING-SYSTEM-2026.md)
*   **Deployment Guide**: [AWS Lambda Deployment](docs/02-Implementation/AWS_LAMBDA_DEPLOYMENT_GUIDE.md)

## System Architecture

### Strategy
*   **Core Logic**: Momentum Breakout with Regime Filtering.
*   **Regime Detection**: Market Analysis (SPY Trend, Breadth, VIX) determines exposure.
    *   Regime A (Bull): 100% Exposure
    *   Regime B (Neutral): 50% Exposure
    *   Regime C (Bear): 10% Exposure
*   **Exit Strategy**: 15% Training Stop (Price-based), Dynamic Exposure Scaling.

### Infrastructure (AWS Serverless)
*   **Compute**: AWS Lambda (x6 Functions)
    *   `market-analysis-handler`: Weekly Regime Check.
    *   `stock-screener-handler`: Daily Stock Scanner (Docker Container).
    *   `ml-trainer-handler`: Weekly Model Retraining (Docker Container).
    *   `position-sizer-handler`: Calculates position sizes based on capital/regime.
    *   `trade-journal-handler`: Logs trades to S3/DynamoDB.
    *   `dashboard-handler`: Generates Performance Reports.
*   **Orchestration**: EventBridge (Cron Schedules).
*   **Storage**: S3 (Data/Models), DynamoDB (State).

## Deployment

### Prerequisites
*   `podman` (for Docker images due to licensing/preference)
*   `uv` (Python dependency management)
*   `aws-cli` (configured with credentials)

### Quick Start
1.  **Run Unit Tests**:
    ```bash
    uv run pytest tests/
    ```
2.  **Build Docker Images**:
    ```bash
    ./aws/scripts/build_docker.sh
    ```
3.  **Deploy Lambda Functions**:
    ```bash
    ./aws/scripts/deploy_functions.sh
    ```
4.  **Configure Schedules**:
    ```bash
    ./aws/scripts/setup_eventbridge.sh
    ```

## Monitoring
*   **Logs**: Check CloudWatch Logs for each Lambda function (Search `/aws/lambda/`).
*   **Daily Report**: Check email for "Daily Dashboard" or "Market Analysis" at 8PM SGT / 6AM SGT respectively.
*   **Alerts**: System sends email alerts for Trade Execution and Errors.

## Development
*   **Strategy Code**: `src/modules/backtester.py` (Core Logic)
*   **Handlers**: `aws/lambda/`
*   **Scripts**: `aws/scripts/`

---
*Project Status: Deployed & Live (Jan 2026)*
