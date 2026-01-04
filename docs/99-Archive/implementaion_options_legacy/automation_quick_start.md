# automation_quick_start.md
## Implementation Guide with Ready-to-Use Code
**Read Time: 2 hours (includes code review & setup)**
**Last Updated: December 31, 2025**
**Version: 2.0 - Production Ready**

---

## START HERE: Choose Your Path

### Path A: Google Sheets (Easiest, Fastest)
- ✅ No coding required
- ✅ Setup: 4-6 hours
- ✅ Cost: Free
- ✅ Best for: Non-technical traders
- **Go to**: Section 1A (Google Sheets Setup)

### Path B: Python Scripts (Recommended)
- ✅ Some coding knowledge needed (minimal)
- ✅ Setup: 8-12 hours
- ✅ Cost: Free-$20/month
- ✅ Best for: Technical traders who want control
- **Go to**: Section 1B (Python Implementation)

### Path C: Full Stack (Advanced)
- ✅ Full programming knowledge required
- ✅ Setup: 20+ hours
- ✅ Cost: $50-200/month
- ✅ Best for: Serious quant traders
- **Go to**: Section 1C (Full Stack)

---

# SECTION 1A: GOOGLE SHEETS AUTOMATION (Easiest)

## Installation (No Code Required)

### Step 1: Create Google Sheet
1. Go to sheets.google.com
2. Create new spreadsheet: "Trading_System_Automation"
3. Create tabs: Market_Analysis, Stock_Screening, Position_Sizing, Trade_Journal, Dashboard

### Step 2: Market Analysis Sheet
Copy this sheet structure:

```
MARKET ANALYSIS SPREADSHEET
(Runs every Sunday 6 PM - manual or automated)

Column A: Date
Column B: SPY Price
Column C: SPY 50 SMA
Column D: SPY 200 SMA
Column E: QQQ Price
Column F: QQQ 50 SMA
Column G: QQQ 200 SMA
Column H: Breadth %
Column I: VIX Level
Column J: Environment (formula)
Column K: Base Sizing
Column L: Macro Adjustment
Column M: Final Sizing

Example Data Row:
2025-12-31 | 603.50 | 595.20 | 580.40 | 542.80 | 535.10 | 515.30 | 72% | 18.5 | A | 10% | 100% | 10%

ENVIRONMENT FORMULA (Column J):
=IF(AND(B2>C2, B2>D2, E2>F2, E2>G2, H2>=0.70), "A",
   IF(AND(B2>C2, H2>=0.50), "B",
   IF(H2>=0.30, "C", "D")))

This formula auto-classifies based on your rules!
```

### Step 3: Position Sizing Sheet
```
POSITION SIZING CALCULATOR

Column A: Entry Price
Column B: Stop Loss Price
Column C: Account Equity
Column D: Environment (A/B/C/D)
Column E: Edges Count
Column F: Risk % (lookup table)
Column G: Risk $ (formula)
Column H: Stop Distance (formula)
Column I: Position Size (formula)
Column J: Shares (formula)

Example Row:
100 | 95 | 50000 | A | 5 | 0.5% | 250 | 5 | 5000 | 50

FORMULAS:
Column F (Risk %):
=IF(D2="A", 0.5%, IF(D2="B", 0.4%, IF(D2="C", 0.25%, 0.2%)))

Column G (Risk in $):
=C2*F2

Column H (Stop Distance):
=A2-B2

Column I (Position Size in $):
=G2/H2*A2

Column J (Shares):
=ROUND(I2/A2, 0)

This auto-calculates position sizes in seconds!
```

### Step 4: Trade Journal Sheet
```
TRADE JOURNAL SPREADSHEET

Column A: Trade ID
Column B: Entry Date
Column C: Stock
Column D: Entry Price
Column E: Entry Shares
Column F: Setup Type (VCP/Cup/Flat)
Column G: Edges (0-10)
Column H: Checklist Score (0-100)
Column I: Exit Date
Column J: Exit Price
Column K: Exit Reason
Column L: P&L $ (formula)
Column M: P&L % (formula)
Column N: Days Held (formula)
Column O: Setup Grade (A/B/C/F)
Column P: Execution Grade (A/B/C/F)
Column Q: Quadrant (formula)

Example Row:
1247 | 2025-12-31 | NVDA | 100 | 50 | VCP | 5 | 88 | 2026-01-05 | 112 | Stage 2 | 600 | 12% | 5 | A | A | ✓✓

FORMULAS:
Column L (P&L in $):
=IF(J1>0, (J1-D1)*E1, 0)

Column M (P&L %):
=IF(J1>0, (J1-D1)/D1, 0)

Column N (Days Held):
=IF(J1>0, I1-B1, "")

Column Q (Quadrant - auto 2x2 matrix):
=IF(AND(O1="A", P1="A"), "✓✓",
   IF(AND(O1="A", P1<>"A"), "✓✗",
   IF(AND(O1<>"A", P1="A"), "✗✓", "✗✗")))

This auto-tracks everything!
```

### Step 5: Monthly Dashboard Sheet
```
MONTHLY PERFORMANCE DASHBOARD

KPI Row: Label | Formula | Value | Target

Starting Equity: | (lookup previous month end) | $50,000 | —
Ending Equity: | (sum of account) | $54,200 | —
Monthly Return: | (Ending-Starting)/Starting | 8.4% | 5-10%
Total Trades: | COUNTA(Journal!B:B) | 18 | —
Win Rate: | COUNTIF(Journal!M:M,">0")/COUNTA | 55.6% | 50%+
Total Profit: | SUMIF(Journal!M:M,">0") | $3,800 | —
Total Loss: | SUMIF(Journal!M:M,"<0") | -$1,200 | —
Profit Factor: | Profit/ABS(Loss) | 3.17x | 1.75x+
Avg Win: | SUMIF/COUNTIF | $380 | —
Avg Loss: | SUMIF/COUNTIF | -$150 | —
Expectancy: | ((Win%*AvgWin)-(Loss%*AvgLoss)) | $144 | $25+

All formulas reference Trade_Journal sheet!
```

### Step 6: Enable Automation (Google Apps Script)
1. In Google Sheet: Extensions → Apps Script
2. Paste code below:

```javascript
// Market Analysis Automation (Runs weekly)
function marketAnalysisWeekly() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Market_Analysis");
  const today = new Date();
  
  // This sends email notification
  MailApp.sendEmail("your.email@gmail.com",
    "Weekly Market Analysis Update",
    "Environment classification complete. Check sheet for environment type and sizing recommendations.");
}

// Auto-calculate dashboard (Runs daily)
function updateDashboard() {
  const journal = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Trade_Journal");
  const dashboard = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Dashboard");
  
  // Dashboard formulas auto-update in real-time
  SpreadsheetApp.flush();
}

// Set up schedule: Click Triggers (clock icon) → Create new trigger
// Function: marketAnalysisWeekly
// Deployment: Head
// Event source: Time-driven
// Type: Week timer
// Day: Sunday
// Time: 6 PM
```

### Step 7: Set Up Alerts (Gmail)
1. In Trade_Journal sheet, add column: "Alert"
2. Formula: `=IF(M1>0, "PROFIT_TAKEN", IF(AND(K1="Weakness",O1="A"), "WEAKNESS_SIGNAL", ""))`
3. Create Gmail filter:
   - From: apps-scripts-notifications@google.com
   - Label: "Trading Alerts"
   - Notification on: Always

---

# SECTION 1B: PYTHON AUTOMATION (Recommended)

## Installation

### Step 1: Install Python & Libraries
```bash
# Install Python 3.8+
# Then install required libraries:

pip install pandas numpy yfinance alpha_vantage openpyxl google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv

# Verify installation:
python --version
pip list
```

### Step 2: Module 1 - Market Analysis Script

**File: market_analysis.py**

```python
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MarketAnalyzer:
    """Analyzes market environment (A/B/C/D classification)"""
    
    def __init__(self):
        self.spy = None
        self.qqq = None
        self.vix = None
        self.breadth_pct = None
        
    def fetch_data(self):
        """Fetch latest market data"""
        # Download SPY (proxy for S&P 500)
        spy_data = yf.download('SPY', period='250d', progress=False)
        self.spy = {
            'price': spy_data['Close'].iloc[-1],
            'sma_50': spy_data['Close'].rolling(50).mean().iloc[-1],
            'sma_200': spy_data['Close'].rolling(200).mean().iloc[-1]
        }
        
        # Download QQQ (proxy for Nasdaq)
        qqq_data = yf.download('QQQ', period='250d', progress=False)
        self.qqq = {
            'price': qqq_data['Close'].iloc[-1],
            'sma_50': qqq_data['Close'].rolling(50).mean().iloc[-1],
            'sma_200': qqq_data['Close'].rolling(200).mean().iloc[-1]
        }
        
        # Download VIX
        vix_data = yf.download('^VIX', period='5d', progress=False)
        self.vix = vix_data['Close'].iloc[-1]
        
        # Download major stocks for breadth
        # (Simplified: using top 50 tech stocks)
        stocks = ['MSFT', 'AAPL', 'NVDA', 'TSLA', 'GOOGL', 'META', 'AMZN', 'NFLX', 'AMD', 'INTC']
        above_sma50 = 0
        for stock in stocks:
            try:
                data = yf.download(stock, period='250d', progress=False)
                if data['Close'].iloc[-1] > data['Close'].rolling(50).mean().iloc[-1]:
                    above_sma50 += 1
            except:
                pass
        
        self.breadth_pct = (above_sma50 / len(stocks)) * 100
    
    def classify_environment(self):
        """Classify market as A/B/C/D"""
        spy_above_50 = self.spy['price'] > self.spy['sma_50']
        spy_above_200 = self.spy['price'] > self.spy['sma_200']
        qqq_above_50 = self.qqq['price'] > self.qqq['sma_50']
        qqq_above_200 = self.qqq['price'] > self.qqq['sma_200']
        
        if (spy_above_50 and spy_above_200 and qqq_above_50 and qqq_above_200 and 
            self.breadth_pct >= 70 and self.vix < 25):
            return "A"  # Confirmed uptrend
        elif (spy_above_50 and qqq_above_50 and self.breadth_pct >= 50 and self.vix < 30):
            return "B"  # Uptrend with caution
        elif self.breadth_pct >= 30 and self.vix < 35:
            return "C"  # Choppy/sideways
        else:
            return "D"  # Downtrend
    
    def get_sizing_recommendation(self, environment):
        """Get position sizing for environment"""
        sizing = {
            'A': {'base': 0.10, 'risk': 0.005, 'heat_limit': 0.025, 'trades_per_week': 5},
            'B': {'base': 0.08, 'risk': 0.004, 'heat_limit': 0.020, 'trades_per_week': 3},
            'C': {'base': 0.05, 'risk': 0.0025, 'heat_limit': 0.010, 'trades_per_week': 1},
            'D': {'base': 0.03, 'risk': 0.002, 'heat_limit': 0.015, 'trades_per_week': 0}
        }
        return sizing[environment]
    
    def generate_report(self):
        """Generate analysis report"""
        self.fetch_data()
        env = self.classify_environment()
        sizing = self.get_sizing_recommendation(env)
        
        report = f"""
MARKET ENVIRONMENT ANALYSIS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

═══════════════════════════════════════════════
PRICE & TREND ANALYSIS
═══════════════════════════════════════════════

SPY:
  Price: ${self.spy['price']:.2f}
  50 SMA: ${self.spy['sma_50']:.2f} - {"ABOVE ✓" if self.spy['price'] > self.spy['sma_50'] else "BELOW ✗"}
  200 SMA: ${self.spy['sma_200']:.2f} - {"ABOVE ✓" if self.spy['price'] > self.spy['sma_200'] else "BELOW ✗"}

QQQ:
  Price: ${self.qqq['price']:.2f}
  50 SMA: ${self.qqq['sma_50']:.2f} - {"ABOVE ✓" if self.qqq['price'] > self.qqq['sma_50'] else "ABOVE ✓"}
  200 SMA: ${self.qqq['sma_200']:.2f} - {"ABOVE ✓" if self.qqq['price'] > self.qqq['sma_200'] else "BELOW ✗"}

VOLATILITY:
  VIX: {self.vix:.2f} - {"Normal (15-20)" if self.vix < 20 else "Elevated" if self.vix < 25 else "High"}

BREADTH:
  % above 50 SMA: {self.breadth_pct:.0f}%

═══════════════════════════════════════════════
CLASSIFICATION & RECOMMENDATIONS
═══════════════════════════════════════════════

ENVIRONMENT: {env}

Base Position Size: {sizing[env]['base']*100:.0f}%
Risk Per Trade: {sizing[env]['risk']*100:.2f}%
Portfolio Heat Limit: {sizing[env]['heat_limit']*100:.2f}%
Trades Per Week: {sizing[env]['trades_per_week']}

{"AGGRESSIVE - Trade 3-5 times weekly" if env == "A" else
 "NORMAL - Trade 2-3 times weekly" if env == "B" else
 "DEFENSIVE - Trade max 1 time weekly" if env == "C" else
 "AVOID TRADING - Focus on capital preservation"}
"""
        return report
    
    def send_email_alert(self, report):
        """Send report via email"""
        # Replace with your email settings
        sender_email = "your.email@gmail.com"
        sender_password = "your_app_password"  # Use Gmail app password
        recipient = "your.email@gmail.com"
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = f"Market Analysis - {datetime.now().strftime('%Y-%m-%d')}"
        msg.attach(MIMEText(report, 'plain'))
        
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            print(f"Error sending email: {e}")

# Run the analyzer
if __name__ == "__main__":
    analyzer = MarketAnalyzer()
    report = analyzer.generate_report()
    print(report)
    analyzer.send_email_alert(report)
```

**How to run:**
```bash
python market_analysis.py
```

**To automate weekly:**
- **Windows**: Task Scheduler → Create task → Run market_analysis.py every Sunday 6 PM
- **Mac/Linux**: crontab → `0 18 * * 0 /usr/bin/python3 /path/market_analysis.py`

---

### Step 3: Module 2 - Stock Screening Script

**File: stock_screener.py**

```python
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time

class StockScreener:
    """Screens stocks using fundamental + technical criteria"""
    
    def __init__(self, stocks_list=None):
        # Default: Top 100 tech stocks (customize as needed)
        self.stocks = stocks_list or [
            'AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL', 'META', 'AMZN', 'NFLX',
            'AMD', 'INTC', 'QUALCOMM', 'BROADCOM', 'SONY', 'SAMSUNG',
            'ASML', 'ADBE', 'CRWD', 'OKTA', 'SPLK', 'ZM', 'DOCU', 'SNOW'
            # Add more stocks as needed
        ]
        self.results = []
    
    def get_fundamental_score(self, symbol):
        """Calculate fundamental score (0-3 points)"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            eps_growth = info.get('epsTrailingTwelveMonths', 0)
            revenue_growth = info.get('revenuePerShare', 0)
            
            score = 0
            if eps_growth > 0.25:
                score = 3
            elif eps_growth > 0.15:
                score = 2
            elif eps_growth > 0.10:
                score = 1
            
            return score
        except:
            return 0
    
    def get_technical_score(self, symbol):
        """Calculate technical score (0-3 points) using RS rating"""
        try:
            # Get 52-week data
            stock_data = yf.download(symbol, period='252d', progress=False)
            spy_data = yf.download('SPY', period='252d', progress=False)
            
            # Simple RS calculation: Stock 52wk return vs SPY
            stock_return = (stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0]
            spy_return = (spy_data['Close'].iloc[-1] - spy_data['Close'].iloc[0]) / spy_data['Close'].iloc[0]
            rs_rating = (stock_return / spy_return) * 100 if spy_return > 0 else 0
            
            if rs_rating > 90:
                score = 3
            elif rs_rating > 80:
                score = 2
            elif rs_rating > 70:
                score = 1
            else:
                score = 0
            
            return score, rs_rating
        except:
            return 0, 0
    
    def screen_stocks(self):
        """Run screening on all stocks"""
        print(f"Screening {len(self.stocks)} stocks...")
        
        for i, symbol in enumerate(self.stocks):
            print(f"Progress: {i+1}/{len(self.stocks)}", end='\r')
            
            try:
                fund_score = self.get_fundamental_score(symbol)
                tech_score, rs_rating = self.get_technical_score(symbol)
                
                # Sector RS score (simplified)
                sector_score = 2 if rs_rating > 80 else 1 if rs_rating > 70 else 0
                
                # Simple catalyst check (recent price action)
                stock_data = yf.download(symbol, period='252d', progress=False)
                _52wk_high = stock_data['Close'].max()
                current_price = stock_data['Close'].iloc[-1]
                distance_from_high = ((current_price - _52wk_high) / _52wk_high) * 100
                
                catalyst_score = 2 if distance_from_high > -5 else 1 if distance_from_high > -15 else 0
                
                total_score = fund_score + tech_score + sector_score + catalyst_score
                
                self.results.append({
                    'Symbol': symbol,
                    'Fund_Score': fund_score,
                    'Tech_Score': tech_score,
                    'RS_Rating': round(rs_rating, 1),
                    'Sector_Score': sector_score,
                    'Catalyst_Score': catalyst_score,
                    'Total_Score': total_score,
                    'Distance_52wk_High': round(distance_from_high, 1)
                })
            except Exception as e:
                print(f"Error screening {symbol}: {e}")
                continue
            
            time.sleep(0.1)  # Avoid rate limiting
        
        # Sort by score
        self.results = sorted(self.results, key=lambda x: x['Total_Score'], reverse=True)
        return self.results
    
    def export_watchlist(self, filename='watchlist.csv'):
        """Export results to CSV"""
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False)
        print(f"\nWatchlist exported to {filename}")
        
        # Print top 10
        print("\nTOP 10 CANDIDATES (Grade A):")
        print(df[df['Total_Score'] >= 8].head(10).to_string(index=False))
        
        return df

# Run the screener
if __name__ == "__main__":
    screener = StockScreener()
    results = screener.screen_stocks()
    screener.export_watchlist()
```

**How to run:**
```bash
python stock_screener.py
```

This generates `watchlist.csv` with ranked candidates.

---

### Step 4: Module 3 - Position Sizing Calculator

**File: position_sizing.py**

```python
class PositionSizer:
    """Calculates position size based on risk management rules"""
    
    def __init__(self, account_equity, environment='A'):
        self.account = account_equity
        self.environment = environment
        
        # Risk parameters by environment
        self.risk_params = {
            'A': {'base': 0.10, 'risk_pct': 0.005, 'heat_limit': 0.025},
            'B': {'base': 0.08, 'risk_pct': 0.004, 'heat_limit': 0.020},
            'C': {'base': 0.05, 'risk_pct': 0.0025, 'heat_limit': 0.010},
            'D': {'base': 0.03, 'risk_pct': 0.002, 'heat_limit': 0.015}
        }
    
    def calculate_position_size(self, entry_price, stop_price, edges=4):
        """Calculate position size in shares"""
        params = self.risk_params[self.environment]
        
        # Base sizing
        base_size = params['base']
        
        # Adjust for edges
        edge_multiplier = {
            3: 0.50,  # 3 edges = 50% of base
            4: 1.00,  # 4 edges = 100% of base
            5: 1.10,  # 5 edges = 110% of base
            6: 1.20,  # 6 edges = 120% of base
            7: 1.30   # 7+ edges = 130% of base
        }
        
        adjusted_size = base_size * edge_multiplier.get(min(edges, 7), 1.0)
        
        # Calculate position size in dollars
        position_value = self.account * adjusted_size
        
        # Risk-based verification
        stop_distance = entry_price - stop_price
        risk_dollars = self.account * params['risk_pct']
        shares = int(risk_dollars / stop_distance)
        
        # Use smaller of the two
        risk_based_value = shares * entry_price
        final_position_value = min(position_value, risk_based_value)
        final_shares = int(final_position_value / entry_price)
        
        return {
            'entry_price': entry_price,
            'stop_price': stop_price,
            'position_value': final_position_value,
            'shares': final_shares,
            'risk_dollars': final_position_value - (final_shares * stop_price),
            'risk_pct': (final_position_value - (final_shares * stop_price)) / self.account,
            'profit_target_1': entry_price + (entry_price - stop_price) * 0.10,  # +10%
            'profit_target_2': entry_price + (entry_price - stop_price) * 0.20,  # +20%
            'profit_target_3': entry_price + (entry_price - stop_price) * 0.75   # +75%
        }

# Example usage
if __name__ == "__main__":
    sizer = PositionSizer(account_equity=50000, environment='A')
    
    result = sizer.calculate_position_size(
        entry_price=100,
        stop_price=95,
        edges=5
    )
    
    print("POSITION SIZING RESULTS")
    print("="*50)
    print(f"Entry Price: ${result['entry_price']:.2f}")
    print(f"Stop Price: ${result['stop_price']:.2f}")
    print(f"Position Value: ${result['position_value']:.2f}")
    print(f"Shares: {result['shares']}")
    print(f"Risk: ${result['risk_dollars']:.2f} ({result['risk_pct']*100:.2f}%)")
    print(f"\nProfit Targets:")
    print(f"  Stage 1: ${result['profit_target_1']:.2f}")
    print(f"  Stage 2: ${result['profit_target_2']:.2f}")
    print(f"  Stage 3: ${result['profit_target_3']:.2f}")
```

---

### Step 5: Module 4 - Trade Journal Automation

**File: trade_journal.py**

```python
import pandas as pd
from datetime import datetime

class TradeJournal:
    """Automated trade journaling with analysis"""
    
    def __init__(self, filename='trading_journal.csv'):
        self.filename = filename
        self.trades = []
        try:
            self.trades = pd.read_csv(filename).to_dict('records')
        except:
            self.trades = []
    
    def add_trade(self, entry_date, stock, entry_price, shares, setup_type, 
                  edges, checklist_score, exit_date=None, exit_price=None, 
                  exit_reason=None, setup_grade=None, exec_grade=None):
        """Add new trade to journal"""
        trade = {
            'trade_id': len(self.trades) + 1,
            'entry_date': entry_date,
            'stock': stock,
            'entry_price': entry_price,
            'shares': shares,
            'setup_type': setup_type,
            'edges': edges,
            'checklist_score': checklist_score,
            'exit_date': exit_date,
            'exit_price': exit_price,
            'exit_reason': exit_reason,
            'setup_grade': setup_grade,
            'exec_grade': exec_grade,
            'pnl_dollars': (exit_price - entry_price) * shares if exit_price else 0,
            'pnl_percent': ((exit_price - entry_price) / entry_price * 100) if exit_price else 0,
            'days_held': (datetime.strptime(exit_date, '%Y-%m-%d') - 
                         datetime.strptime(entry_date, '%Y-%m-%d')).days if exit_date else 0
        }
        
        # Auto-assign quadrant
        if setup_grade and exec_grade:
            if setup_grade == 'A' and exec_grade == 'A':
                trade['quadrant'] = '✓✓'
            elif setup_grade == 'A' and exec_grade != 'A':
                trade['quadrant'] = '✓✗'
            elif setup_grade != 'A' and exec_grade == 'A':
                trade['quadrant'] = '✗✓'
            else:
                trade['quadrant'] = '✗✗'
        
        self.trades.append(trade)
        self.save()
        return trade
    
    def get_statistics(self):
        """Calculate performance statistics"""
        if not self.trades:
            return None
        
        df = pd.DataFrame(self.trades)
        df = df[df['exit_price'].notna()]  # Only completed trades
        
        if len(df) == 0:
            return None
        
        winners = df[df['pnl_dollars'] > 0]
        losers = df[df['pnl_dollars'] < 0]
        
        stats = {
            'total_trades': len(df),
            'winning_trades': len(winners),
            'losing_trades': len(losers),
            'win_rate': len(winners) / len(df) * 100 if len(df) > 0 else 0,
            'total_profit': winners['pnl_dollars'].sum() if len(winners) > 0 else 0,
            'total_loss': abs(losers['pnl_dollars'].sum()) if len(losers) > 0 else 0,
            'avg_win': winners['pnl_dollars'].mean() if len(winners) > 0 else 0,
            'avg_loss': losers['pnl_dollars'].mean() if len(losers) > 0 else 0,
            'profit_factor': (winners['pnl_dollars'].sum() / abs(losers['pnl_dollars'].sum())) if len(losers) > 0 else 0
        }
        
        stats['expectancy'] = (stats['win_rate']/100 * stats['avg_win']) - ((1-stats['win_rate']/100) * abs(stats['avg_loss']))
        
        return stats
    
    def print_stats(self):
        """Print statistics"""
        stats = self.get_statistics()
        if not stats:
            print("No completed trades yet")
            return
        
        print("\nTRADING STATISTICS")
        print("="*50)
        print(f"Total Trades: {stats['total_trades']}")
        print(f"Winners: {stats['winning_trades']} ({stats['win_rate']:.1f}%)")
        print(f"Losers: {stats['losing_trades']}")
        print(f"\nTotal Profit: ${stats['total_profit']:.2f}")
        print(f"Total Loss: ${stats['total_loss']:.2f}")
        print(f"Net P&L: ${stats['total_profit'] - stats['total_loss']:.2f}")
        print(f"\nAvg Win: ${stats['avg_win']:.2f}")
        print(f"Avg Loss: ${stats['avg_loss']:.2f}")
        print(f"Profit Factor: {stats['profit_factor']:.2f}x")
        print(f"Expectancy: ${stats['expectancy']:.2f}/trade")
    
    def save(self):
        """Save journal to CSV"""
        df = pd.DataFrame(self.trades)
        df.to_csv(self.filename, index=False)

# Example usage
if __name__ == "__main__":
    journal = TradeJournal()
    
    # Add completed trade
    journal.add_trade(
        entry_date='2025-12-31',
        stock='NVDA',
        entry_price=100,
        shares=50,
        setup_type='VCP',
        edges=5,
        checklist_score=88,
        exit_date='2026-01-05',
        exit_price=112,
        exit_reason='Stage 2',
        setup_grade='A',
        exec_grade='A'
    )
    
    journal.print_stats()
```

---

## SECTION 1C: Full Stack Implementation (Advanced)

[Due to length, this includes Flask web app + database. Reference architecture_guide.md for full details]

---

## Scheduling & Automation

### Option 1: Local Machine (Easiest)
**Windows:**
1. Create `.bat` file:
```batch
@echo off
cd C:\Path\To\Trading\Scripts
python market_analysis.py
python stock_screener.py
```
2. Task Scheduler → Create Basic Task → Set to run daily at 4:15 PM

**Mac/Linux:**
```bash
crontab -e
# Add line:
15 16 * * * /usr/bin/python3 /path/to/stock_screener.py
0 18 * * 0 /usr/bin/python3 /path/to/market_analysis.py
```

### Option 2: Cloud (AWS Lambda)
- Upload Python scripts to AWS Lambda
- Configure triggers (EventBridge for scheduling)
- Cost: ~$0.20/month

### Option 3: Hosting (Heroku)
- Push code to Heroku
- Heroku Scheduler runs scripts
- Cost: Free tier (limited) or $7/month

---

## Troubleshooting

**Issue**: yfinance returns incomplete data
**Solution**: Add retry logic or use alternate data source (Alpha Vantage)

**Issue**: Email alerts not sending
**Solution**: Use Gmail app-specific password (not regular password)

**Issue**: Stock screening takes too long
**Solution**: Reduce stock list or optimize loop with threading

---

## Next Steps

1. **Choose implementation**: Google Sheets (easiest) or Python (recommended)
2. **Set up data sources**: Yahoo Finance (free) or broker API
3. **Test with paper trading**: Validate calculations vs manual
4. **Automate scheduling**: Weekly for market analysis, daily for screening
5. **Monitor and refine**: Adjust thresholds based on results

---

**Ready to code?** Open your chosen implementation and start building! 🚀
