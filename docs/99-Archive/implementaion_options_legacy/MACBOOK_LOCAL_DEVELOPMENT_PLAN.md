# MACBOOK_LOCAL_DEVELOPMENT_PLAN.md
## Mac Local Development → AWS Lambda Deployment Protocol
**Version: 1.0 | January 1, 2026**
**Objective:** Execute Hybrid Path B (Weeks 1-8) successfully using MacBook Pro as the primary development station.

---

## 1. ENVIRONMENT ARCHITECTURE

### The Workflow
1.  **Code Locally:** Write & test Python code on your MacBook Pro.
2.  **Version Control:** Git commits locally.
3.  **Validate:** Run unit tests locally (`pytest`).
4.  **Deploy:** Push verified code to AWS Lambda using AWS CLI or scripts.
5.  **Data:** Application stores data in S3 (production) or local CSVs (dev/test).

### The Stack
*   **Hardware:** MacBook Pro (Apple Silicon/Intel)
*   **OS:** macOS
*   **Language:** Python 3.9+
*   **IDE:** VS Code
*   **Cloud:** AWS Lambda, S3, EventBridge, SES
*   **CLI Tools:** AWS CLI v2, Git, Python venv

---

## 2. WEEK-BY-WEEK EXECUTION PLAN

### WEEK 1: Foundation & Market Analysis Module
*   **Goal:** Get the infrastructure up and Module 1 running in the cloud.
*   **Mon:** Setup Dev Environment (Python, AWS CLI, Git). Create project structure.
*   **Tue:** Code `MarketAnalyzer` module locally. Test with `yfinance`.
*   **Wed:** Create AWS S3 buckets. Configure IAM roles for Lambda.
*   **Thu:** Create & Deploy `market_analysis_handler` Lambda function.
*   **Fri:** Setup EventBridge scheduler (Sunday trigger). Verify SES email sending.

### WEEK 2: Stock Screening & Watchlists
*   **Goal:** Automate the daily search for high-potential stocks.
*   **Mon:** Code `StockScreener` module locally. Implement T.I.G.E.R.S logic.
*   **Tue:** Connect to data sources (Yahoo Finance/AlphaVantage).
*   **Wed:** Create & Deploy `stock_screener_handler` Lambda.
*   **Thu:** Configure daily cron trigger (4:15 PM EST).
*   **Fri:** Validate CSV output format in S3.

### WEEK 3: Position Sizing & Risk Management
*   **Goal:** Automate the math to protect capital.
*   **Mon:** Code `PositionSizer` module. Implement ATR & Heat logic.
*   **Tue:** Create API-like Lambda handler (invokable on demand).
*   **Wed:** Write local scripts to invoke this calculator quickly.
*   **Thu:** Stress test with various account sizes/scenarios.
*   **Fri:** Documentation & Cheat Sheet creation.

### WEEK 4: Journaling & Dashboarding
*   **Goal:** Capture data and visualize it.
*   **Mon:** Code `TradeJournal` module (S3 CSV append logic).
*   **Tue:** Code `PerformanceDashboard` (calculates stats from Journal CSV).
*   **Wed:** Deploy Journal & Dashboard Lambdas.
*   **Thu:** Create a simple script to upload local trades to the system.
*   **Fri:** **FULL SYSTEM TEST.** Verify all 6 modules work together.

---

## 3. EXACT CONFIGURATION COMMANDS (Copy-Paste)

### Step 1: Install Tools (Terminal)
```bash
# Install Homebrew (if not present)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python & AWS CLI
brew install python
brew install awscli
brew install git

# Verify installations
python3 --version
aws --version
git --version
```

### Step 2: Configure AWS CLI
```bash
aws configure
# AWS Access Key ID: [Your Key]
# AWS Secret Access Key: [Your Secret]
# Default region name: us-east-1
# Default output format: json

# Verify connection
aws s3 ls
```

### Step 3: Project Structure Setup
```bash
# Create main directory
mkdir -p ~/workspace/quantx/my_trading_desk/trading-automation
cd ~/workspace/quantx/my_trading_desk/trading-automation

# Initialize Git
git init

# Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install Dependencies
pip install boto3 pandas yfinance numpy pytest

# Freeze requirements
pip freeze > requirements.txt
```

### Step 4: Directory Hierarchy
```bash
mkdir -p src/modules         # Core logic (MarketAnalysis, Screener)
mkdir -p src/handlers        # Lambda handlers
mkdir -p src/utils           # AWS helpers (S3, SES)
mkdir -p tests               # Unit tests
mkdir -p scripts             # Deployment scripts
mkdir -p data/local          # Local CSV storage for testing
```

---

## 4. DEPLOYMENT WORKFLOW (The "Deploy" Script)

We will create a simple shell script (`deploy.sh`) to package and update Lambda functions from your Mac.

**File: `scripts/deploy.sh`**
```bash
#!/bin/bash
FUNCTION_NAME=$1
ZIP_FILE="function.zip"

echo "Deploying $FUNCTION_NAME..."

# 1. Prepare package
cd venv/lib/python3.9/site-packages
zip -r9 ../../../../$ZIP_FILE .
cd ../../../..
zip -g $ZIP_FILE src/modules/*.py
zip -g $ZIP_FILE src/utils/*.py
zip -g $ZIP_FILE src/handlers/$FUNCTION_NAME.py

# 2. Upload to AWS
aws lambda update-function-code --function-name trading-$FUNCTION_NAME --zip-file fileb://$ZIP_FILE

# 3. Cleanup
rm $ZIP_FILE
echo "Done!"
```

**Usage:**
```bash
./scripts/deploy.sh market_analysis_handler
```

---

## 5. LOCAL TESTING PROTOCOL

Before deploying, **ALWAYS** run this check:

1.  **Unit Test:**
    ```bash
    pytest tests/test_market_analyzer.py
    ```
2.  **Local Run:**
    Create a `run_local.py` driver:
    ```python
    from src.modules.market_analysis import MarketAnalyzer
    analyzer = MarketAnalyzer()
    analyzer.run() # Should print results to console/local CSV
    ```
    Execute: `python run_local.py`

3.  **Check Output:** Verify `data/local/market_analysis_log.csv` exists and looks correct.

---

## 6. S3 DATA STRUCTURE (Production)

Your S3 bucket (`trading-system-prod`) will mirror this structure:

*   `/market_analysis/` -> `YYYY-MM-DD.json` (Weekly analysis)
*   `/watchlists/` -> `YYYY-MM-DD_watchlist.csv` (Daily screens)
*   `/journal/` -> `master_journal.csv` (The source of truth)
*   `/metrics/` -> `dashboard_stats.json` (Calculated daily)

---

## 7. NEXT STEPS (Tomorrow Morning)

1.  **Open Terminal.**
2.  **Navigate** to `~/workspace/quantx/my_trading_desk/`.
3.  **Run** the commands in "Step 3: Project Structure Setup".
4.  **Create** `src/modules/market_analysis.py`.
5.  **Write** your first 50 lines of code.

**Status:** READY TO BUILD.
