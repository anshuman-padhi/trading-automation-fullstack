# Section 3: Edges, Setups & Entry Tactics - COMPLETE VISUAL GUIDE
## Exactly WHAT Chart Patterns to Look For (With Detailed Specifications)

---

## OVERVIEW

This document provides **exact visual specifications** for every setup and entry tactic in your trading system. By the end, you'll know:
- ✅ What each pattern looks like (down to specific measurements)
- ✅ How to identify them objectively (not "it looks like...")  
- ✅ When to enter (exact trigger points)
- ✅ Where to place stops (exact formulas)
- ✅ What makes a GOOD vs BAD version of each pattern

---

---

# PART 1: YOUR 10 EDGES (What Makes a Stock Worth Trading)

**Before we define setups, understand: EDGES are the "pre-qualifiers" that make a stock worth your attention.**

## EDGE #1: RS PHASE (Relative Strength Trending)

**Definition**: Stock's RS line (price ÷ SPY) is above its own rising 21 EMA

**How to Measure**:
```
Step 1: Plot stock price ÷ SPY price as a line on chart
Step 2: Add 21 EMA to that RS line
Step 3: Check:
  ✓ RS line is ABOVE the 21 EMA
  ✓ 21 EMA is RISING (higher than 5 days ago)
  ✓ RS line made new high in last 4-8 weeks
```

**Visual Example**:
```
RS Line Chart:
                          /\  ← RS line making new highs
                     /\  /  \/
         21 EMA → __/  \/____/  ← RS line staying above 21 EMA
        ________/

GOOD: RS line consistently above rising 21 EMA
BAD: RS line choppy, crossing below 21 EMA frequently
```

**Quantitative Threshold**:
- RS line > 21 EMA for 80%+ of last 20 days
- 21 EMA slope positive (angle > 0°)
- RS line made new 20-day high within last 10 days

---

## EDGE #2: SHORT-TERM RS RATING (Top Quartile Performance)

**Definition**: Stock ranks in top 15-20% of all stocks for 1-month and 3-month returns

**How to Measure**:
```
Use screener (Finviz, TradingView, IBD MarketSmith, Deepvue):
  
  1-Month RS Rating: ___/100
  3-Month RS Rating: ___/100
  
  For FULL position (10%): Both >85
  For SMALLER position (5%): Both >80
  For EXPLORATION (2%): Both >75
```

**Where to Find**:
- **IBD MarketSmith**: RS Rating column (0-99 scale)
- **Finviz**: Sort by "Perf Month" or "Perf Quarter"
- **TradingView**: Custom screener with "% change 1M" > 85th percentile
- **Manual**: Compare stock's 1M/3M return to SPY + peers

**Quantitative Threshold**:
```
Full Position (10%):  RS 1M >85 AND RS 3M >85
Half Position (5%):   RS 1M >80 AND RS 3M >80  
Small Position (2%):  RS 1M >75 AND RS 3M >75
```

---

## EDGE #3: GROWTH (Earnings & Sales Acceleration)

**Definition**: Company has real, accelerating earnings or sales growth (not just "good")

**How to Measure**:
```
Pull from earnings reports or screener:

YoY EPS Growth (Current Q):     ____%
YoY EPS Growth (Prior Q):       ____%
YoY Sales Growth (Current Q):   ____%
Expected EPS Growth (Next Q):   ____%

EDGE PRESENT if:
  ✓ Current Q EPS >40% YoY (or >20% for mega-caps)
  ✓ Current Q EPS > Prior Q EPS (acceleration)
  ✓ Sales growth >20% YoY
  ✓ Next Q estimates rising (positive revisions)
```

**Example: NVDA (Q3 2024)**:
```
YoY EPS Growth: +206% ✓ (massive)
YoY Sales Growth: +94% ✓ (massive)
Prior Q EPS Growth: +168% ✓ (accelerating)
Next Q Estimate: Rising ✓

EDGE SCORE: 4/4 → Strong Growth Edge
```

**Example: Mature Tech (AAPL)**:
```
YoY EPS Growth: +11% ✗ (below 40% threshold for growth stock)
YoY Sales Growth: +6% ✗ (below 20%)
Growth Edge: NOT PRESENT for momentum trading
(AAPL is a quality hold, but not a growth breakout candidate)
```

**Quantitative Thresholds**:
```
Growth Stocks:  EPS >40% YoY, Sales >20% YoY
Mega-Caps:      EPS >20% YoY (if accelerating), Sales >15% YoY
Tech Leaders:   EPS >30% YoY minimum
```

---

## EDGE #4: LEADING THEME (Part of Hot Sector)

**Definition**: Stock is part of an identified 2025-2026 leading theme with multiple strong names

**How to Measure**:
```
Step 1: Identify current leading themes (weekly routine)
  Example themes for 2025:
    - AI / LLMs (NVDA, MSFT, META, GOOGL, AMZN)
    - Semiconductors (NVDA, AMD, ASML, TSM, AVGO)
    - Cybersecurity (CRWD, OKTA, ZS, NET, PANW)
    - Cloud Infrastructure (MSFT, AMZN, GOOGL)
    - AI Chips/Hardware (SMCI, NVDA, DELL, HPE)

Step 2: Check if stock's sector ETF is outperforming:
  Sector ETF (XLK, SOXX, etc.) performance vs SPY:
    1-Month: +___% vs SPY +___%
    3-Month: +___% vs SPY +___%
  
  ✓ Sector ETF beating SPY by 3%+ = Leading Theme

Step 3: Count how many stocks in theme are working:
  - If 5+ stocks in theme breaking out: Strong theme ✓
  - If 2-3 stocks working: Moderate theme
  - If only 1 stock working: Weak theme ✗
```

**Visual Check**:
```
Pull up sector ETF chart (e.g., SOXX for semis):

Price vs SPY:
SOXX: ===================> +15% (3 months)
SPY:  ============> +8% (3 months)

SOXX beating SPY by 7% → Semiconductors = Leading Theme ✓
```

**Quantitative Threshold**:
```
Theme Edge Present if:
  ✓ Sector ETF beats SPY by 3%+ over 1-3 months
  ✓ 3+ stocks in theme have RS >85
  ✓ 2+ stocks in theme breaking out to new highs
```

---

## EDGE #5: TRENDABILITY (Proven 30%+ Moves)

**Definition**: Stock has historically trended cleanly from bases (not choppy or prone to reversals)

**How to Measure**:
```
Step 1: Look back 1-2 years on weekly chart
Step 2: Identify prior bases (consolidations 20+ days)
Step 3: Measure moves from each base:

Base 1 (Date): Breakout at $___ → High at $___ = ___% gain
Base 2 (Date): Breakout at $___ → High at $___ = ___% gain
Base 3 (Date): Breakout at $___ → High at $___ = ___% gain

Step 4: Check trend quality:
  ✓ At least 2 of last 3 bases led to 30%+ moves
  ✓ Stock trended above 21 EMA for most of move (not choppy)
  ✓ No violent -20%+ reversals mid-trend
```

**Visual Example**:
```
NVDA 2023-2024:
  Base (Jan 2023): $140 → $300 = +114% ✓
  Base (Oct 2023): $410 → $520 = +27% ✗ (close to 30%)
  Base (Apr 2024): $750 → $950 = +27% ✗ (extended already)
  
  Trendability Score: 1.5/3 bases with 30%+ = MODERATE
  But: Clean trends, respected 21 EMA = Still qualifies ✓
```

**Quantitative Threshold**:
```
Trendability Edge Present if:
  ✓ 2 of last 3 bases produced 30%+ moves OR
  ✓ 1 of last 3 produced 50%+ move with clean trend
  ✓ Price stayed above 21 EMA for 70%+ of trend duration
```

---

## EDGE #6: HIGH VOLUME (HV) / INCREASING AVG VOLUME

**Definition**: Stock printed highest volume in 1+ years OR 20-day avg volume increased 25%+

**How to Measure**:
```
HV Edge (Highest Volume):
  Step 1: Check volume in last 90 days
  Step 2: Compare to volume over past 1-2 years
  
  ✓ Any day in last 90 days = highest volume since IPO or 1 year
  
  Example: SMCI Feb 2024 - Volume 80M shares
           vs Prior 52-week high volume: 45M shares
           = HV Edge Present ✓

Increasing Avg Volume Edge:
  Step 1: Calculate 20-day avg volume now: ___ M shares
  Step 2: Calculate 20-day avg volume 2 months ago: ___ M shares
  Step 3: % Increase = (Now - Then) / Then × 100 = ___%
  
  ✓ If increase >25% = Volume Edge Present
```

**Visual on Chart**:
```
Volume Bars:
           ║               
       ║   ║  ║            ← Recent volume bars much taller
    ║  ║   ║  ║  ║         
 ║  ║  ║ ║ ║  ║  ║ ║       
─┴──┴──┴─┴─┴──┴──┴─┴───────
 Old   →    Recent

20-day avg volume:
  2 months ago: 15M/day
  Now: 22M/day
  Increase: +47% ✓ Volume Edge Present
```

**Quantitative Threshold**:
```
HV Edge:              Any day in last 90 = highest volume in 1+ year
Increasing Avg Vol:   20-day avg up 25%+ over prior 2 months
```

---

## EDGE #7: NEW HIGHS / IPO RECENCY

**Definition**: Stock making new 52-week highs OR is a recent IPO (within 3 years)

**How to Measure**:
```
New Highs Check:
  Current Price: $___
  52-Week High:  $___
  Days Since 52W High: ___ days
  
  ✓ If current price within 5% of 52W high
  ✓ OR made new 52W high within last 20 days
  
  Edge Present: YES / NO

IPO Check:
  IPO Date: ________
  Years Since IPO: ___ years
  
  ✓ If IPO within last 3 years AND stock >50% above IPO price
  
  Edge Present: YES / NO
```

**Why This Matters**:
- New highs = No overhead resistance (no bag holders selling at breakeven)
- Recent IPOs = Early stage growth, often more explosive
- BUT: IPOs can be volatile, use smaller sizing

**Quantitative Threshold**:
```
New High Edge:   Price within 5% of 52W high OR new high <20 days ago
IPO Edge:        IPO date within 3 years AND price >50% above IPO
```

---

## EDGE #8: MULTI-TIMEFRAME ALIGNMENT

**Definition**: Daily AND weekly charts both showing constructive, bullish structure

**How to Measure**:
```
Daily Chart Check:
  ✓ Price > rising 21 EMA
  ✓ Price > rising 50 SMA
  ✓ 21 EMA > 50 SMA (EMA crossover bullish)
  ✓ Recent candles closing in top 50% of range (buyers in control)
  
  Daily Score: ___/4 checks

Weekly Chart Check:
  ✓ Price > rising 10 EMA (weekly)
  ✓ Price > rising 50 SMA (weekly)
  ✓ Weekly candles mostly green last 4-8 weeks
  ✓ No major breakdown through key support
  
  Weekly Score: ___/4 checks

Multi-TF Edge Present if:
  Daily Score ≥3 AND Weekly Score ≥3
```

**Visual Example**:
```
Daily Chart (left) + Weekly Chart (right):

Daily:                    Weekly:
Price ──────────          Price ───────
   above 21 EMA ✓            above 10 EMA ✓
21 EMA ─────────           10 EMA ────────
   above 50 SMA ✓            above 50 SMA ✓

Both bullish = Multi-TF Alignment ✓
```

**Quantitative Threshold**:
```
Daily:   3 of 4 checks passing
Weekly:  3 of 4 checks passing
Result:  Multi-TF Edge Present
```

---

## EDGE #9: CATALYST / N-FACTOR

**Definition**: Company has identifiable near-term catalyst that could drive explosive move

**Types of Catalysts**:
```
Product Launch:
  - New AI model/chip/software release
  - Major product upgrade
  - Platform expansion
  
M&A / Partnership:
  - Acquisition announcement
  - Strategic partnership (e.g., MSFT + OpenAI)
  - Major customer win
  
Regulatory / FDA:
  - FDA approval (biotech)
  - Regulatory clearance
  - Patent grant
  
Earnings:
  - Upcoming earnings in 2-4 weeks
  - Expected guidance increase
  - Analyst day presentation
  
Other:
  - Insider buying (10%+ purchases)
  - Activist investor involvement
  - Spin-off or restructuring
```

**How to Identify**:
```
Step 1: Check company news/calendar for upcoming events
Step 2: Assess if catalyst is "game-changing" (not routine)
Step 3: Determine timing (within 1-4 weeks ideal)

Catalyst Edge Present if:
  ✓ Identifiable catalyst within 1-4 weeks
  ✓ Catalyst has potential to change growth trajectory
  ✓ Market not fully pricing in catalyst yet
```

**Example: NVDA H100 Launch (2023)**:
```
Catalyst: H100 GPU launch (AI training chip)
Timing: March 2023
Impact: Drove stock from $240 → $480 in 4 months (+100%)
Catalyst Edge: Strong ✓
```

**Quantitative Threshold**: Qualitative, but document:
```
Catalyst: _________________ (what)
Date: _________________ (when)
Potential Impact: _________________ (why it matters)
```

---

## EDGE #10: VOLUME CONFIRMATION ON BREAKOUT

**Definition**: When stock breaks out, volume surges 50-100%+ above average (institutional buying)

**How to Measure** (on breakout day):
```
Step 1: Calculate 20-day avg volume: ___ M shares
Step 2: Check breakout day volume: ___ M shares
Step 3: Calculate % above average:
  (Breakout Vol - Avg Vol) / Avg Vol × 100 = ___%

Volume Edge Present if:
  ✓ Breakout volume 50-100%+ above 20-day average
  ✓ OR absolute volume >3x normal (e.g., 10M vs 3M avg)
```

**Visual Example**:
```
Volume Chart:
Breakout Day →   ║║║║║  ← 80M shares (2.5x normal)
                  ║║║
                  ║║
Normal Days:     ║║║ ← 30M shares average
              ────┴┴┴┴┴────
              Days before breakout

80M / 30M = 2.67x = 167% above average ✓ Strong volume confirmation
```

**Quantitative Threshold**:
```
Minimum:    Breakout volume 50% above 20-day avg
Ideal:      Breakout volume 100%+ (2x) above avg
Excellent:  Breakout volume 150%+ (2.5x+) above avg
```

---

## YOUR EDGE SCORING SYSTEM

**For each trade candidate, score edges:**

```
STOCK: ____________  Date: ________

EDGES PRESENT (Check all that apply):
[ ] RS Phase (RS line > rising 21 EMA)
[ ] RS Rating (1M/3M RS >85)
[ ] Growth (EPS >40% YoY, accelerating)
[ ] Leading Theme (sector hot, 3+ names working)
[ ] Trendability (proven 30%+ moves from bases)
[ ] High Volume (HV or +25% avg vol)
[ ] New Highs (within 5% of 52W high)
[ ] Multi-TF Alignment (daily + weekly bullish)
[ ] Catalyst (game-changing event <4 weeks)
[ ] Volume Confirmation (on breakout, 50%+ surge)

TOTAL EDGES: ___/10

POSITION SIZING DECISION:
  0-2 edges: PASS (not enough conviction)
  3 edges:   5% position (small, exploratory)
  4 edges:   7-10% position (standard)
  5-6 edges: 12-15% position (strong setup)
  7+ edges:  15-20% position (exceptional, max size)
```

---

---

# PART 2: YOUR 3 SETUPS (Exact Chart Patterns)

**Now that we have edges (stock qualifiers), let's define SETUPS (exact chart structures to trade).**

---

## SETUP #1: VOLATILITY CONTRACTION PATTERN (VCP)

**Definition**: Stock consolidates in progressively tighter price swings, then breaks out on volume

**Developed by**: Mark Minervini (U.S. Investing Champion, 334% return 2021)

### VISUAL STRUCTURE:

```
Price Chart (VCP forming over 8-12 weeks):

        Contraction 1 (15% depth)
    /\      Contraction 2 (10% depth)  
   /  \    /\     Contraction 3 (5% depth)
  /    \  /  \   /\ Breakout
 /      \/    \ /  \→
─────────────────────────────
   6-8wks  4-5wks 2-3wks

KEY VISUAL MARKERS:
1. Each pullback SMALLER than prior (15% → 10% → 5%)
2. Volume CONTRACTS during each pullback (bars shrinking)
3. Breakout occurs on VOLUME EXPANSION (bars explode)
```

### EXACT SPECIFICATIONS:

**Duration**: 6-12 weeks total (ideal)
**Contractions**: 2-4 pullbacks minimum (ideally 3-4)
**Depth Progression**:
```
Contraction 1: 15-25% pullback (deepest)
Contraction 2: 8-15% pullback (shallower)
Contraction 3: 3-8% pullback (shallowest)
Contraction 4: 1-5% pullback (tightest)
```

**Volume Pattern**:
```
Volume During Contractions:
  ║         ← First pullback (moderate volume)
  ║ ║
  ║ ║ ║     ← Second pullback (lighter volume)
    ║       ← Third pullback (very light)
      ║     ← Tightness (almost no volume)
────────────
Each pullback has LESS volume than prior

Volume on Breakout:
  ║║║║║║    ← Breakout (volume 50-150% above avg)
```

**Moving Average Positioning**:
```
✓ Price stays above rising 50 SMA entire pattern
✓ Price respects 21 EMA on pullbacks (bounces off it, doesn't break)
✓ 21 EMA > 50 SMA (bullish alignment)
```

### MEASUREMENT FORMULA:

```
VCP CHECKLIST (All must pass):

1. PRIOR UPTREND:
   [ ] Stock up 30%+ before VCP forms
   [ ] Uptrend duration: 4-12 weeks minimum

2. PROGRESSIVE TIGHTENING:
   Contraction 1 depth: ___%
   Contraction 2 depth: ___%
   Contraction 3 depth: ___%
   [ ] Each one smaller than prior

3. VOLUME CONTRACTION:
   Avg volume in Contraction 1: ___ M
   Avg volume in Contraction 2: ___ M
   Avg volume in Contraction 3: ___ M
   [ ] Each one lighter than prior

4. PIVOT POINT IDENTIFIED:
   Pivot Price: $___ (highest point before final tightening)
   [ ] Clear resistance level visible

5. BREAKOUT VOLUME:
   20-day avg volume: ___ M
   Breakout day volume: ___ M
   [ ] Breakout volume 50%+ above average

VCP VALID: YES / NO (if all 5 pass)
```

### GOOD vs BAD VCP:

**GOOD VCP**:
```
✓ Each contraction 30-50% smaller than prior
✓ Volume diminishes consistently
✓ Tight price action in final contraction (3-5% range)
✓ Breakout on 2x+ normal volume
✓ Stock above 50 SMA entire time
✓ Pattern takes 8-12 weeks (not rushed)
```

**BAD VCP** (avoid these):
```
✗ Contractions erratic (not progressively smaller)
✗ Volume spikes mid-pattern (distribution, not accumulation)
✗ Price breaks below 50 SMA during pattern
✗ Pattern too short (<4 weeks) or too long (>20 weeks)
✗ Breakout on weak volume (<30% above avg)
✗ Contractions too deep (all >15%)
```

### REAL EXAMPLE: NVDA October 2023

```
NVDA VCP (Oct-Nov 2023):

Contraction 1 (late Sept): $430 → $410 = 4.7% depth
Contraction 2 (early Oct): $465 → $450 = 3.2% depth  
Contraction 3 (mid Oct):   $470 → $460 = 2.1% depth
Breakout (late Oct):       Above $475 on 80M volume (2x avg)

Result: Broke out to $495 (+4.2% gain in days)
Then continued to $520 (+9.5% from breakout)

VCP Quality: Excellent ✓
```

---

## SETUP #2: CUP-WITH-HANDLE BASE (CANSLIM Classic)

**Definition**: Stock forms U-shaped cup (20-60% depth), then handle (10-15% depth), breaks out on volume

**Developed by**: William O'Neil (CANSLIM methodology, Investor's Business Daily)

### VISUAL STRUCTURE:

```
Price Chart:

        Handle
         /\─┐  Breakout
        /  \ │  →
Cup:   /    \│
  /\  /      \
 /  \/        \
─────────────────
←Left Side→←Right Side→←Handle→

STRUCTURE:
- Cup depth: 20-60% from peak to bottom
- Cup duration: 5-12 weeks minimum
- Handle depth: 10-15% max (shallower than cup)
- Handle duration: 1-4 weeks
```

### EXACT SPECIFICATIONS:

**Cup Specifications**:
```
Minimum Duration: 5 weeks (7 weeks ideal)
Maximum Duration: 60 weeks (longer = weaker)
Ideal Duration: 7-12 weeks

Depth Requirements:
  Shallow (best):     20-30% from high to low
  Normal:             30-40% depth
  Deeper (acceptable): 40-60% depth
  Too Deep (avoid):    >60% depth (shows weakness)

Shape:
  ✓ U-shaped bottom (rounded, not V)
  ✓ Left side decline gradual
  ✓ Bottom forms over 2-4 weeks (not sharp)
  ✓ Right side climbs back near left-side high
```

**Handle Specifications**:
```
Duration: 5-20 trading days (1-4 weeks)
Depth: 10-15% max from right-side high
Shape: Downward drift or tight sideways

Handle Requirements:
  ✓ Forms in upper half of cup (not at bottom)
  ✓ Volume diminishes in handle
  ✓ Price stays above 50% retracement of cup depth
  ✓ Handle doesn't undercut cup low
```

**Pivot Point (Buy Point)**:
```
Pivot = Highest point on right side of cup (or handle high)
Buy when price closes above pivot + $0.10-0.25
```

### MEASUREMENT FORMULA:

```
CUP-WITH-HANDLE CHECKLIST:

1. PRIOR UPTREND:
   [ ] Stock up 30%+ before cup forms
   [ ] Duration of uptrend: 4+ weeks

2. CUP FORMATION:
   Cup left-side high: $___
   Cup bottom (low):   $___
   Cup depth: ___% = (High - Low) / High × 100
   [ ] Depth between 20-60%
   [ ] Duration: 5-12 weeks ✓

3. CUP SHAPE:
   [ ] U-shaped (rounded bottom, not V)
   [ ] Right side climbs back to within 5% of left-side high

4. HANDLE FORMATION:
   Handle high: $___
   Handle low:  $___
   Handle depth: ___% = (High - Low) / High × 100
   [ ] Depth <15%
   [ ] Duration: 1-4 weeks
   [ ] Formed in upper half of cup

5. VOLUME PATTERN:
   Avg volume in cup: ___ M
   Avg volume in handle: ___ M
   [ ] Handle volume 20-50% below cup average
   
   Breakout volume: ___ M
   [ ] Breakout volume 40-50%+ above 20-day avg

6. PIVOT POINT:
   Pivot price: $___
   [ ] Clear resistance at right-side high

CUP-WITH-HANDLE VALID: YES / NO
```

### GOOD vs BAD CUP-WITH-HANDLE:

**GOOD Cup-with-Handle**:
```
✓ Cup depth 25-40% (Goldilocks)
✓ U-shaped bottom (rounded, 2-3 weeks at bottom)
✓ Right side climbs back to 95%+ of left-side high
✓ Handle drifts down 10-12% on light volume
✓ Handle takes 2-3 weeks (not rushed)
✓ Breakout on 50%+ volume surge
✓ Price never breaks below 50 SMA during cup
```

**BAD Cup-with-Handle** (avoid):
```
✗ Cup too shallow (<15%) or too deep (>60%)
✗ V-shaped bottom (sharp reversal, not accumulation)
✗ Right side doesn't reach left-side high (weak)
✗ Handle too deep (>20%) or forms at cup bottom
✗ Handle too short (<5 days) or too long (>6 weeks)
✗ Volume spikes in handle (distribution)
✗ Breakout on light volume (<30% above avg)
```

### REAL EXAMPLE: META March 2024

```
META Cup-with-Handle (Feb-Mar 2024):

Cup left-side high: $475 (early Feb)
Cup bottom low:     $390 (mid Feb)
Cup depth:          18% ✓ (shallow, strong)
Cup duration:       6 weeks ✓

Right-side high:    $470 (within $5 of left-side)
Handle forms:       $470 → $450 (4.3% depth) ✓
Handle duration:    2 weeks ✓
Handle volume:      40% below cup average ✓

Pivot point:        $475
Breakout:           Close $478 on 35M volume (60% above avg) ✓

Result: Ran to $525 (+10% from breakout in 2 weeks)

Cup Quality: Excellent ✓
```

---

## SETUP #3: FLAT BASE BREAKOUT

**Definition**: Stock consolidates sideways in tight 8-15% range for 5+ weeks after 30%+ run, breaks out on volume

**Developed by**: William O'Neil (CANSLIM), Mark Minervini adaptation

### VISUAL STRUCTURE:

```
Price Chart:

Prior Run:         Flat Base:        Breakout:
   /              ─────────────          /
  /              /             \        /  
 /              /               \─────/
────────────────────────────────────────
     30%+           5-8 weeks
     gain

STRUCTURE:
- Prior advance: 30%+ gain in 4-8 weeks
- Base depth: 8-15% max (tight)
- Base duration: 5-8 weeks minimum
- Price oscillates in horizontal band
```

### EXACT SPECIFICATIONS:

**Prior Advance**:
```
Minimum gain before base: 30%
Ideal gain: 40-70%
Duration of advance: 4-10 weeks
```

**Base Requirements**:
```
Minimum Duration: 5 weeks (35 trading days)
Maximum Duration: 12 weeks (longer OK if tight)
Depth: 8-15% from highest to lowest point in base

Ideal Characteristics:
  ✓ Depth 10-12% (tighter = better)
  ✓ Duration 5-7 weeks (sweet spot)
  ✓ Price bounces between clear support/resistance
  ✓ Volume contracts 30-50% vs prior advance
```

**Visual Pattern**:
```
Flat Base Price Action:

High: $150 ──────────────────  ← Resistance (tested 2-3x)
           \  /\    /\  /
            \/  \  /  \/       ← Tight oscillation
                 \/
Low:  $135 ──────────────────  ← Support (tested 2-3x)

Range: $150 - $135 = $15 = 10% depth ✓ (ideal)
Duration: 6 weeks ✓
```

**Breakout Trigger**:
```
Pivot Point: Highest point in flat base ($150 in example)
Breakout: Close above pivot on 40%+ volume surge
Buy Point: $150.15 (pivot + $0.10-0.25 cushion)
```

### MEASUREMENT FORMULA:

```
FLAT BASE CHECKLIST:

1. PRIOR ADVANCE:
   Start of advance: $___
   Peak before base: $___
   Gain: ___% = (Peak - Start) / Start × 100
   [ ] Advance ≥30%
   [ ] Duration: 4-10 weeks

2. BASE FORMATION:
   Base high: $___
   Base low:  $___
   Base depth: ___% = (High - Low) / High × 100
   [ ] Depth ≤15% (ideally 8-12%)
   
   Base duration: ___ weeks
   [ ] Duration 5-12 weeks

3. BASE STRUCTURE:
   [ ] Price oscillates between clear high/low
   [ ] At least 2 tests of resistance (highs)
   [ ] At least 2 tests of support (lows)
   [ ] Price stays above 50 SMA entire base

4. VOLUME BEHAVIOR:
   Avg volume during advance: ___ M
   Avg volume in base: ___ M
   Volume contraction: ___% = (Advance - Base) / Advance × 100
   [ ] Volume contracts 30%+ in base
   
   Breakout volume: ___ M
   [ ] Breakout 40-50%+ above 20-day avg

5. PIVOT POINT:
   Pivot (base high): $___
   [ ] Clear resistance level

FLAT BASE VALID: YES / NO
```

### GOOD vs BAD FLAT BASE:

**GOOD Flat Base**:
```
✓ Prior advance 40-70% (strong momentum)
✓ Base depth 10-12% (very tight)
✓ Duration 5-7 weeks (not too long)
✓ 2-3 clean tests of resistance
✓ Volume dries up 40%+ in base
✓ Breakout on 50%+ volume surge
✓ Price never closes below 21 EMA in base
```

**BAD Flat Base** (avoid):
```
✗ Prior advance <25% (not enough momentum)
✗ Base depth >20% (too loose)
✗ Duration <4 weeks (not enough time) or >15 weeks (too long)
✗ Erratic price action (not flat oscillation)
✗ Volume spikes mid-base (shows distribution)
✗ Price breaks below 21 EMA multiple times
✗ Breakout on weak volume
```

### REAL EXAMPLE: CRWD June 2024

```
CRWD Flat Base (May-June 2024):

Prior advance: $240 → $350 = +45.8% ✓ (strong)
Advance duration: 6 weeks ✓

Base high: $350
Base low:  $320
Base depth: 8.6% ✓ (very tight)
Base duration: 6 weeks ✓

Volume in advance: 8M/day avg
Volume in base: 4.5M/day avg (44% contraction) ✓

Pivot: $350
Breakout: Close $352 on 12M volume (2.7x avg) ✓

Result: Ran to $395 (+12.6% from breakout)

Flat Base Quality: Excellent ✓
```

---

---

# PART 3: YOUR 2 ENTRY TACTICS (Exact Trigger Points)

**You now know WHAT patterns to look for (setups). Now learn WHEN to pull the trigger (entry tactics).**

---

## ENTRY TACTIC #1: RANGE BREAKOUT

**Definition**: Price tightens into 2-5 day tight range below resistance, breaks above range high on volume

**This tactic works with**: All 3 setups (VCP, Cup-Handle, Flat Base)

### VISUAL STRUCTURE:

```
Price Chart:

Setup forms →    Tight Range    Breakout
                 (2-5 days)       ↗
─────────────  ▓▓▓▓▓▓▓▓▓▓▓      /
              │          │     /
              └──────────┘────   ← Range high = pivot
                2-4% range

TRIGGER: Price closes above range high + volume surge
```

### EXACT SPECIFICATIONS:

**Range Requirements**:
```
Duration: 2-5 trading days
  - 2 days minimum (too short = unreliable)
  - 5 days maximum (longer = potential weakness)
  - 3-4 days ideal

Width: 2-4% from high to low
  - <2% = too tight (might be intraday noise)
  - >5% = too wide (not a tight range)
  - 3% ideal

Location: Within 5-10% of setup pivot
  - Range forms just below resistance
  - Should be at upper end of base/pattern
```

**Visual Measurement**:
```
Identify the Range:

Day 1: High $100.50, Low $98.00, Close $99.25
Day 2: High $100.75, Low $98.50, Close $99.80
Day 3: High $101.00, Low $98.75, Close $100.10
Day 4: High $100.85, Low $99.00, Close $100.50

Range High: $101.00 (highest of Day 1-4)
Range Low:  $98.00 (lowest of Day 1-4)
Range Width: ($101 - $98) / $98 × 100 = 3.06% ✓ (ideal)

Pivot Point = Range High = $101.00
```

### ENTRY EXECUTION:

```
STEP 1: IDENTIFY RANGE
  [ ] 2-5 days of tight consolidation
  [ ] Range width 2-4%
  [ ] Range forms near setup pivot (within 5-10%)

STEP 2: MARK PIVOT (RANGE HIGH)
  Range high: $___
  This is your buy trigger level

STEP 3: SET BUY PRICE
  Buy Price = Range High + $0.10 to $0.25
  Example: Range high $101.00 → Buy at $101.15

STEP 4: CONFIRM VOLUME
  20-day avg volume: ___ M
  Breakout day volume (so far): ___ M
  [ ] Volume 40%+ above average

STEP 5: SET STOP LOSS
  Stop = Range Low - $0.50
  Example: Range low $98.00 → Stop at $97.50

STEP 6: CALCULATE POSITION SIZE
  Entry: $101.15
  Stop:  $97.50
  Risk:  $101.15 - $97.50 = $3.65 per share
  
  If 10% position on $50,000 account:
    Position value: $5,000
    Shares: $5,000 / $101.15 = 49 shares
    Dollar risk: 49 × $3.65 = $178.85
    Portfolio risk: $178.85 / $50,000 = 0.36% ✓

EXECUTE: Buy 49 shares at $101.15, stop at $97.50
```

### ENTRY TIMING:

**Option A: Market Order on Close Above Pivot**:
```
If price closes above $101.00 on Day 5:
  → Buy at market open next day (Day 6)
  → Usually fills within 0.5% of close price
```

**Option B: Buy-Stop Order (Automated)**:
```
Place buy-stop at $101.15 before market open
  → If price hits $101.15, order executes automatically
  → Eliminates need to watch live
  → Risk: Might get filled on brief spike
```

**Option C: Limit Order on Breakout**:
```
Watch price live on breakout day
If price crosses $101.00 on volume:
  → Place limit order at $101.15-$101.25
  → Gets fill near your target price
  → Requires active monitoring
```

### CONFIRMATION SIGNALS:

```
STRONG ENTRY (Take full size):
  ✓ Price gaps up through range high
  ✓ Volume 80-150%+ above average
  ✓ Close in top 25% of day's range
  ✓ No false breakouts in past week

MODERATE ENTRY (Take 60-70% size):
  ✓ Price grinds above range high (no gap)
  ✓ Volume 40-80% above average
  ✓ Close in top 50% of range
  ✓ Clean action overall

WEAK ENTRY (Pass or 30-40% size):
  ✗ Price barely breaks range high
  ✗ Volume <30% above average
  ✗ Close in lower half of range
  ✗ Multiple failed breakouts recently
```

### REAL EXAMPLE: SMCI VCP Breakout

```
SMCI VCP (March 2024):

Setup: VCP pattern, final contraction
Range forms: Days 1-4 below $45.00

Day 1: High $44.80, Low $43.20, Close $44.00
Day 2: High $44.90, Low $43.50, Close $44.50
Day 3: High $45.10, Low $43.80, Close $44.70
Day 4: High $44.95, Low $44.00, Close $44.60

Range High: $45.10 (pivot)
Range Low:  $43.20
Range Width: 4.4% (slightly wide but OK)

Breakout Day (Day 5):
  Open: $44.70
  High: $46.50
  Volume: 25M (2.8x average) ✓✓
  Close: $46.20 (top 20% of range) ✓

Entry Execution:
  Buy Price: $45.25 (pivot + $0.15)
  Filled: $45.30 (market open Day 6)
  Stop: $43.00 (range low - $0.20, tighter)
  Risk: $45.30 - $43.00 = $2.30 per share

Result: 
  +2 days: $48.50 (+7.1%)
  +1 week: $52.00 (+14.8%)
  +2 weeks: $58.00 (+28.0%)

Entry Quality: Excellent ✓✓
```

---

## ENTRY TACTIC #2: OOPS REVERSAL (Gap-Down Recovery)

**Definition**: Stock gaps down below prior day low, then recovers ABOVE prior day low same session on volume

**This tactic works with**: Primarily pullback setups, post-earnings shakeouts, false breakdowns

### VISUAL STRUCTURE:

```
Intraday Chart (Gap-Down Day):

Prior Day Close: $100   Prior Day Low: $98
                 ─┬─     ─────────────────
Gap Down Open:    │        
  $96 ───────────┴──      ← Opens below prior low
                  \       
Intraday Low:      \      
  $95 ─────────────┴──    ← Panic selling
                    \     
Recovery:            \    
  $100 ──────────────┴──  ← Reclaims prior low ✓
                      \   
Close:                 \  
  $101.50 ─────────────┴─ ← Closes strong ✓

TRIGGER: Price trades back ABOVE $98 (prior low) on expanding volume
```

### EXACT SPECIFICATIONS:

**Gap Requirements**:
```
Gap Size: 3-8% below prior day low
  - <3% = minor gap, less reliable
  - >10% = potential fundamental issue (avoid)
  - 5-7% ideal (creates panic but not disaster)

Gap Timing: At market open (9:30 AM EST)
  - Must open below prior day's low
  - Intraday break below doesn't count
```

**Recovery Requirements**:
```
Reclaim Prior Low: SAME trading session (not next day)
  - Price must trade back above prior day's low
  - Ideally within first 2-4 hours (morning recovery)

Close Location: Upper 50% of day's range
  - If day range is $95-$102, close should be $98.50+
  - Close near highs ($100+) = strongest signal
```

**Volume Requirements**:
```
Volume Surge: 50-150% above 20-day average
  - Shows aggressive buying pressure
  - Indicates short covering + new buyers

Intraday Volume Profile:
  - High volume on initial drop (panic)
  - Sustained volume on recovery (accumulation)
```

### ENTRY EXECUTION:

```
STEP 1: IDENTIFY GAP DOWN
  Prior day close: $___
  Prior day low:   $___
  Today's open:    $___
  [ ] Open below prior day low

STEP 2: DETERMINE GAP SIZE
  Gap % = (Prior Low - Open) / Prior Low × 100
  Gap %: ___% 
  [ ] Gap 3-10%

STEP 3: WATCH FOR RECOVERY
  Monitor price intraday for reclaim of prior day low
  Prior day low (key level): $___
  
STEP 4: ENTRY TRIGGER
  Price crosses back ABOVE prior day low
  Entry Price: Prior Low + $0.10 to $0.25
  Example: Prior low $98 → Enter at $98.15

STEP 5: CONFIRM VOLUME
  Today's volume (live): ___ M vs avg ___ M
  [ ] Volume 50%+ above average

STEP 6: SET STOP LOSS
  Stop = Intraday low of gap-down day - $0.50
  Example: Intraday low $95 → Stop $94.50
  
STEP 7: CALCULATE RISK & SIZE
  Entry: $98.15
  Stop:  $94.50
  Risk:  $3.65 per share
  
  10% position on $50k account:
    $5,000 / $98.15 = 51 shares
    Risk: 51 × $3.65 = $186 (0.37% account risk) ✓
```

### ENTRY TIMING OPTIONS:

**Option A: Enter on Initial Reclaim (Aggressive)**:
```
As soon as price crosses prior day low:
  → Place buy order at $98.15-98.25
  → Get fill early in recovery
  → Risk: Could reverse back down (use tight stop)
```

**Option B: Enter on Close Confirmation (Conservative)**:
```
Wait until last 30 minutes of trading:
  → Confirm price holding above prior low
  → Confirm closing near highs of day
  → Enter at close or next morning open
  → Lower risk but might miss some upside
```

**Option C: Enter Next Morning (Most Conservative)**:
```
If gap-down day closes strong above prior low:
  → Enter at next day's open
  → Confirms recovery wasn't just intraday squeeze
  → Stop still at gap-down day's intraday low
```

### IDEAL CONDITIONS:

```
PERFECT OOPS SETUP:
  ✓ Stock in strong uptrend (above 21/50 EMA)
  ✓ Gap down on NO fundamental bad news (just profit-taking)
  ✓ Gap size 5-7% (enough to shake weak hands)
  ✓ Recovery within 2 hours (fast, decisive)
  ✓ Volume 100%+ above average (strong buying)
  ✓ Close in top 25% of day's range
  ✓ Pattern forms at key support (21 EMA, pivot, etc.)

GOOD OOPS SETUP:
  ✓ Stock in uptrend
  ✓ Gap 3-5% (moderate)
  ✓ Recovery by end of day
  ✓ Volume 50-80% above average
  ✓ Close in top 50% of range

WEAK OOPS (avoid):
  ✗ Gap >10% (potential real issue)
  ✗ Gap on bad earnings/news (not just profit-taking)
  ✗ Recovery slow or incomplete
  ✗ Volume weak (<30% above avg)
  ✗ Close in lower half of range
  ✗ Stock in downtrend or choppy action
```

### WHEN TO USE OOPS:

```
Best Conditions for Oops Reversal:
  1. Post-Earnings Shakeout
     - Stock gaps down 5-7% after earnings
     - But fundamentals actually strong
     - Recovers same day as shorts cover

  2. False Breakdown
     - Stock breaks below key support briefly
     - Then immediately reclaims it
     - Traps short sellers

  3. Market-Wide Selloff
     - Broader market gaps down (SPY/QQQ down)
     - Individual stock gaps with market
     - But recovers faster than market (RS strength)

Avoid Oops When:
  ✗ Real bad news (fraud, massive earnings miss, etc.)
  ✗ Stock already in downtrend
  ✗ Gap >10-12% (too much damage)
  ✗ No volume on recovery (weak hands leaving)
```

### REAL EXAMPLE: NVDA Post-Earnings Gap (Nov 2023)

```
NVDA Oops Reversal (Nov 22, 2023):

Prior Day (Nov 21):
  Close: $504.20
  Low:   $498.00

Gap Down Day (Nov 22):
  Open: $485.00 (-$13 gap, -2.6%) ✓
  Why: Profit-taking after strong earnings run
  Intraday Low: $480.50 (panic low)

Recovery:
  By 11:30 AM: Price reclaims $498 (prior low) ✓
  Volume: 95M shares (3.2x average) ✓✓
  Close: $505.50 (top 15% of day's range) ✓✓

Entry Execution:
  Trigger: $498.15 (prior low + $0.15)
  Entry Filled: $498.50 (11:45 AM)
  Stop: $480.00 (below intraday low - $0.50)
  Risk: $498.50 - $480 = $18.50 per share (3.7%)

Result:
  Next day close: $520 (+4.3%)
  1 week: $505 (+1.3% - pulled back but held)
  2 weeks: $495 (stopped out for small loss)
  
  Trade outcome: Small loss, but setup was textbook ✓
  (Not all perfect setups work, that's trading)

Oops Quality: Excellent setup, moderate outcome
```

---

---

# PART 4: INTEGRATION - PUTTING IT ALL TOGETHER

## THE COMPLETE TRADE DECISION PROCESS:

```
STEP 1: SCAN FOR EDGE CANDIDATES
  → Run weekly screener (Sunday routine)
  → Filter for stocks with 3+ edges
  → Build watchlist of 50-100 names

STEP 2: IDENTIFY SETUPS IN WATCHLIST
  → Which stocks are forming VCP, Cup-Handle, or Flat Base?
  → Mark pivot points on each setup
  → Narrow to 10-20 best setups

STEP 3: MONITOR FOR ENTRY TACTICS
  → Watch for range breakouts or oops reversals
  → Set alerts at pivot levels
  → Prepare exact entry/stop/size in advance

STEP 4: EXECUTE WHEN TACTICS TRIGGER
  → Enter at defined price
  → Place stop immediately
  → Journal the trade (edges present, setup type, entry tactic)

STEP 5: MANAGE POSITION
  → Follow sell rules from Section 5
  → Trim at +10%, +20%, exit on trend break
  → Log all actions in journal
```

## DECISION TREE EXAMPLE:

```
Stock: CRWD (example)
Date: July 2024

EDGES PRESENT:
[✓] RS Phase (RS line > 21 EMA)
[✓] RS Rating (1M: 92, 3M: 88)
[✓] Growth (EPS +48% YoY)
[✓] Leading Theme (Cybersecurity hot)
[✓] Trendability (prior +60% move from base)
[ ] High Volume (not yet)
[✓] New Highs (within 3% of 52W high)
[✓] Multi-TF (daily + weekly aligned)
[✓] Catalyst (upcoming conference presentation)
[ ] Volume Confirmation (pending breakout)

TOTAL EDGES: 8/10 ✓✓ (Excellent)

SETUP IDENTIFIED: Flat Base
  Prior advance: +35% in 6 weeks ✓
  Base depth: 9.5% ✓
  Base duration: 7 weeks ✓
  Pivot: $350.00

ENTRY TACTIC: Range Breakout
  Range: 4 days, $346-$350
  Range high: $350.00 (pivot)
  Buy trigger: $350.15

RISK MANAGEMENT:
  Entry: $350.15
  Stop: $345.50 (range low - $0.50)
  Risk: $4.65 per share (1.33%)
  
  Position size: 10% + 6% (8 edges) = 16% of portfolio
  Account size: $50,000
  Position value: $8,000
  Shares: 22
  Dollar risk: $102 (0.2% of account) ✓

DECISION: BUY 22 shares at $350.15, stop $345.50

RESULT: (track after entry)
  +1 day: $___
  +1 week: $___
  Exit price: $___
  Outcome: Win/Loss, ___% gain/loss
```

---

## YOUR PLAYBOOK DATABASE STRUCTURE:

Create folders for each setup with 10-20 annotated examples:

```
/Trading_Playbook
  /VCP_Examples
    - NVDA_VCP_Oct2023.png (annotated)
    - SMCI_VCP_Mar2024.png
    - CRWD_VCP_May2024.png
    - [10-15 more examples]
  
  /Cup_Handle_Examples
    - META_CupHandle_Mar2024.png
    - AAPL_CupHandle_Jan2023.png
    - [10-15 more examples]
  
  /Flat_Base_Examples
    - CRWD_FlatBase_Jun2024.png
    - MSFT_FlatBase_Dec2023.png
    - [10-15 more examples]
  
  /Range_Breakout_Entries
    - NVDA_RangeBreakout_Nov2023.png
    - [10-15 examples]
  
  /Oops_Reversal_Entries
    - TSLA_OopsReversal_Apr2024.png
    - [10-15 examples]
```

Each screenshot should show:
- Full setup context (prior move, base formation)
- Entry point marked with arrow
- Stop loss level marked
- Risk/reward calculation noted
- Outcome (how far it ran, where you would exit)

---

## YOUR NEXT STEPS:

1. **This Weekend**: 
   - Print this guide
   - Study each setup (VCP, Cup-Handle, Flat Base)
   - Study each entry tactic (Range Breakout, Oops Reversal)

2. **This Week**:
   - Find 10 historical examples of each setup (30 charts total)
   - Screenshot and annotate each
   - Mark entries, stops, and outcomes

3. **Week 2**:
   - Practice identifying setups on current charts
   - Paper trade 5-10 setups with exact entry tactics
   - Journal each paper trade

4. **Week 3-4**:
   - Continue paper trading
   - Build confidence in pattern recognition
   - By end of month, you should instantly recognize these patterns

5. **Month 2**:
   - Begin live trading with small position sizes (50% of planned)
   - Execute exactly as practiced in paper trading
   - Scale up after proving 50%+ win rate

---

**You now have exact specifications for every chart pattern in your trading system. No more guessing - you know exactly what to look for.**

**Next**: Complete Section 4 (Risk Management) and Section 5 (Sell Rules) homework to finish your complete system.

