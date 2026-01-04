# Section 4: Risk Management & Position Sizing - COMPLETE GUIDE
## How Much to Risk, Where to Place Stops, and When to Cut Losses

---

## OVERVIEW

This section defines the **exact rules** for:
1. ✅ **Stop Loss Placement** - Where to place stops for each setup (ATR-based + technical)
2. ✅ **Position Sizing** - How much capital to allocate per trade (environment + edge-based)
3. ✅ **Portfolio Heat Management** - Total risk exposure limits across all positions
4. ✅ **Drawdown Circuit Breakers** - When to pause trading and reduce risk
5. ✅ **Risk-of-Ruin Protection** - Preventing catastrophic account losses

**Philosophy**: Professional traders don't guess at risk—they calculate it precisely. Every trade you enter has:
- Exact entry price (to the penny)
- Exact stop price (to the penny)
- Exact position size (number of shares)
- Exact dollar risk (known before entry)
- Exact portfolio impact (% of account)

**No more "I'll figure it out later" or "feels about right." You'll know your exact risk on every trade before you click buy.**

---

---

# PART 1: STOP LOSS PLACEMENT (Where to Exit When Wrong)

## PHILOSOPHY: STOP LOSSES ARE NON-NEGOTIABLE

**Three types of traders**:
1. ❌ **Dead traders**: Never use stops, "ride it out," blow up eventually
2. ⚠️ **Amateur traders**: Use stops, but place them arbitrarily ("5% below entry feels right")
3. ✅ **Professional traders**: Calculate stops mathematically based on volatility + technicals

**You will be a professional trader.**

---

## RULE 1: ATR-BASED STOPS (Volatility-Adjusted)

**What is ATR?**
- **Average True Range** = measure of stock's volatility
- Developed by J. Welles Wilder (1970s)
- Shows how much a stock typically moves per day
- Higher ATR = more volatile, needs wider stops
- Lower ATR = less volatile, can use tighter stops

**Why Use ATR?**[274][275][276][277][278]
- Adapts to each stock's volatility (NVDA needs wider stops than AAPL)
- Prevents getting stopped out by normal price action
- Gives trades "room to breathe"
- Professional standard in institutional trading

---

### ATR STOP LOSS FORMULA

**Basic Formula**[275][277][278][280]:
```
Stop Loss = Entry Price - (ATR × Multiplier)

For Long Positions:
  Stop = Entry - (ATR × Multiplier)

For Short Positions (if you trade shorts):
  Stop = Entry + (ATR × Multiplier)
```

**ATR Multiplier Guidelines**[275][280][282]:
```
Tight Stops (Aggressive):   1.5x - 2.0x ATR
Standard Stops (Balanced):  2.0x - 2.5x ATR
Wide Stops (Conservative):  2.5x - 3.0x ATR
Very Wide (High Vol):       3.0x - 4.0x ATR
```

---

### WHEN TO USE EACH MULTIPLIER

**1.5x - 2.0x ATR** (Tight Stops):
```
Use when:
  ✓ Low volatility stock (ATR <3% of price)
  ✓ Strong trending environment (Environment A)
  ✓ Tight setup (flat base, tight VCP)
  ✓ High conviction (7+ edges present)
  ✓ Planning to scale into position

Risk: 3-5% per share typically

Example:
  Stock: CRWD
  Entry: $350.00
  ATR(14): $12.00
  Multiplier: 2.0x
  Stop: $350 - ($12 × 2.0) = $350 - $24 = $326.00
  Risk: $24 per share = 6.9% per share
```

**2.0x - 2.5x ATR** (Standard Stops):
```
Use when:
  ✓ Normal volatility (ATR 3-5% of price)
  ✓ Environment A or B
  ✓ Standard setup quality (Grade B)
  ✓ 4-6 edges present
  ✓ Full position size

Risk: 5-8% per share typically

Example:
  Stock: META
  Entry: $475.00
  ATR(14): $15.00
  Multiplier: 2.5x
  Stop: $475 - ($15 × 2.5) = $475 - $37.50 = $437.50
  Risk: $37.50 per share = 7.9% per share
```

**2.5x - 3.0x ATR** (Wide Stops):
```
Use when:
  ✓ Higher volatility (ATR 5-7% of price)
  ✓ Environment B or C
  ✓ Wider setup (cup-with-handle, deeper VCP)
  ✓ 3-4 edges present
  ✓ Swing trade (5-20 day hold)

Risk: 8-12% per share typically

Example:
  Stock: TSLA
  Entry: $250.00
  ATR(14): $12.00
  Multiplier: 3.0x
  Stop: $250 - ($12 × 3.0) = $250 - $36 = $214.00
  Risk: $36 per share = 14.4% per share
```

**3.0x - 4.0x ATR** (Very Wide Stops):
```
Use when:
  ✓ Very high volatility (ATR >7% of price)
  ✓ Environment C or D (choppy market)
  ✓ Breakout from deep base
  ✓ Post-earnings volatility
  ✓ Position trade (20+ day hold)

Risk: 12-18% per share typically
WARNING: Only use with smaller position sizes!

Example:
  Stock: SMCI (high volatility)
  Entry: $1,000.00
  ATR(14): $80.00
  Multiplier: 3.5x
  Stop: $1,000 - ($80 × 3.5) = $1,000 - $280 = $720.00
  Risk: $280 per share = 28% per share (!)
  
  Solution: Use 50% normal position size to keep dollar risk reasonable
```

---

### ATR CALCULATION (How to Get ATR Value)

**Where to Find ATR**:
```
TradingView:
  → Add indicator "ATR" (Average True Range)
  → Default setting: 14 periods (use this)
  → Read current ATR value from indicator

Interactive Brokers TWS:
  → Right-click chart → Insert Indicator → ATR
  → Period: 14
  → Read value

Yahoo Finance / Manual:
  → Download daily prices (14 days)
  → Calculate True Range each day:
      TR = MAX(High-Low, |High-PrevClose|, |Low-PrevClose|)
  → ATR = Average of last 14 TRs
```

**Example Calculation** (Manual Method):
```
Stock: NVDA
Last 14 days True Range values:
  Day 1: $18.50
  Day 2: $22.00
  Day 3: $15.00
  Day 4: $19.50
  Day 5: $21.00
  ... (10 more days)
  
  Sum of 14 days: $265.00
  ATR(14) = $265 / 14 = $18.93

Use: $18.93 as your ATR multiplier base
```

---

## RULE 2: TECHNICAL STOPS (Key Support Levels)

**ATR stops are mathematical, but sometimes technical levels are better.**

### WHEN TO USE TECHNICAL STOPS INSTEAD

**Priority Order** (use whichever is WIDER):
```
1. Check ATR stop distance
2. Check technical support distance
3. Use the WIDER of the two

Why? Tighter stops get hit too easily (false stops)
```

---

### TECHNICAL STOP LEVELS

**A. Below Setup Low** (Most Common):
```
For VCP:
  Stop = Lowest low of final contraction - $0.50

For Cup-with-Handle:
  Stop = Handle low - $0.50

For Flat Base:
  Stop = Base low - $0.50

For Range Breakout:
  Stop = Range low - $0.50

Example: CRWD Flat Base
  Entry: $350.15 (range high breakout)
  Range low: $346.00
  ATR stop (2.5x): $326.00 (too tight)
  Technical stop: $346.00 - $0.50 = $345.50 ✓ (wider, better)
  
  USE: $345.50 (technical stop)
```

**B. Below Key Moving Average**:
```
21 EMA Stop (Tight):
  Stop = 21 EMA - (1% of price)
  Use for: Strong trends, tight setups
  
  Example: Stock at $200, 21 EMA at $195
  Stop = $195 - ($200 × 0.01) = $195 - $2 = $193

50 SMA Stop (Wide):
  Stop = 50 SMA - (2% of price)
  Use for: Position trades, wider bases
  
  Example: Stock at $200, 50 SMA at $185
  Stop = $185 - ($200 × 0.02) = $185 - $4 = $181
```

**C. Below Prior Swing Low**:
```
Identify last significant swing low before breakout
Place stop $0.25-0.50 below that level

Example: NVDA breakout
  Entry: $500
  Prior swing low (2 weeks ago): $480
  Stop: $480 - $0.50 = $479.50
```

**D. Percentage Stop** (Last Resort Only):
```
Fixed % below entry:
  Tight: 5-7% below entry
  Standard: 7-10% below entry
  Wide: 10-12% below entry
  
ONLY use if:
  ✗ ATR not available
  ✗ No clear technical level
  ✗ Trading very short-term

Example:
  Entry: $100
  Stop: $100 × (1 - 0.08) = $92.00 (8% stop)
```

---

### STOP PLACEMENT DECISION TREE

```
DECISION PROCESS:

STEP 1: Calculate ATR Stop
  → Entry - (ATR × Multiplier) = $___

STEP 2: Identify Technical Stop
  → Setup low, MA, or swing low - $0.50 = $___

STEP 3: Compare
  → ATR Stop: $___
  → Technical Stop: $___
  → Use WIDER of the two ✓

STEP 4: Validate
  → Is stop 5-15% below entry? 
    YES: Reasonable, proceed ✓
    NO (<5%): Too tight, consider passing
    NO (>15%): Too wide, reduce position size

STEP 5: Place Order
  → Set stop-loss order at calculated price
  → NEVER enter trade without stop placed
```

---

## RULE 3: ADJUSTING STOPS (Dynamic Stop Management)

**Stops are NOT "set and forget" - they should adjust as trade progresses.**

### TRAILING STOP METHODS

**Method A: 21 EMA Trailing Stop** (Conservative):
```
Once stock is up 10%+:
  → Move stop to just below 21 EMA
  → Adjust daily as 21 EMA rises
  → Gives trade room, protects large gains

Example: NVDA
  Entry: $500, Initial stop: $475
  Stock runs to $600 (+20%)
  21 EMA now at $585
  New stop: $585 - (1% of $600) = $585 - $6 = $579
  
  Locked in gain: $579 - $500 = $79 (+15.8% profit secured)
```

**Method B: ATR Trailing Stop**[275][280] (Dynamic):
```
As stock moves up, trail stop using ATR:
  New Stop = Current Price - (ATR × Trailing Multiplier)
  
Trailing multipliers:
  Initial: 2.0x - 2.5x (wider)
  After +10% gain: 2.5x - 3.0x (wider still, lock profits)
  After +20% gain: 3.0x - 3.5x (very wide, let it run)

Example:
  Entry: $100, ATR: $5, Initial stop: $100 - ($5 × 2.0) = $90
  
  Stock at $110 (+10%):
    New stop: $110 - ($5 × 2.5) = $110 - $12.50 = $97.50
    Locked in: $97.50 - $100 = Still down -2.5% (minimal lock)
  
  Stock at $120 (+20%):
    New stop: $120 - ($5 × 3.0) = $120 - $15 = $105
    Locked in: $105 - $100 = +5% profit secured
```

**Method C: Breakeven Stop + Profit Lock**[298][304] (Mark Minervini Method):
```
Move stop to breakeven when:
  ✓ Stock up by 1× your initial risk
  
Then move to profit-lock when:
  ✓ Stock up by 2× your initial risk

Example:
  Entry: $100
  Initial stop: $92 (risk = $8)
  
  Stock at $108 (+8%, = 1× risk):
    Move stop to $100 (breakeven) ✓
    No longer at risk of loss
  
  Stock at $116 (+16%, = 2× risk):
    Move stop to $108 (+8% lock) ✓
    Guaranteed 8% profit even if reverses
```

---

## RULE 4: WHEN TO TIGHTEN STOPS (Risk Reduction Scenarios)

**Tighten stops (reduce risk) when**:

**A. Environment Degrades**:
```
Environment shifts A → B or B → C:
  → Tighten stops to 1.5x - 2.0x ATR
  → Consider trailing existing winners more aggressively
  → Be quicker to exit weak positions
```

**B. Stock Behavior Changes**:
```
Signs of weakness:
  ✗ Price closes below 21 EMA on increasing volume
  ✗ Volume dries up on up days (no demand)
  ✗ Makes lower high after breakout
  ✗ Breaks below key support intraday multiple times
  
Action: Tighten stop to just below recent low
```

**C. Time Stop Triggered** (No Progress):
```
If stock hasn't moved 5% in your favor after:
  - 5-10 days (for breakout trades)
  - 10-15 days (for base breakouts)
  - 15-20 days (for position trades)
  
Action: Tighten stop to breakeven or exit entirely
Reason: Capital tied up, not working, better opportunities elsewhere
```

**D. After Big Run** (+30%+ Gains):
```
Once up 30-50%:
  → Trail stop very tightly (just below 21 EMA daily)
  → Objective: Don't give back huge gains
  → Be willing to exit on first sign of weakness
```

---

## RULE 5: WHEN NEVER TO ADJUST STOPS

**DO NOT move stops wider (against you)**:
```
❌ NEVER: "Stock just needs more room, I'll move stop to $80 from $85"
   Result: Turns 5% loss into 10% loss, violates risk management

❌ NEVER: "I don't want to take the loss today, I'll move stop lower"
   Result: Hope trading, account killer

❌ NEVER: "Stock will come back, let me give it space"
   Result: Small loss becomes large loss

✅ ONLY move stops in your favor (securing profits)
```

**The Only Exception**:
```
If initial stop was placed incorrectly (too tight due to calculation error):
  → Fix it IMMEDIATELY on same day
  → Document why it was wrong
  → Don't make same mistake again
  
But NEVER move stop after trade is already against you
```

---

---

# PART 2: POSITION SIZING (How Much Capital Per Trade)

## PHILOSOPHY: SIZE MATTERS MORE THAN WIN RATE

**What kills traders?**
- ❌ Not lack of good setups
- ❌ Not lack of knowledge
- ✅ **Position sizing too large relative to risk**

**Key Principle**: Risk small enough that even 5-10 consecutive losses doesn't blow you up.

---

## YOUR POSITION SIZING FRAMEWORK

**Three Inputs Determine Position Size**:
1. **Environment** (A/B/C/D) = Base position size
2. **Edges Present** (0-10) = Size multiplier
3. **Setup Quality** (A/B/C/F) = Final adjustment

---

## RULE 6: BASE POSITION SIZE BY ENVIRONMENT

**From Section 1: Market Analysis Framework**

**Environment A** (Strong Bull Market):
```
Base Position Size: 10% of portfolio
Maximum Position Size: 20% of portfolio
Maximum Portfolio Heat: 2.5% (total risk across all positions)
Number of Positions: 5-8 positions typical

Example ($50,000 account):
  Base position value: $5,000 (10%)
  Max position value: $10,000 (20%)
  Max portfolio risk: $1,250 (2.5%)
```

**Environment B** (Normal Bull Market):
```
Base Position Size: 8% of portfolio
Maximum Position Size: 15% of portfolio
Maximum Portfolio Heat: 2.0%
Number of Positions: 5-8 positions

Example ($50,000 account):
  Base position value: $4,000 (8%)
  Max position value: $7,500 (15%)
  Max portfolio risk: $1,000 (2.0%)
```

**Environment C** (Weak/Choppy Market):
```
Base Position Size: 5% of portfolio
Maximum Position Size: 10% of portfolio
Maximum Portfolio Heat: 1.0%
Number of Positions: 3-5 positions

Example ($50,000 account):
  Base position value: $2,500 (5%)
  Max position value: $5,000 (10%)
  Max portfolio risk: $500 (1.0%)
```

**Environment D** (Bear Market / Distribution):
```
Base Position Size: 0-3% of portfolio (mostly cash)
Maximum Position Size: 5% of portfolio
Maximum Portfolio Heat: 1.5%
Number of Positions: 0-3 positions (highly selective)

Example ($50,000 account):
  Base position value: $1,500 (3%)
  Max position value: $2,500 (5%)
  Max portfolio risk: $750 (1.5%)
```

---

## RULE 7: EDGE-BASED POSITION SIZE ADJUSTMENTS

**From Section 3: Your 10 Edges**

**Sizing Multiplier Formula**:
```
Final Position % = Base Position % + (Number of Edges × 0.5%)

Maximum addition: +5% (if all 10 edges present)
```

**Sizing Table**:
```
Edges Present | Size Adjustment | Environment A Example
--------------|-----------------|----------------------
0-2 edges     | PASS           | No trade
3 edges       | -5%            | 10% → 5% (reduce to 50%)
4 edges       | Base           | 10% (no adjustment)
5 edges       | +0.5%          | 10% → 10.5%
6 edges       | +1.0%          | 10% → 11%
7 edges       | +1.5%          | 10% → 11.5%
8 edges       | +2.0%          | 10% → 12%
9 edges       | +2.5%          | 10% → 12.5%
10 edges      | +3.0%          | 10% → 13%
```

**Full Example**:
```
Account: $50,000
Environment: A (Base = 10%)
Edges Present: 7 edges
Setup: VCP Grade A
Stock: CRWD at $350

Calculation:
  Base position: 10%
  Edge adjustment: +1.5% (7 edges)
  Final position: 11.5% of $50,000 = $5,750
  
  Entry: $350.00
  Shares: $5,750 / $350 = 16 shares
  Position value: 16 × $350 = $5,600
```

---

## RULE 8: SETUP QUALITY ADJUSTMENTS

**Grade-Based Sizing**:
```
Grade A Setup (Excellent):
  → Use calculated position size (no adjustment)
  → Full conviction

Grade B Setup (Good):
  → Reduce calculated size by 20-30%
  → Good setup but not perfect

Grade C Setup (Marginal):
  → Reduce calculated size by 50%
  → Only trade if 8+ edges present
  → Consider passing entirely

Grade F Setup (Poor):
  → PASS, do not trade
```

**Example**:
```
Calculated position: $5,750 (11.5%)
Setup grade: B

Adjusted position: $5,750 × 0.75 = $4,312.50
Rounded shares: $4,312.50 / $350 = 12 shares
Final position value: 12 × $350 = $4,200 (8.4% of account)
```

---

## RULE 9: RISK-BASED POSITION SIZING (The Professional Method)

**Most Important Formula in Trading**[289][290][291]:

### FIXED FRACTIONAL POSITION SIZING[289][291][296][299]

**Formula**:
```
Position Size = (Account Value × Risk %) / Risk Per Share

Where:
  Account Value = Current account equity
  Risk % = Percentage of account you're willing to risk
  Risk Per Share = Entry Price - Stop Loss Price
```

**Step-by-Step Calculation**:
```
STEP 1: Determine Risk Percentage
  Environment A: 0.5% per trade
  Environment B: 0.4% per trade
  Environment C: 0.25% per trade
  Environment D: 0.2% per trade

STEP 2: Calculate Dollar Risk
  Dollar Risk = Account Value × Risk %
  
  Example: $50,000 × 0.5% = $250 risk per trade

STEP 3: Calculate Risk Per Share
  Risk Per Share = Entry Price - Stop Price
  
  Example: $350 - $345.50 = $4.50 per share

STEP 4: Calculate Position Size
  Shares = Dollar Risk / Risk Per Share
  Shares = $250 / $4.50 = 55.5 → 55 shares
  
STEP 5: Verify Position Value
  Position Value = 55 × $350 = $19,250 (38.5% of account)
  
STEP 6: Check Against Max Position Limits
  38.5% > 20% max (Environment A) ❌
  
  Action: Position too large, reduce
  Use maximum: 20% of $50,000 = $10,000
  Shares: $10,000 / $350 = 28 shares
  
  New risk: 28 × $4.50 = $126 (0.25% of account) ✓
```

---

### POSITION SIZING EXAMPLES (Full Scenarios)

**Scenario 1: Tight Stop, Environment A**:
```
Account: $50,000
Environment: A (base 10%, risk 0.5%)
Edges: 8 (excellent)
Setup: Flat Base Grade A

Entry: $350.00
Stop: $345.50 (tight, range low)
Risk per share: $4.50 (1.3%)

Position Calculation:
  Base: 10% + 2% (8 edges) = 12% = $6,000
  Risk-based: ($50,000 × 0.5%) / $4.50 = $250 / $4.50 = 55 shares = $19,250
  
  Conflict: $6,000 vs $19,250
  Use: $6,000 (position size limit takes priority)
  
  Final: $6,000 / $350 = 17 shares
  Position value: $5,950 (11.9% of account)
  Dollar risk: 17 × $4.50 = $76.50 (0.15% of account) ✓✓
  
VERDICT: Conservative, low account risk, appropriate for high conviction
```

**Scenario 2: Wide Stop, Environment C**:
```
Account: $50,000
Environment: C (base 5%, risk 0.25%)
Edges: 4 (minimal)
Setup: VCP Grade B

Entry: $1,000.00
Stop: $920.00 (wide, ATR 3x)
Risk per share: $80 (8%)

Position Calculation:
  Base: 5% = $2,500
  Risk-based: ($50,000 × 0.25%) / $80 = $125 / $80 = 1.56 → 1 share
  
  Position value: 1 × $1,000 = $1,000 (2% of account)
  Dollar risk: 1 × $80 = $80 (0.16% of account) ✓
  
VERDICT: Very small position due to wide stop + weak environment, appropriate
```

**Scenario 3: Medium Stop, Environment B**:
```
Account: $50,000
Environment: B (base 8%, risk 0.4%)
Edges: 6 (good)
Setup: Cup-Handle Grade A

Entry: $200.00
Stop: $186.00 (ATR 2.5x)
Risk per share: $14 (7%)

Position Calculation:
  Base: 8% + 1% (6 edges) = 9% = $4,500
  Risk-based: ($50,000 × 0.4%) / $14 = $200 / $14 = 14.3 → 14 shares = $2,800
  
  Conflict: $4,500 vs $2,800
  Use: $2,800 (risk-based is MORE conservative, use that)
  
  Final: 14 shares × $200 = $2,800 (5.6% of account)
  Dollar risk: 14 × $14 = $196 (0.39% of account) ✓
  
VERDICT: Risk-based sizing reduces position, protecting capital
```

---

## RULE 10: SCALING INTO POSITIONS (Advanced Technique)

**Instead of entering full size immediately, scale in as setup confirms.**[298][301][304]

### SCALING STRATEGY (Mark Minervini Method)[298][301][304]

**Initial Position: 25-33% of Planned Size**:
```
Purpose: Test the waters, get market feedback
Risk: Minimal if wrong

Example:
  Planned position: 16 shares ($5,600)
  Initial entry: 4 shares ($1,400) = 25%
  Entry: $350.00
  Stop: $345.50
  Initial risk: 4 × $4.50 = $18 (0.036% of account)
```

**Add 33% More If Working** (+5% gain):
```
Stock at $367.50 (+5%):
  Add: 5 shares at $367.50 ($1,837.50)
  Total: 9 shares, avg price $356.94
  Move stop: $350 (breakeven on initial lot)
  Risk now: Only on 5 new shares
```

**Add Final 33%** (+10% gain):
```
Stock at $385 (+10% from initial):
  Add: 7 shares at $385 ($2,695)
  Total: 16 shares, avg price $368.28
  Move stop: $367.50 (lock small profit on all)
  
Full position now deployed, but with:
  ✓ Confirmation stock is working
  ✓ Minimal risk if initial entry failed
  ✓ Lower average cost than buying full size at higher price
```

**When to Scale vs Full Entry**:
```
Scale In:
  ✓ Environment B or C (uncertain)
  ✓ Setup grade B or C (not perfect)
  ✓ Only 4-5 edges (moderate conviction)
  ✓ Post-earnings volatility
  ✓ Stock near resistance

Full Entry:
  ✓ Environment A (strong)
  ✓ Setup grade A (excellent)
  ✓ 7+ edges (high conviction)
  ✓ Clear breakout on huge volume
  ✓ Gap up through resistance
```

---

---

# PART 3: PORTFOLIO HEAT MANAGEMENT (Total Risk Control)

## WHAT IS PORTFOLIO HEAT?

**Definition**[281][283][285][287]: Total risk exposure across ALL open positions simultaneously.

**Formula**:
```
Portfolio Heat = Σ (Position Size % × Stop Loss %)

For each position:
  Individual Heat = (Position Value / Account Value) × (Entry - Stop) / Entry

Total Heat = Sum of all individual heats
```

---

## RULE 11: MAXIMUM PORTFOLIO HEAT LIMITS

**By Environment** (from Section 1):

```
Environment A: Maximum 2.5% portfolio heat
  → Can lose 2.5% of account if ALL stops hit same day
  
Environment B: Maximum 2.0% portfolio heat
  → Can lose 2.0% of account if ALL stops hit same day
  
Environment C: Maximum 1.0% portfolio heat
  → Can lose 1.0% of account if ALL stops hit same day
  
Environment D: Maximum 1.5% portfolio heat
  → Very few positions, tight risk control
```

---

### PORTFOLIO HEAT CALCULATION EXAMPLE

**Scenario: 5 Open Positions in Environment A**

```
Account Value: $50,000
Max Heat Allowed: 2.5% = $1,250

Position 1: NVDA
  Shares: 10
  Entry: $500
  Stop: $480
  Position value: $5,000 (10% of account)
  Risk per share: $20
  Individual heat: (10 × $20) / $50,000 = $200 / $50,000 = 0.4%

Position 2: CRWD
  Shares: 17
  Entry: $350
  Stop: $345.50
  Position value: $5,950 (11.9%)
  Risk per share: $4.50
  Individual heat: (17 × $4.50) / $50,000 = $76.50 / $50,000 = 0.15%

Position 3: META
  Shares: 12
  Entry: $475
  Stop: $460
  Position value: $5,700 (11.4%)
  Risk per share: $15
  Individual heat: (12 × $15) / $50,000 = $180 / $50,000 = 0.36%

Position 4: MSFT
  Shares: 14
  Entry: $420
  Stop: $408
  Position value: $5,880 (11.8%)
  Risk per share: $12
  Individual heat: (14 × $12) / $50,000 = $168 / $50,000 = 0.34%

Position 5: AAPL
  Shares: 30
  Entry: $185
  Stop: $178
  Position value: $5,550 (11.1%)
  Risk per share: $7
  Individual heat: (30 × $7) / $50,000 = $210 / $50,000 = 0.42%

TOTAL PORTFOLIO HEAT:
  0.4% + 0.15% + 0.36% + 0.34% + 0.42% = 1.67%
  
VERDICT: 1.67% < 2.5% max ✓ Safe to hold all positions
```

---

## RULE 12: ACTIONS WHEN HEAT LIMIT EXCEEDED

**If Portfolio Heat > Maximum Allowed**:

**Option 1: Don't Add New Positions**:
```
Current heat: 2.3% (Environment A, max 2.5%)
New trade opportunity: Would add 0.4% heat

Decision: PASS on new trade
Reason: 2.3% + 0.4% = 2.7% > 2.5% limit
Wait for: Existing position to close or move to breakeven
```

**Option 2: Reduce Existing Position**:
```
Current heat: 2.6% (over limit by 0.1%)

Action: Identify weakest position, trim or close
Example: Close AAPL position (0.42% heat)
New heat: 2.6% - 0.42% = 2.18% ✓ Under limit

OR: Tighten stops on all positions to reduce heat
```

**Option 3: Tighten All Stops**:
```
Current heat: 2.6%
Action: Move all stops closer (trail stops aggressively)

Example: NVDA
  Old stop: $480 (risk $20 per share, heat 0.4%)
  New stop: $490 (risk $10 per share, heat 0.2%)
  Heat reduction: 0.2%

Repeat for all positions
New total heat: 2.1% ✓
```

---

## RULE 13: PORTFOLIO HEAT MONITORING (Weekly Routine)

**Every Sunday (Part of Market Analysis)**:

```
PORTFOLIO HEAT CHECK:

Current Positions:
  Position 1: ___ shares of ___, entry $__, stop $__, heat ___%
  Position 2: ___ shares of ___, entry $__, stop $__, heat ___%
  Position 3: ___ shares of ___, entry $__, stop $__, heat ___%
  [... all positions]

Total Portfolio Heat: ___% (sum of all)
Maximum Allowed Heat: ___% (based on environment)

Status: UNDER LIMIT ✓ / OVER LIMIT ✗

If OVER LIMIT:
  [ ] Option chosen:
      [ ] Pass on new trades until under limit
      [ ] Close weakest position: ___
      [ ] Tighten stops on: ___, ___, ___
      [ ] Reduce position sizes by ___%

If UNDER LIMIT:
  [ ] Available heat capacity: ___% 
  [ ] Can add ___ positions at ___% sizing
```

---

---

# PART 4: DRAWDOWN CIRCUIT BREAKERS (Emergency Protocols)

## WHAT IS DRAWDOWN?

**Definition**[297]: Peak-to-trough decline in account value.

```
Example:
  Account peak: $60,000 (your all-time high)
  Current value: $54,000
  Drawdown: ($60,000 - $54,000) / $60,000 = 10%
```

**Why It Matters**[297]:
- Drawdowns are inevitable (even best systems have them)
- Large drawdowns destroy psychology
- Recovering from drawdowns requires larger gains
- 50% drawdown needs 100% gain to recover (!)

**Drawdown Recovery Math**:
```
10% loss → Need 11.1% gain to recover
20% loss → Need 25% gain to recover
30% loss → Need 42.9% gain to recover
50% loss → Need 100% gain to recover ⚠️
```

---

## RULE 14: CIRCUIT BREAKER LEVELS[294][297]

**Three levels of intervention:**

### LEVEL 1: -5% DRAWDOWN (Yellow Alert)[294]

**Trigger**: Account down 5% from peak

**Actions**:
```
MANDATORY:
  [ ] Review all open positions
  [ ] Grade each trade (is setup still valid?)
  [ ] Tighten stops on all positions by 20-30%
  [ ] STOP adding new positions for 3 trading days
  [ ] Reduce position sizing by 25% on next trades
  [ ] Daily journaling: What's going wrong?

Example:
  Peak: $50,000
  Current: $47,500 (-5%)
  
  Action:
    - Stop trading for 3 days
    - Review what led to losses
    - Tighten all stops
    - Next trade: Use 75% of calculated size
```

**Resume Normal Trading When**:
```
✓ Account recovers to within -2.5% of peak
✓ 3+ winning trades in a row
✓ Market environment improves
✓ Identified and fixed mistakes
```

---

### LEVEL 2: -10% DRAWDOWN (Orange Alert)[294][297]

**Trigger**: Account down 10% from peak

**Actions**:
```
MANDATORY:
  [ ] STOP trading completely for 1 week
  [ ] Close 50% of open positions (keep only best 2-3)
  [ ] Move all remaining stops to breakeven or better
  [ ] Comprehensive trading review:
      - What rules were broken?
      - What's different about market environment?
      - Are setups still working?
  [ ] Paper trade only for 1 week
  [ ] Reduce position sizing by 50% when resuming

Example:
  Peak: $50,000
  Current: $45,000 (-10%)
  
  Action:
    - Immediately close 3 of 6 positions
    - Move stops to breakeven on remaining 3
    - No live trading for 7 days
    - Paper trade during those 7 days
    - When resuming: 5% positions instead of 10%
```

**Resume Normal Trading When**:
```
✓ Account recovers to within -5% of peak
✓ Paper trading shows 5+ winning trades
✓ Market environment confirms improvement
✓ 2 weeks minimum break taken
✓ Documented plan for what you'll do differently
```

---

### LEVEL 3: -15% DRAWDOWN (Red Alert - Trading Suspension)[297]

**Trigger**: Account down 15% from peak

**Actions**:
```
MANDATORY - FULL STOP:
  [ ] Close ALL open positions immediately (no exceptions)
  [ ] Move 100% to cash
  [ ] STOP live trading for minimum 1 month
  [ ] Full system audit:
      - Is strategy still valid?
      - Did market regime change?
      - Am I emotionally damaged?
      - Do I need to re-educate?
  [ ] Paper trade entire system for 3-4 weeks
  [ ] Seek external review (mentor, trading coach, peer review)
  [ ] Consider reducing account size when resuming (trade with less capital)

Example:
  Peak: $50,000
  Current: $42,500 (-15%)
  
  Action:
    - Close everything, go 100% cash
    - Take 1 month minimum break
    - Re-study all materials
    - Paper trade 20+ trades
    - When resuming: Start with $25,000 only (50% of peak)
    - Rebuild slowly to full size over 3-6 months
```

**Resume Normal Trading When**:
```
✓ 1 month minimum break completed
✓ 20+ paper trades with 60%+ win rate
✓ Market environment strongly favorable
✓ Psychological recovery confirmed (no revenge trading urges)
✓ Written plan for position sizing rebuild
✓ External review/approval (coach, mentor, or peer)
```

---

## RULE 15: CONSECUTIVE LOSS LIMITS[294]

**In addition to drawdown triggers, also stop when:**

**3 Consecutive Losses** (Any Size):
```
Trigger: 3 losing trades in a row

Action:
  [ ] Stop trading for 2 days
  [ ] Review all 3 trades:
      - Was setup valid?
      - Was entry timing correct?
      - Did you follow rules?
  [ ] Identify pattern (are you making same mistake?)
  [ ] Paper trade 3 trades before resuming

Purpose: Break losing streak psychology
```

**5 Losses in 10 Trades** (50%+ Loss Rate):
```
Trigger: 5 losing trades out of last 10

Action:
  [ ] Stop trading for 1 week
  [ ] Full review of all 10 trades
  [ ] Is win rate below expectation?
  [ ] Is market environment hostile?
  [ ] Paper trade until 7 of 10 winning

Purpose: System not working, need re-calibration
```

**Daily Loss Limit** (2% Max Per Day):
```
Trigger: Down 2% of account in single day

Action:
  [ ] Stop trading immediately (rest of day)
  [ ] No more trades today, period
  [ ] Journal what went wrong
  [ ] Review trades tomorrow morning
  [ ] Resume next day with reduced sizing (50%)

Purpose: Prevent cascade of emotional revenge trades
```

---

## RULE 16: DRAWDOWN PREVENTION (Best Practices)

**Prevent large drawdowns BEFORE they happen**:

**1. Trade Small** (Most Important)[297]:
```
Never risk more than 0.5% per trade in Environment A
Never risk more than 0.25% per trade in Environment C

Even if you lose 10 trades in a row:
  Environment A: 10 × 0.5% = 5% drawdown (manageable)
  Environment C: 10 × 0.25% = 2.5% drawdown (minimal)
```

**2. Diversify Across Setups**:
```
Don't trade only one setup type
Spread risk across:
  - VCP breakouts
  - Cup-with-Handle breakouts
  - Flat base breakouts
  - Pullback entries
  
If one setup stops working, others may still work
```

**3. Diversify Across Sectors**:
```
Don't load up on single sector (e.g., all semiconductors)

Max per sector:
  Environment A: 40% of portfolio
  Environment B: 30% of portfolio
  Environment C: 20% of portfolio
  
Example: If 60% invested, max in any sector:
  Semiconductors: 24% (40% of 60%)
  Cybersecurity: 24%
  Cloud: 12%
```

**4. Use Stops Religiously**:
```
100% of trades must have stops placed
Never "mental stops" - always hard stops in system
Never move stops against you
Take losses quickly, let winners run
```

**5. Monitor Market Environment Daily**:
```
If environment shifts A → B or B → C:
  → Immediately reduce position sizes
  → Tighten all stops
  → Raise bar for new entries
  
Don't wait until drawdown forces you
```

---

---

# PART 5: INTEGRATION - YOUR COMPLETE RISK SYSTEM

## YOUR TRADE EXECUTION CHECKLIST

**Before Every Trade, Complete This** (2-3 minutes):

```
TRADE SETUP: _____________ (stock symbol)
DATE: _________

SECTION 1: SETUP VALIDATION
[ ] Setup identified: VCP / Cup-Handle / Flat Base / Other
[ ] Setup grade: A / B / C / F
[ ] If C or F: PASS on trade ✗

SECTION 2: EDGE SCORING
Count edges present:
[ ] RS Phase
[ ] RS Rating >85
[ ] Growth >40% EPS
[ ] Leading Theme
[ ] Trendability
[ ] High Volume
[ ] New Highs
[ ] Multi-TF Alignment
[ ] Catalyst
[ ] Volume Confirmation

Total Edges: ___/10
[ ] If <3 edges: PASS on trade ✗

SECTION 3: ENVIRONMENT CHECK
Current Environment: A / B / C / D
Base Position Size: ___% of account
Max Position Size: ___% of account
Risk Per Trade: ___% of account

SECTION 4: STOP LOSS CALCULATION
Entry Price: $_____
ATR(14): $_____
ATR Multiplier: ___x
ATR Stop: $_____ (Entry - ATR × Multiplier)

Technical Stop Level: $_____
  (Setup low, MA, or swing low - $0.50)

Final Stop (wider of two): $_____
[ ] Stop is 5-15% below entry ✓ / ✗

SECTION 5: POSITION SIZING
Account Value: $_____
Environment Base: ___% = $_____
Edge Adjustment: +___% (from edges) = $_____
Setup Adjustment: ___% (if Grade B/C) = $_____
Final Position Value: $_____

Risk-Based Check:
  Account Risk %: ___%
  Dollar Risk: $_____ (Account × Risk %)
  Risk Per Share: $_____ (Entry - Stop)
  Max Shares: _____ (Dollar Risk / Risk Per Share)
  Max Position Value: $_____ (Shares × Entry)

Use SMALLER of:
  Position-based: $_____
  Risk-based: $_____
  
Final Position Value: $_____
Final Shares: _____

SECTION 6: PORTFOLIO HEAT CHECK
Current Portfolio Heat: ___%
This Trade Heat: ___%
  (Position Value / Account) × (Risk Per Share / Entry Price)
  
New Total Heat: ___% (Current + This Trade)
Max Heat Allowed: ___% (based on environment)

[ ] New Total < Max Allowed ✓
[ ] If exceeded: PASS or reduce position ✗

SECTION 7: RISK METRICS SUMMARY
Position Size: _____ shares at $_____
Position Value: $_____ (___% of account)
Entry Price: $_____
Stop Price: $_____
Risk Per Share: $_____ (__% per share)
Total Dollar Risk: $_____
Account Risk: ___% of account

SECTION 8: DECISION
[ ] All checks passed: EXECUTE TRADE ✓
[ ] Any check failed: PASS ON TRADE ✗
[ ] Action: BUY ___ shares at $_____, stop at $_____
```

---

## POSITION MANAGEMENT QUICK REFERENCE

**After Entry:**

**Day 1-5** (Initial Period):
```
[ ] Stop is placed and active in broker system
[ ] Position recorded in journal
[ ] Initial stop = _____
[ ] No adjustments unless major environment change
```

**After +5% Gain**:
```
[ ] Consider moving stop to breakeven
[ ] If strong (up on volume), hold with initial stop
[ ] If weak (up on light volume), tighten to breakeven
```

**After +10% Gain**:
```
[ ] Move stop to breakeven minimum
[ ] Consider trimming 25-33% of position
[ ] Trail remaining with 21 EMA or ATR trailing stop
```

**After +20% Gain**:
```
[ ] Trim another 25-33% of position
[ ] Move stop to lock in 10%+ profit on remainder
[ ] Trail very tightly (just below 21 EMA daily)
```

**After +30%+ Gain**:
```
[ ] Consider final trim or full exit
[ ] Huge gains = don't give back
[ ] Trail stop to within 3-5% of current price
[ ] Exit on first close below 21 EMA
```

---

## WEEKLY RISK REVIEW (Every Sunday)

**Part of Weekly Routine** (from Section 2):

```
WEEKLY RISK METRICS REVIEW:

1. CURRENT DRAWDOWN
   Account peak (all-time high): $_____
   Current account value: $_____
   Drawdown: ___% = (Peak - Current) / Peak × 100
   
   [ ] <5%: Normal, continue ✓
   [ ] 5-10%: Level 1 alert, reduce risk
   [ ] 10-15%: Level 2 alert, stop trading 1 week
   [ ] >15%: Level 3 alert, full stop, go to cash

2. PORTFOLIO HEAT
   Position 1: ___% heat
   Position 2: ___% heat
   Position 3: ___% heat
   [... all positions]
   
   Total heat: ___%
   Max allowed: ___%
   Status: Under / Over ___

3. WIN RATE (Last 10 Trades)
   Wins: ___ / 10 = ___%
   Losses: ___ / 10 = ___%
   
   [ ] Win rate ≥50%: On track ✓
   [ ] Win rate <50%: Review needed ⚠
   [ ] Win rate <40%: Stop trading, paper trade 2 weeks ✗

4. AVERAGE WIN/LOSS RATIO
   Avg winning trade: $___
   Avg losing trade: $___
   Ratio: ___ : 1
   
   [ ] Ratio >1.5:1: Excellent ✓
   [ ] Ratio 1:1 - 1.5:1: Acceptable
   [ ] Ratio <1:1: Cutting winners, holding losers ✗

5. CONSECUTIVE LOSSES
   Current streak: ___ losses in a row
   
   [ ] 0-2: Normal
   [ ] 3: Stop 2 days, review
   [ ] 5+: Stop 1 week, paper trade

6. ACTION ITEMS FOR NEXT WEEK
   [ ] Continue normal trading
   [ ] Reduce position sizing by ___%
   [ ] Tighten stops on all positions
   [ ] Stop trading for ___ days
   [ ] Paper trade only
   [ ] Other: _____________
```

---

## YOUR RISK MANAGEMENT RULES (Print and Post)

```
═══════════════════════════════════════════════
        MY TRADING RISK RULES
        (Non-Negotiable)
═══════════════════════════════════════════════

1. EVERY trade has a stop loss placed BEFORE entry
2. NEVER risk more than 0.5% per trade (Env A)
3. NEVER risk more than 0.25% per trade (Env C)
4. Portfolio heat NEVER exceeds environment limits
5. 3 losses in a row = STOP 2 days
6. -5% drawdown = Reduce sizing 25%
7. -10% drawdown = STOP 1 week, review
8. -15% drawdown = STOP 1 month, full reset
9. NEVER move stops against me (wider)
10. ALWAYS let winners run (trail stops)
11. Cut losses quickly (<7 days)
12. Position sizes based on edges + environment
13. Maximum position: 20% (Env A), 10% (Env C)
14. Risk-based sizing trumps position-based
15. When in doubt, trade SMALLER
16. Protect capital FIRST, profits second
17. If it feels too big, it probably is - reduce
18. Perfect execution > perfect prediction
19. Journal EVERY trade (no exceptions)
20. Rules exist to protect me from myself

═══════════════════════════════════════════════

SIGNED: ________________  DATE: _________

POST THIS WHERE YOU TRADE (monitor, wall, desk)
READ BEFORE EVERY TRADING SESSION
═══════════════════════════════════════════════
```

---

## YOUR NEXT STEPS

**This Week**:
- [ ] Read Section 4 completely
- [ ] Calculate ATR for 10 stocks you're watching
- [ ] Practice stop loss placement (5 examples)
- [ ] Practice position sizing calculations (5 scenarios)
- [ ] Create your Trade Execution Checklist (print it)

**Next Week**:
- [ ] Paper trade 5 trades with full risk management
- [ ] Calculate portfolio heat for each paper trade
- [ ] Practice drawdown calculations
- [ ] Set up weekly risk review template
- [ ] Print Risk Rules poster and post it

**Ongoing**:
- [ ] Use Trade Execution Checklist for EVERY trade
- [ ] Complete Weekly Risk Review every Sunday
- [ ] Monitor drawdown daily
- [ ] Adjust position sizes by environment
- [ ] Honor circuit breaker rules without exception

---

**You now have a complete, institutional-grade risk management system. Most retail traders never build this level of structure - they trade "by feel" and blow up. You will trade with calculated risk and survive to compound gains long-term.**

**Next**: Complete Section 5 (Sell Rules & Position Management) to learn exactly when to take profits and exit positions.

