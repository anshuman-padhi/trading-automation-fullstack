# START_TOMORROW_MORNING.md
## Day 1 Execution Guide: Project Kickoff
**Date:** [Tomorrow's Date]
**Objective:** Go from "Zero" to "Code Running" by 5:00 PM.

---

## 08:00 AM - 09:00 AM: THE SETUP (Coffee & Console)
**Goal:** A fully configured development environment.

1.  **Open Terminal** on your Mac.
2.  **Check Python:** `python3 --version`. If < 3.9, install latest via `brew install python`.
3.  **Configure AWS:**
    *   Log into AWS Console -> IAM -> Users -> Create User `admin-dev` -> Attach Policy `AdministratorAccess`.
    *   Create Access Keys for `admin-dev`. Copy Key ID and Secret.
    *   Run `aws configure` in terminal and paste credentials.
4.  **Create Project:**
    ```bash
    mkdir -p ~/workspace/quantx/my_trading_desk/trading-automation
    cd ~/workspace/quantx/my_trading_desk/trading-automation
    git init
    python3 -m venv venv
    source venv/bin/activate
    ```
5.  **Install Libraries:**
    ```bash
    pip install boto3 yfinance pandas numpy pytest
    pip freeze > requirements.txt
    ```

## 09:00 AM - 10:00 AM: SCAFFOLDING (Structure)
**Goal:** Create the skeleton of your application.

1.  **Create Folders:**
    ```bash
    mkdir -p src/modules src/handlers src/utils data/local tests scripts
    ```
2.  **Create Placeholders:**
    *   `touch src/modules/__init__.py`
    *   `touch src/handlers/__init__.py`
    *   `touch src/utils/__init__.py`
    *   `touch .gitignore` (Add `venv/`, `*.pyc`, `.env`, `data/local/`)

## 10:00 AM - 12:00 PM: MODULE 1 (Market Analysis)
**Goal:** Write the code that checks market health.

1.  **Create File:** `src/modules/market_analysis.py`.
2.  **Implement Class:** `MarketAnalyzer`.
    *   Method `get_data()`: Fetch SPY, QQQ, VIX using `yfinance`.
    *   Method `analyze_trend()`: Calculate SMA50, SMA200. Return "Uptrend" or "Downtrend".
    *   Method `classify_environment()`: Logic for A, B, C, D environments.
3.  **Test Locally:** Create `scripts/test_market.py` and run it. Ensure it prints the correct environment based on today's chart.

## 12:00 PM - 01:00 PM: LUNCH BREAK
*   Step away from the screen.
*   Clear your head.

## 01:00 PM - 03:00 PM: MODULE 3 (Position Sizing)
**Goal:** Write the risk calculator.

1.  **Create File:** `src/modules/position_sizer.py`.
2.  **Implement Class:** `PositionSizer`.
    *   Input: Account Size, Entry Price, Stop Price, Environment (A-D).
    *   Logic: Calculate risk % based on Environment (e.g., A=0.50%, B=0.40%).
    *   Output: Number of shares to buy.
3.  **Test Locally:** Run a few manual scenarios.
    *   *Scenario:* $50k account, Env A, Entry $150, Stop $145. Result should be safe size.

## 03:00 PM - 04:30 PM: AWS LAMBDA PREP
**Goal:** Prepare for cloud deployment (Deployment happens Day 2, but prep today).

1.  **Create S3 Bucket:**
    ```bash
    aws s3 mb s3://trading-automation-data-[your-name]
    ```
2.  **Create IAM Role:** Create a role `TradingLambdaRole` in AWS Console with permissions for S3 and CloudWatch Logs.

## 04:30 PM - 05:00 PM: CLEANUP & COMMIT
**Goal:** Save progress.

1.  **Run Tests:** Ensure your local scripts still run without errors.
2.  **Git Commit:**
    ```bash
    git add .
    git commit -m "Day 1 Complete: Setup, Market Analysis, Position Sizing modules initialized"
    ```
3.  **Review:** Check `task.md` and mark Module 1 logic as "In Progress" or "Local Complete".

---

**TROUBLESHOOTING CHEATSHEET**
*   **"Module not found":** Run `export PYTHONPATH=$PYTHONPATH:$(pwd)` in terminal.
*   **"AWS Access Denied":** Re-check `aws configure` credentials.
*   **"yfinance error":** Update library `pip install yfinance --upgrade`.

**You are ready. Good luck.**
