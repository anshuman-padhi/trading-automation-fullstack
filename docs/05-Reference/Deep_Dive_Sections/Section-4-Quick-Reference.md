# Section 4 QUICK REFERENCE: Risk Management Cheat Sheet
## One-Page Guide for Daily Trading

---

## STOP LOSS PLACEMENT (Choose Wider of Two)

### ATR-Based Stops
```
Stop = Entry - (ATR × Multiplier)

Multipliers:
  Tight (1.5-2.0x):    Strong trend, tight setup, high conviction
  Standard (2.0-2.5x): Normal volatility, standard setup
  Wide (2.5-3.0x):     Higher volatility, wider setup
  Very Wide (3.0-4.0x): Extreme volatility (reduce size!)
```

### Technical Stops
```
Setup Low:      Base/range/handle low - $0.50
21 EMA:         21 EMA - 1% of price
50 SMA:         50 SMA - 2% of price  
Swing Low:      Prior low - $0.25-0.50
```

**Rule**: Use WIDER of ATR or Technical stop

---

## POSITION SIZING (3-Step Process)

### Step 1: Base Size by Environment
```
Environment A:  10% base, 20% max, risk 0.5%/trade
Environment B:  8% base, 15% max, risk 0.4%/trade
Environment C:  5% base, 10% max, risk 0.25%/trade
Environment D:  3% base, 5% max, risk 0.2%/trade
```

### Step 2: Edge Adjustment
```
3 edges:   -5% (reduce to 50%)
4 edges:   Base (no change)
5 edges:   +0.5%
6 edges:   +1.0%
7 edges:   +1.5%
8 edges:   +2.0%
9 edges:   +2.5%
10 edges:  +3.0%
```

### Step 3: Risk-Based Verification
```
Shares = (Account × Risk%) / (Entry - Stop)

Then use SMALLER of:
  - Position-based calculation
  - Risk-based calculation
```

---

## PORTFOLIO HEAT LIMITS

```
Individual Heat = (Position$ / Account$) × (Risk$ / Entry$)
Total Heat = Sum of all positions

Max Heat:
  Environment A: 2.5%
  Environment B: 2.0%
  Environment C: 1.0%
  Environment D: 1.5%
  
If exceeded: Don't add new trades OR reduce existing positions
```

---

## CIRCUIT BREAKERS (Mandatory Actions)

### Level 1: -5% Drawdown
```
[ ] Stop new trades 3 days
[ ] Tighten all stops 20-30%
[ ] Reduce sizing 25% next trades
[ ] Daily journal review
```

### Level 2: -10% Drawdown
```
[ ] STOP trading 1 week
[ ] Close 50% of positions
[ ] Paper trade only
[ ] Reduce sizing 50% when resume
```

### Level 3: -15% Drawdown
```
[ ] Close ALL positions immediately
[ ] 100% cash
[ ] STOP live trading 1 month minimum
[ ] Full system audit
[ ] External review
```

### Additional Stops
```
3 losses in a row → Stop 2 days
5 of 10 losses → Stop 1 week
2% loss in 1 day → Stop rest of day
```

---

## TRAILING STOPS (Once Profitable)

```
+5% gain:   Consider breakeven stop
+10% gain:  Breakeven minimum, consider 25-33% trim
+20% gain:  Trim 25-33%, lock 10%+ profit on rest
+30% gain:  Final trim or exit, trail within 3-5%

Methods:
  21 EMA Trail:  Stop just below daily 21 EMA
  ATR Trail:     Stop = Price - (ATR × 2.5-3.5x)
  Breakeven+:    Stop at entry, then +5%, then +10%
```

---

## TRADE EXECUTION CHECKLIST (Every Trade)

```
BEFORE ENTRY:
[ ] Setup grade A/B (not C/F)
[ ] Edges ≥3 (count all 10)
[ ] Entry price: $_____
[ ] Stop price: $_____ (5-15% below entry)
[ ] Risk per share: $_____
[ ] Position size calculated: _____ shares
[ ] Portfolio heat checked: ___% (under limit)
[ ] Dollar risk: $_____ (≤0.5% account)

AFTER ENTRY:
[ ] Stop order placed in broker
[ ] Position logged in journal
[ ] Initial stop: $_____
[ ] Review daily for stop adjustments
```

---

## WEEKLY RISK REVIEW (Every Sunday)

```
1. Drawdown: (Peak - Current) / Peak = ___%
   [ ] <5% normal [ ] 5-10% alert [ ] 10-15% stop [ ] >15% reset

2. Portfolio Heat: ___% (vs max ___%})
   [ ] Under limit ✓ [ ] Over limit - take action ✗

3. Win Rate (last 10): ___% 
   [ ] ≥50% ✓ [ ] <50% review [ ] <40% stop

4. Consecutive losses: ___ 
   [ ] 0-2 OK [ ] 3 stop 2 days [ ] 5+ stop 1 week

5. Actions this week:
   [ ] Continue normal
   [ ] Reduce sizing ___%
   [ ] Tighten stops
   [ ] Stop trading ___ days
   [ ] Paper trade only
```

---

## POSITION SIZING EXAMPLES (Quick Calculate)

### Tight Stop Example
```
Account: $50,000
Environment: A (risk 0.5%)
Entry: $350, Stop: $345.50
Risk: $4.50/share (1.3%)

Risk-based: ($50k × 0.5%) / $4.50 = 55 shares
Position value: 55 × $350 = $19,250 (38.5%)
TOO BIG! Use max 20% = $10k / $350 = 28 shares ✓
Dollar risk: 28 × $4.50 = $126 (0.25%) ✓
```

### Wide Stop Example
```
Account: $50,000
Environment: C (risk 0.25%)
Entry: $1000, Stop: $920
Risk: $80/share (8%)

Risk-based: ($50k × 0.25%) / $80 = 1.56 → 1 share
Position value: 1 × $1000 = $1000 (2%) ✓
Dollar risk: 1 × $80 = $80 (0.16%) ✓
```

---

## SCALING IN STRATEGY (Advanced)

```
Instead of full size immediately:

Initial: 25-33% of planned position
  → Test the waters, minimal risk

Add 33% at +5% gain:
  → Stock working, add more
  → Move stop to breakeven on initial

Add final 33% at +10% gain:
  → Full position deployed
  → Stop locks small profit on all
  
Use when: Env B/C, setup grade B, 4-5 edges
Skip when: Env A, setup grade A, 7+ edges
```

---

## GOLDEN RULES (Never Break)

```
1. Every trade has stop placed BEFORE entry
2. Never risk >0.5% per trade (Env A)
3. Portfolio heat never exceeds limits
4. 3 losses = stop 2 days (no exceptions)
5. -10% drawdown = stop 1 week (mandatory)
6. Never move stops against you (wider)
7. Always use smaller of position/risk calc
8. When in doubt, trade SMALLER
9. Protect capital FIRST, profits second
10. Rules protect you from yourself
```

---

## CALCULATION FORMULAS (Copy to Spreadsheet)

### ATR Stop
```
= Entry - (ATR × Multiplier)
```

### Risk Per Share
```
= Entry - Stop
```

### Risk-Based Position Size
```
= (Account × RiskPercent) / (Entry - Stop)
```

### Position Value
```
= Shares × Entry
```

### Individual Heat
```
= (Position$ / Account$) × ((Entry - Stop) / Entry)
```

### Portfolio Heat
```
= SUM(All Individual Heats)
```

### Drawdown
```
= (Peak - Current) / Peak × 100
```

---

## STOP LOSS ADJUSTMENT DECISION TREE

```
Is stock profitable?
  NO → Keep initial stop (or tighten if weak)
  YES → Continue below
  
Is gain >5%?
  NO → Keep initial stop
  YES → Move to breakeven OR keep initial if very strong
  
Is gain >10%?
  NO → Keep current stop
  YES → Lock profit: Stop at +5% minimum, consider trim
  
Is gain >20%?
  NO → Trail with 21 EMA or ATR 3x
  YES → Trail tightly (3-5% below price), consider trim
  
Is gain >30%?
  YES → Trail very tightly (21 EMA daily), consider exit
```

---

## ENVIRONMENT-BASED QUICK SETTINGS

| Parameter | Env A | Env B | Env C | Env D |
|-----------|-------|-------|-------|-------|
| Base Position | 10% | 8% | 5% | 3% |
| Max Position | 20% | 15% | 10% | 5% |
| Risk/Trade | 0.5% | 0.4% | 0.25% | 0.2% |
| Portfolio Heat | 2.5% | 2.0% | 1.0% | 1.5% |
| ATR Mult | 2.0x | 2.5x | 2.5-3x | 3.0x |
| Max Positions | 5-8 | 5-8 | 3-5 | 0-3 |

---

## YOUR PERSONAL LIMITS (Fill In)

```
Account Size: $__________
Peak Value: $__________ (update monthly)

Environment: ___ (A/B/C/D)
Base Position: ___% = $__________
Max Position: ___% = $__________
Risk Per Trade: ___% = $__________
Max Portfolio Heat: ___% = $__________

Current Positions: ___
Current Portfolio Heat: ___%
Heat Capacity: ___% remaining

Today's Status:
[ ] Can add new positions
[ ] At heat limit - no new trades
[ ] Over limit - reduce positions
[ ] Circuit breaker active - no trading

Next Review: ___________ (Sunday)
```

---

**Print this sheet and keep it at your trading desk. Reference it BEFORE EVERY trade.**

