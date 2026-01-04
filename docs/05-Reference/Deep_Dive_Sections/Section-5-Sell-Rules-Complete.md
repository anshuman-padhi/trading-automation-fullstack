# Section 5: Sell Rules & Position Management - COMPLETE GUIDE
## Exactly When to Take Profits, Exit Losers, and Maximize Gains

---

## OVERVIEW

This section defines the **exact exit rules** for every trade scenario:
1. ✅ **Profit-Taking Framework** - When and how to lock in gains (not "when it feels right")
2. ✅ **Weakness Exit Signals** - When to exit early if setup breaks
3. ✅ **Partial Profit Trimming** - Scale out at specific levels to lock profits while staying in
4. ✅ **Trailing Stop Management** - Trail stops to maximize wins while protecting gains
5. ✅ **Time-Based Exits** - When to cut losses based on time elapsed with no progress
6. ✅ **Earnings Management** - Special rules for positions around earnings announcements
7. ✅ **Position Management Rules** - When to hold, when to add, when to reduce

**Philosophy**: Most traders' problem isn't getting IN the trade—it's knowing when to GET OUT. You need rules for:
- ❌ Never letting a winner turn into a loser (most common mistake)
- ❌ Cutting losers quickly before -15% becomes -30%
- ❌ Taking profits too early (missing 50% runners)
- ❌ Holding too long looking for perfection (gives back everything)

**You'll know exactly where to exit BEFORE you enter, preventing emotional decisions in real time.**

---

---

# PART 1: THE PROFIT-TAKING FRAMEWORK

## PRINCIPLE: LOCK PROFITS IN 3 STAGES

**You'll never hold a full position hoping for perfection. Instead:**

```
Stage 1: Lock First Profits (+10% gain)
  → Take 33% off the table
  → Move stop to breakeven on remaining
  → "Profits are no longer at risk"

Stage 2: Secure Core Position (+20% gain)
  → Take another 33% off the table
  → Lock in 10%+ profit on remainder
  → "Building a winning position"

Stage 3: Let Final 33% Run
  → Trail aggressively with 21 EMA or ATR
  → Let it run until trend breaks
  → "Capturing the big move"
```

**Why This Works**[316][320][317]:
- ✅ Guarantees you take SOME profits (not all-or-nothing)
- ✅ Removes pressure from final "runner" position
- ✅ Locks in gains while still participating in big moves
- ✅ Prevents giving back 50% gains waiting for 100%
- ✅ Matches professional trader behavior (Minervini, Investor's Business Daily)

---

## RULE 1: STAGE 1 - FIRST PROFIT TAKE AT +10%

### Trigger
```
Stock hits +10% gain from entry
At ANY point (same day or weeks later)
```

### Action
```
SELL: 33% of position (1/3)
  Shares sold: ___
  Price: (entry + 10% of entry)
  
STOP ADJUSTMENT:
  Old stop: Entry - $___
  New stop: Entry Price (breakeven)
  
REMAINING POSITION: 67% still held
  Profit locked: 33% × 10% = 3.3% of position ✓
  Capital secured: Ready for new trades
  Risk: Now zero (stop is at breakeven on this position)
```

### Example

```
Entry: CRWD at $350.00
Initial position size: 15 shares = $5,250
Initial stop: $345.50

Stock rises to $385.00 (+10%):
  
STAGE 1 EXECUTION:
  Sell 1/3 of position: 15 × 0.33 = 5 shares
  Shares sold: 5 at $385 = $1,925 profit
  Move stop on remaining: From $345.50 to $350.00 (breakeven)
  
REMAINING POSITION:
  Shares held: 10 (at $350 original entry)
  Stop: $350.00 (breakeven)
  Risk on these 10 shares: ZERO
  
PSYCHOLOGY: "I've taken profits, no longer at risk, can sleep well"
```

### When NOT to Take Stage 1 (Hold Initial Position)

**Conditions to skip profit-taking at +10%**:
```
[ ] Stock hit +10% on same entry day (first day)
    AND entry was on heavy volume with huge momentum gap
    AND environment is strong (A)
    
REASON: Sometimes first day explosions continue (20-50% runners)
Take normal Stage 1 next day instead

[ ] All other cases: Take Stage 1 immediately at +10%
```

---

## RULE 2: STAGE 2 - CORE POSITION LOCK AT +20%

### Trigger
```
Stock hits +20% gain from entry (from remaining position)
```

### Action
```
SELL: Another 33% of original position (1/3)
  
REMAINING FROM STAGE 1: 67% (10 shares in example)
  Sell another 33% of ORIGINAL: 5 shares
  
REMAINING POSITION: 33% (5 shares in example)
  
STOP ADJUSTMENT:
  Move stop to: Original Entry + 10% (secure at least 10% on final portion)
  Example: $350 + $35 = $385
  
PSYCHOLOGY: "I now have 20% locked in, core 33% has 10% profit protected"
```

### Example Continued

```
Stock now at $420.00 (+20% from $350 entry):

STAGE 2 EXECUTION:
  From remaining 10 shares, sell 1/3: ~3 shares at $420
  Shares sold: 3 at $420 = $1,260 (profit on these 3)
  Move stop on final 7 shares: From breakeven $350 to $385
  
POSITION ACCOUNTING:
  Already cashed out Stage 1: 5 shares × $385 = $1,925 profit
  Just cashed out Stage 2: 3 shares × $420 = $1,260 profit
  Still holding Stage 3: 7 shares at $420 (up from $350 entry)
  
Total profit locked: $1,925 + $1,260 = $3,185 (60% of original)
  Remaining position: 7 shares, stop $385 (locks $35/share × 7 = $245 more)
  Maximum risk: Zero (all remaining is profit)
  
PSYCHOLOGY: "I've captured 60% of available gains, final 7 shares is "free money""
```

---

## RULE 3: STAGE 3 - LET RUNNER RUN WITH TRAILING STOP

### Trigger
```
After Stage 2 is taken at +20%
Final 33% position remains
Stop is locked at +10% minimum profit
```

### Trailing Stop Methods (Choose One)

**Option A: 21 EMA Trailing Stop** (Conservative)
```
Adjust daily:
  New stop = 21 EMA (daily) - (1% of current price)
  
As stock continues up:
  Stop follows, always just below 21 EMA
  
Exit trigger:
  Close below 21 EMA on volume
  Automatic exit at stop
  
Example: Stock at $500, 21 EMA at $480
  Stop = $480 - ($500 × 0.01) = $480 - $5 = $475
  
Next day: Stock at $530, 21 EMA at $505
  Stop = $505 - ($530 × 0.01) = $505 - $5.30 = $499.70
  Stop trails up, locking more profit
```

**Option B: ATR Trailing Stop** (Dynamic)
```
Adjust daily using ATR(14):
  New stop = Current Price - (ATR × 2.5x to 3.0x)
  
As volatility changes:
  Stop adjusts for current conditions (not fixed distance)
  
Example: Stock at $500, ATR = $8
  Stop = $500 - ($8 × 2.75) = $500 - $22 = $478
  
Stock continues to $550, new ATR = $10:
  Stop = $550 - ($10 × 2.75) = $550 - $27.50 = $522.50
  Stop trails, gets wider to match increased volatility
```

**Option C: Breakeven + Profit Trail** (Simple, Professional)
```
As stock makes higher highs:
  
+0-10% gain: Stop at breakeven (initial)
+10-20%: Stop at entry + 5% (+ $17.50 from entry $350)
+20-30%: Stop at entry + 10% (locks $35)
+30-40%: Stop at entry + 15% (locks $52.50)
+40-50%: Stop at entry + 20% (locks $70)
+50%+: Stop at entry + 30% (locks $105)

Example: Position up +35%
  Entry: $350
  Current: $472.50
  Stop: $350 + ($350 × 0.15) = $350 + $52.50 = $402.50
  
Profit locked if stops: $472.50 - $402.50 = $70 per share ✓
```

**Which to Use?**
```
21 EMA Trail:   Strongest trends, let it maximize (best for momentum)
ATR Trail:      Adapts to volatility changes (best for choppy moves)
Fixed Profit:   Simple to execute, mechanical (best for discipline)

RECOMMENDATION: Use Fixed Profit Trailing for simplicity
  Adjust % locked every $10-20 gain
  Exit if stock closes below your stop
```

### Example: CRWD Stage 3 - Let Runner Run

```
After Stage 2, remaining position: 7 shares at $420
Stop: Locked at $385 (minimum +10% = $35/share)

Day 1: Stock closes at $420
  Stop remains: $385
  Trailing stop decision: No change, stock flat

Day 2: Stock jumps to $455 (+10% from $420)
  Adjust trailing stop: $455 - (5% of $455) = $455 - $22.75 = $432.25
  New stop locked in: $432.25

Day 3: Stock pulls back to $440 (below yesterday high)
  Check trailing stop: $440 > $432.25 (not hit, stay in)
  Adjust stop higher: $440 - $22 = $418

Day 5: Stock runs to $490 (+15% from $420)
  Adjust trailing: $490 - (3% of $490) = $490 - $14.70 = $475.30
  New stop: $475.30

Day 10: Stock pulls back to $470
  Check: $470 > $475.30? NO, hit stop! ✗
  Exit trigger: Sell 7 shares at $470
  Profit: 7 × ($470 - $350) = 7 × $120 = $840

TOTAL POSITION PROFIT:
  Stage 1: 5 shares × $35 gain = $175
  Stage 2: 3 shares × $70 gain = $210
  Stage 3: 7 shares × $120 gain = $840
  TOTAL: $1,225 profit on $5,250 position (23.3% gain)

Risk: $0 (all cashed out with profits)
Final exit: Natural trend break (21 EMA or ATR signal)
```

---

## RULE 4: WHAT IF STOCK NEVER HITS +20%?

### Scenario A: Stock at +15%, Trend Looks Weak

```
Stock: Up only 15% after 10+ days
Market environment weakening
RS line starting to roll over

Decision: Take what you have
  Exit position entirely
  Don't wait for +20% target
  Better to be out than destroyed
  
Reason: Trend may be failing, better to lock +15% than watch it turn negative
```

### Scenario B: Stock at +5%, Stock is Rolling Over

```
Entry: MSFT at $420
Current: $441 (+5%)
But: 
  - Closed below 21 EMA on volume
  - RS line rolling over
  - Environment weakened from A to B

Decision: Exit now, take +5%
  No need to wait for +10% target
  Trend may be reversing
  Protect your capital
  
Reason: Sell weakness, don't wait for perfection
```

---

---

# PART 2: WEAKNESS EXIT SIGNALS (When to Exit Early)

## THE RULE: "SELL WEAKNESS, BUY STRENGTH"[320][321][323][326][329]

**Never hold "hoping it comes back" if these warning signals appear:**

---

## WEAKNESS SIGNAL #1: BREAK BELOW 21 EMA (Immediate Exit)

### Definition
```
Price closes BELOW the 21 EMA on increasing volume
```

### Why It Matters
```
21 EMA = Short-term trend direction
Price above it = Momentum is positive
Price below it = Momentum has reversed
```

### Action
```
[ ] Stock closes below 21 EMA on daily chart
[ ] Volume is above 20-day average
[ ] IMMEDIATE DECISION: Exit position

DO NOT wait for stop loss hit
DO NOT wait for "one more day"
Exit the moment this signal occurs

Reason: This is the most reliable sell signal for momentum stocks
Market structure has shifted against you
```

### Example

```
Entry: NVDA at $500
21 EMA: Has been $495-505 range (around entry)
Position up +10%, at $550

Red Flag Day:
  Open: $548
  High: $550
  Low: $540 ← Closes HERE on $250M volume (4x avg)
  Close: $542 (below 21 EMA at $545)
  
SIGNAL: Close below 21 EMA + volume ✓✓

Immediate Action:
  Sell entire remaining position at market open next day
  Don't wait for "better price"
  Expected fill: Around $540-545 (slight gap, but guaranteed exit)
  
Outcome: Exit at $540, original entry $500 = +8% gain
  Could have been +10-20% if held, but protected against further downside
  Better to get 8% than hold 10 days and turn it into -5%
```

---

## WEAKNESS SIGNAL #2: BREAK BELOW 50 SMA (Early Warning)

### Definition
```
Price closes BELOW 50 SMA 
This is second line of defense
```

### Why It Matters
```
50 SMA = Intermediate trend
If broken, larger trend may be reversing
```

### Action
```
[ ] Stock closes below 50 SMA
[ ] If also below 21 EMA: EXIT immediately (21 EMA already triggered)
[ ] If above 21 EMA but below 50 SMA:
    [ ] Tighten stop to breakeven or just above 21 EMA
    [ ] Watch for next day: Will it close above 50 SMA again?
    
If close above 50 SMA next day:
  → Stays in trend, can hold
  
If closes below 50 SMA again:
  → Trend is breaking, exit on third day
  → Don't wait for Stage target profits
```

---

## WEAKNESS SIGNAL #3: LOWER HIGH (Failed Breakout)

### Definition
```
Stock makes a lower high than prior high
While in a supposed uptrend
```

### Visual Pattern
```
Prior High: $550
Pullback: $520
Bounce High: $545 (new high is LOWER than $550) ← LH
```

### Why It Matters
```
Stock failing to make higher highs = Loss of momentum
Suggests buyers are getting weaker
Potential trend reversal coming
```

### Action
```
[ ] Stock makes lower high
[ ] Check if this is combined with:
    [ ] Lower low (pattern deteriorating) - SELL immediately
    [ ] Volume declining on the "bounce" - TIGHTEN STOP
    [ ] RS line rolling over - SELL immediately
    
If ONLY lower high:
  → Tighten stop to just above prior high
  → Watch for next day's action
  → If makes higher high, trend intact
  → If makes lower high again, EXIT
```

### Example

```
Stock in uptrend, entry at $350:

Pattern:
  High #1: $420 (you're up +20%)
  Pullback: $400
  High #2: $415 (lower than High #1)
  
Lower High detected at $415

Decision:
  This stock is struggling to make higher highs
  Momentum is fading
  Tighten stop to: $410 (just below pullback low)
  
Next Day: If stock closes below $410 → EXIT
Next Day: If stock closes above $420 (makes new high) → Stay in, trend intact
```

---

## WEAKNESS SIGNAL #4: FAILED BREAKDOWN (False Signal)

### Definition
```
Stock breaks below support clearly
Then reverses back above same day
But reverses on weak volume/no follow-through
```

### Example

```
Support at $345 (original stop location)
Stock breaks below to $340 (gap down)
Then reverses to $350 by close

Problems:
  - Broke support (failure)
  - Recovered same day (looks positive)
  - But on lower volume than the initial break (weak reversal)
  - Shows indecision/weakness
  
Decision:
  Even though back above support
  The ability to break it shows weakness
  Tighten stop to just above $345 (support that was broken)
  Watch for next break - if it happens again, EXIT
```

---

## WEAKNESS SIGNAL #5: VOLUME DRYING UP (Supply Removed)

### Definition
```
Stock is rising, but on DECLINING volume
Volume much lighter than breakout or prior days
```

### Why It Matters
```
Volume = Conviction of buyers
Rising on light volume = Buyers are leaving
Lack of demand = Pullback likely
```

### Action
```
[ ] Stock up 15%+ from entry
[ ] Last 3-5 days: Volume declining (not higher)
[ ] Price not making new highs on the light volume

Decision:
  Take profits
  Trend is losing power
  Risk/reward now shifted against you
  
Action: Take Stage 2 profits (at +20% target or 85% of it)
```

---

## WEAKNESS SIGNAL #6: EARNINGS APPROACHING (Watch)

### Definition
```
Company has earnings announcement within 2 weeks
```

### Why It Matters
```
Pre-earnings volatility increases
Post-earnings gaps (up or down) kill positions
You don't want to hold through earnings surprise
```

### Action
```
WITHIN 1 WEEK OF EARNINGS:
  [ ] Exit 50% of position (lock profits before event)
  [ ] Keep 50% if very strong (and willing to take bigger swings)
  
2-3 DAYS BEFORE EARNINGS:
  [ ] Exit remaining position
  [ ] Don't let 20% profit turn into -10% gap down
  
Reason: Risk/reward deteriorates going into earnings
Better to be in cash than take binary event risk
```

---

---

# PART 3: TIME-BASED EXIT RULES (When Time = Stop Loss)

## "DEAD TIME STOP" CONCEPT

**If stock doesn't move within X days, exit (capital no longer working)**

---

## RULE 5: 10-DAY NO PROGRESS EXIT

### Trigger
```
Stock has been flat (within 5% of entry) for 10+ trading days
No progress made toward +10% target
```

### Example

```
Entry: CRWD at $350
Stop: $345.50

Days 1-10: Stock bounces between $348-355 (choppy, no progress)
No new highs made
No breakdown below entry
Volume declining as traders lose interest

Decision:
  Day 10: If still flat (not > +5%), EXIT
  Capital is not working
  Better to redeploy elsewhere
  
Reason: Time value. 10 days wasted = opportunity cost
        Other trades could have been +15% by now
        Cut it loose, find better setups
```

---

## RULE 6: 20-DAY NO NEW HIGH EXIT

### Trigger
```
Stock has not made a new high from entry price in 20+ days
```

### Action
```
By Day 20:
  [ ] If price is still below original entry + 10% = EXIT
  [ ] Stock has shown no power to break through resistance
  [ ] Cut it and move on

Example: Entry $350
  Target high: $385 (entry + 10%)
  Day 20: Price still at $365 (hasn't made $385 yet)
  Decision: EXIT at market, take $15 profit ($365 - $350)
  
Reason: Pattern has failed. Real breakouts happen within 10-15 days.
        If it can't break in 20 days, it probably won't.
```

---

## RULE 7: 30-DAY EXIT FOR SWING TRADES

### Trigger
```
Swing trade held for 30+ days
(Swing trades defined as 5-20 day intended hold)
```

### Action
```
By Day 30:
  [ ] Exit position regardless of profit/loss
  [ ] This has become a "position trade" or failed swing
  [ ] Cut and move on to active swing opportunities

Why:
  - 30 days in one position = huge opportunity cost
  - Capital locked up for a month = inefficient
  - Other opportunities missed while watching this one
  - Psychology: Attachment to the position increases
  
Use 30-day rule to force discipline
```

---

---

# PART 4: EARNINGS MANAGEMENT (Special Rules)

## THE PROBLEM: EARNINGS = 10-20% OVERNIGHT MOVES

**Most positions shouldn't be held through earnings.**

---

## RULE 8: PRE-EARNINGS POSITION MANAGEMENT

### 2-3 Weeks Before Earnings

```
[ ] Identify earnings date (check SEC, investor relations)
[ ] Note date on calendar
[ ] Continue normal trading with full position
[ ] No action needed yet
```

### 1 Week Before Earnings

```
[ ] If position is in gains (+5% or more):
    [ ] Sell 50% of remaining position
    [ ] Lock some profits before event
    [ ] Keep 50% if you want to play the "earnings surprise"
    
[ ] If position is near breakeven or slightly negative:
    [ ] Exit entire position 3-5 days before earnings
    [ ] Don't want to hold through potential gap down
    [ ] Move capital elsewhere
```

### 2-3 Days Before Earnings

```
[ ] If still holding 50% for earnings play:
    [ ] Check Implied Move % (what market expects)
    [ ] If implied move >8%:
        [ ] Consider exiting (risk/reward unfavorable)
    [ ] If implied move 3-5%:
        [ ] Can hold 50% position
        
Example: Stock at $350, implied move $15 (4.3%)
  Expected range: $335-365
  If stock was at $350 on entry
  Worst case: Down to $335 = -2.1% loss
  Best case: Up to $365 = +4.3% gain
  Risk/Reward: 4.3:2.1 = 2:1 favorable
  Can hold
  
Example: Stock at $350, implied move $25 (7.1%)
  Expected range: $325-375
  Worst case: $325 = -7.1%
  Best case: $375 = +7.1%
  Risk/Reward: 7.1:7.1 = 1:1 (unfavorable, too risky)
  EXIT before earnings
```

### Day Before / Day Of Earnings

```
DECISION TREE:

If you DID NOT hold through earnings:
  ✓ You're done, position closed 3-5 days ago
  ✓ Profits locked in, capital free for next trade

If you ARE holding 50% for earnings surprise:
  
  Option A: Exit before market open
    - Guarantees your price
    - No gap risk
    - Recommended if nervous
    
  Option B: Hold through earnings, but set stop
    - Pre-set a stop at -4 to -5% from entry
    - If earnings gap down, auto-sell
    - Can participate if gaps UP
    
  Option C: Set alert, watch
    - Monitor live at 4:15 PM (assume 4 PM ET earnings)
    - If down 5%+, sell immediately
    - If up 5%+, trail your stop
```

---

## RULE 9: POST-EARNINGS MANAGEMENT

### Immediate Post-Earnings (Next Day)

```
Stock gaps up or down 5-20%

IF GAP UP (+5%+):
  [ ] This is a new setup (different entry)
  [ ] Don't automatically hold for Stage targets
  [ ] If you only held 50%, decide:
      [ ] Close remaining 50% to lock all-in profits
      [ ] Or hold if gap was on massive volume (real strength)

IF GAP DOWN (-5%+):
  [ ] Position likely stopped out (good, capital protected)
  [ ] If somehow still holding:
      [ ] Exit immediately at market open
      [ ] Take the loss, don't hope for recovery
      [ ] Earnings disappointment = stock likely continues down
```

### Days 2-7 Post-Earnings

```
Stock has gapped, but now consolidating

IF GAPPED UP AND CONSOLIDATING:
  [ ] Position is actually more solid
  [ ] Stock proved strength (gapped higher)
  [ ] Can let it continue with trailing stops
  [ ] Use same Stage 1, 2, 3 profit-taking rules

IF GAPPED DOWN AND CONSOLIDATING:
  [ ] Position should already be closed
  [ ] If somehow still in: Confirm down trend with 21 EMA break
  [ ] Exit on any further weakness
```

---

---

# PART 5: POSITION MANAGEMENT RULES

## RULE 10: NEVER ADD TO LOSING POSITION[320][323]

### Definition
```
You never buy more shares if current position is losing money
```

### Example - WRONG (Don't Do This)

```
Entry 1: NVDA at $500, bought 10 shares
Stock drops to $480 (-4%)

Wrong decision: "It's cheaper now, buy 10 more!"
New position: 20 shares at avg $490

Problem:
  - Increased risk
  - More capital at risk
  - Psychological pressure increases
  - Typical retail trader mistake
  - This is how accounts blow up
```

### Example - RIGHT (Do This)

```
Entry 1: NVDA at $500, bought 10 shares
Stock at $550 (+10%)
Taking Stage 1 profits: Sell 3 shares, lock $150 profit

Stock at $560, looking strong
Right decision: "Position is already +12%, stay in" (don't add)

Or: "Can I add? No. Only add to WINNING positions" (no add)
```

---

## RULE 11: ONLY SCALE UP WHEN WINNING[320][323]

### When to Add to Position

```
Current position is +20%+ in profit
Stock just made breakout through resistance
Volume expanding
All technical indicators aligned

ONLY THEN: Consider adding 25-50% more shares

Example:
  Original 10 shares bought at $350
  Stock now at $420 (+20%)
  Breaks through resistance on volume
  
Add: 5 shares at $420 (add 50% to existing position)
New position: 15 shares (10 original + 5 new)
Avg price: (10×$350 + 5×$420) / 15 = $373.33

Benefit:
  - You're adding ONLY after proof of success
  - You're adding at higher price, but with more confidence
  - Worst case: You have 10 shares at breakeven
  - Best case: All 15 shares continue running
```

---

## RULE 12: NEVER HOLD THROUGH "STUPID RISK" EVENTS

### Examples of Stupid Risk

```
1. FOMC Announcement (Federal Reserve Decision)
   - Exit 50% of position 1 hour before
   - 2-4% gap moves common
   - Not worth risk

2. Earnings (covered in Rule 8)
   - Exit before event risk
   - Play technicals, not events

3. Economic Reports (Unemployment, Inflation, etc.)
   - Exit major positions before big economic reports
   - Market-wide gaps common
   - Personal trading positions shouldn't be at risk

4. Options Expiration Week
   - Stock behavior can be manipulated by large options positions
   - Exit if you want clean price action
   - Re-enter next week

5. Gap Down Opening (>-3% from prior close)
   - Consider exiting if position is small loss
   - Don't hold hoping for recovery on gap down
```

---

## RULE 13: TIGHTEN STOPS ON WINNERS (Lock Profits)

### The Principle

```
As position becomes more profitable, stop should move UP
Stop = Your profit protection, not your loss protection
```

### Progressive Tightening (from Section 4)

```
+0-10%:     Stop at original entry
+10-20%:    Stop at entry + 3-5% profit
+20-30%:    Stop at entry + 10% profit
+30-50%:    Stop at entry + 15-20% profit
+50%+:      Stop at entry + 30% profit (or use 21 EMA trail)
```

### Example

```
Entry: $350
Current: $420 (+20%)

Stop adjustment:
  Old stop: $345.50 (original risk)
  New stop: $350 + (350 × 0.10) = $350 + $35 = $385
  
Locked profit: If stopped at $385, you make $35/share
  = $35 / $350 = 10% minimum profit
  
BUT position is currently at $420
  = $70 profit per share
  
If stock drops from $420 to $385, you only give back $35
  Locked 50% of profit gained
```

---

---

# PART 6: THE COMPLETE SELL DECISION TREE

## FLOWCHART: WHAT TO DO AT EACH STAGE

```
POSITION ENTERED AT PRICE: $_____
CURRENT PRICE: $_____
DAYS HELD: _____
PROFIT/LOSS: ___%

                           │
                 Is price -5% or worse?
                      /        \
                    YES        NO
                    │          │
            STOP LOSS        Continue
            HIT          Review daily
            EXIT
                           │
              Did ANY weakness signal occur?
              (21 EMA break, 50 SMA break, lower high,
               volume drying up, failed bounce)
                      /        \
                    YES        NO
                    │          │
                   EXIT     Continue
              Immediately   (let trailing stop
              (protect       manage it)
              capital)
              
                           │
              Is price +10% or more?
                      /        \
                    YES        NO
                    │          │
              STAGE 1:     Continue
              Take 1/3     Hold
              Sell 33%
              Move stop
              to breakeven
              
                           │
              Is price +20% or more?
                      /        \
                    YES        NO
                    │          │
              STAGE 2:     Continue
              Take 1/3     Hold
              Sell another (wait for
              Sell 33%     20% target
              Lock profit
              
                           │
              Earnings within 2 weeks?
                      /        \
                    YES        NO
                    │          │
              1 week:    Continue
              Exit 50%   Trail final
              3 days:    33% with
              Exit all   Trailing Stop
                         (21 EMA or ATR)
                         
                           │
              Been flat for 20+ days?
                      /        \
                    YES        NO
                    │          │
                   EXIT      Continue
                (time out)     (or exit on
                           weakness signal)
```

---

## SELL RULES CHECKLIST (Print This)

```
═══════════════════════════════════════════════
POSITION: ____________  ENTRY: $_______
═══════════════════════════════════════════════

STAGE 1 (+10% Gain) - TAKE PROFITS NOW
[ ] Stock hit +10% gain
[ ] Sell 33% of position (1/3)
[ ] Move stop on remaining to breakeven
[ ] Remaining: 67% with zero risk

STAGE 2 (+20% Gain) - SECURE CORE POSITION
[ ] Stock hit +20% gain
[ ] Sell another 33% of original position (1/3)
[ ] Move stop to entry + 10% profit
[ ] Remaining: 33% with 10% profit protected

STAGE 3 (Runner Position) - TRAIL WITH STOP
[ ] Final 33% remaining
[ ] Use 21 EMA trailing stop OR ATR trailing stop
[ ] Adjust daily
[ ] Exit on stop hit or weakness signal

WEAKNESS SIGNALS - EXIT IMMEDIATELY
[ ] Close below 21 EMA on volume → EXIT
[ ] Break below support + lower high → TIGHTEN STOP
[ ] Lower high confirmed → TIGHTEN STOP
[ ] Volume drying up + no new highs → EXIT
[ ] Failed breakout (reversal) → TIGHTEN STOP

EARNINGS MANAGEMENT
[ ] Earnings within 2 weeks? → EXIT 50% (1 week before)
[ ] Earnings within 3 days? → EXIT ALL remaining
[ ] Post-earnings gap? → MANAGE accordingly

TIME-BASED EXITS
[ ] Been flat for 10 days? → EXIT (capital not working)
[ ] No new high in 20 days? → EXIT
[ ] In position 30+ days? → EXIT (swing trade done)

DECISION: ______________________
  [✓] SELL (which shares, which stage)
  [✓] HOLD (moving stop, trailing)
  [✓] REDUCE (tighten stop, wait)
═══════════════════════════════════════════════
```

---

---

# PART 7: EXIT EXAMPLES (Real Scenarios)

## EXAMPLE 1: CRWD - Perfect Exit (All Stages)

```
Entry: $350.00 (15 shares = $5,250)
Initial Stop: $345.50

DAY 1: Stock closes $352 (flat, hold)
DAY 3: Stock at $385 (+10%) 
  STAGE 1 TRIGGER: Sell 5 shares at $385
  Move stop to $350 (breakeven)
  Remaining: 10 shares
  
DAY 5: Stock at $420 (+20%)
  STAGE 2 TRIGGER: Sell 3 more shares at $420
  Move stop to $385 (entry + 10%)
  Remaining: 7 shares
  Profit locked: $1,925 + $1,260 = $3,185
  
DAY 7: Stock at $455 (+30%)
  STAGE 3: Trailing stop at $455 - (ATR × 2.5x)
  ATR = $8, so stop = $455 - $20 = $435
  
DAY 10: Stock at $480 (+37%)
  Adjust trailing: $480 - $20 = $460
  
DAY 12: Stock pulls back to $465
  Stop at $460, still holding
  
DAY 15: Stock breaks $460 (below stop)
  STAGE 3 EXIT: Sell 7 shares at $460
  Profit on final: $460 - $350 = $110/share × 7 = $770

TOTAL: $3,185 + $770 = $3,955 profit on $5,250 (75.2% total gain)
Exit: Clean, on trailing stop, 15 days held
Risk: Zero (all profits after Stage 1 breakeven)
```

---

## EXAMPLE 2: META - Early Exit (Weakness Signal)

```
Entry: $475 (12 shares = $5,700)
Initial Stop: $465

DAY 1-8: Stock at $500-510 (+5-7%)
DAY 8: Earnings announcement next week (Day 15)

DAY 8 DECISION:
  Stock at $510 (+7%)
  Earnings in 7 days
  Following Rule 8 (1 week before earnings)
  
ACTION: Exit 50% of position at $510
  Sell 6 shares at $510 = $3,060 (profit $210)
  Remaining: 6 shares with breakeven stop
  
DAY 10: Stock at $515 (+8%)
  RS line starts rolling
  Volume declining on the bump
  BUT: Staying for earnings play on final 50%

DAY 12: 3 days before earnings
  Check implied move: $12 (2.5%)
  Expected range: $463-487
  Stock at $515, could gap to $503-527
  Risk/reward neutral
  
DECISION: Exit remaining 50% before earnings
  Sell 6 shares at $515 = $3,090 (profit $240)
  
TOTAL RESULT: 
  Exited all at $510-515 avg
  Entry was $475
  Profit: $40-45 per share × 12 = $480-540 total
  +8.4% - +9.5% return
  Avoided earnings binary risk
  Held position 12 days
  
WHY THIS IS GOOD:
  - Took profits before event
  - Didn't hold through earnings surprise
  - Got reasonable gain
  - Capital now free for next trade
```

---

## EXAMPLE 3: NVDA - Hit Weakness Signal (21 EMA Break)

```
Entry: $500 (20 shares = $10,000)
Initial Stop: $485

DAY 1-12: Stock at $530-550 (+6-10%)
  Stage 1 trigger: Sold 6 shares at $550 (break even stop at $500)
  
DAY 15: Stock at $575 (+15%)
  Stage 2 trigger: Sold 6 shares at $575 (stop at $525, = entry +$25)
  Remaining: 8 shares
  Profit locked: $6,000 + $4,500 = $10,500
  
DAY 20: Stock at $590 (+18%)
  Still bullish, no weakness
  Trailing stop at $575 (using ATR 2.5x)
  
DAY 23: WEAKNESS SIGNAL - CLOSE BELOW 21 EMA
  Open: $588
  High: $590
  Low: $572
  Close: $575 (BELOW 21 EMA at $580) ← SELL SIGNAL
  Volume: 350M shares (4x normal)
  
IMMEDIATE ACTION (Rule 1):
  Market open next day: Exit remaining 8 shares
  Expected fill: $573-578 (slight gap)
  Actual sell: 8 shares at $575
  
FINAL OUTCOME:
  6 shares (Stage 1): $550 × 6 = $3,300
  6 shares (Stage 2): $575 × 6 = $3,450
  8 shares (Stage 3): $575 × 8 = $4,600
  Total collected: $11,350
  Original investment: $10,000
  PROFIT: $1,350 (+13.5%)
  Days held: 23 days
  Exit: On weakness signal (not perfect, but protected)
  
KEY: Didn't wait for +20-30% target
  Took +13.5% on weakness signal
  This is actually GOOD: protect capital first
```

---

---

# PART 8: YOUR COMPLETE EXIT SYSTEM

## WEEKLY REVIEW - CHECK ALL POSITIONS

**Every Sunday, review all open positions:**

```
POSITION REVIEW: (STOCK NAME)

1. PROFIT/LOSS CHECK:
   Entry: $_____
   Current: $_____
   Gain/Loss: ___% (___$)
   
2. STAGE CHECK:
   [ ] Below +10%: Holding for Stage 1
   [ ] +10-20%: Holding for Stage 2 (Stage 1 taken)
   [ ] +20%+: Running Stage 3 (Stages 1&2 taken)
   [ ] Negative: Holding stop, watching for exit
   
3. WEAKNESS CHECK:
   [ ] Price above 21 EMA? YES / NO
   [ ] Price above 50 SMA? YES / NO
   [ ] Higher highs being made? YES / NO
   [ ] Volume confirming move? YES / NO
   [ ] RS line trending up? YES / NO
   
   If NO to 2+: TIGHTEN STOP
   If NO to 3+: CONSIDER EXITING
   
4. TIME CHECK:
   Days held: _____
   [ ] <10 days: Normal, continue
   [ ] 10-20 days: Acceptable, but check progress
   [ ] 20-30 days: Getting long, should show 20%+ gain
   [ ] 30+ days: END POSITION if <20% gain
   
5. EARNINGS CHECK:
   Days to earnings: _____
   [ ] >3 weeks: Normal
   [ ] 2-3 weeks: Plan exit strategy
   [ ] 1 week: Exit 50% if profitable
   [ ] <3 days: Exit all remaining
   
6. ACTION DECISION:
   [ ] HOLD (everything normal)
   [ ] TAKE PROFITS (hit stage target)
   [ ] TIGHTEN STOP (weakness detected)
   [ ] EXIT (weakness confirmed or time out)
```

---

## YOUR RULES TO PRINT AND POST

```
═══════════════════════════════════════════════
          MY SELL RULES (NON-NEGOTIABLE)
═══════════════════════════════════════════════

PROFIT TAKING (3-Stage System):
1. Stage 1: At +10% gain, sell 1/3, move stop to breakeven
2. Stage 2: At +20% gain, sell another 1/3, lock profit
3. Stage 3: Trail final 1/3 with 21 EMA or ATR stop

WEAKNESS SIGNALS (Exit immediately):
4. Close below 21 EMA on volume → EXIT
5. Break below 50 SMA → TIGHTEN STOP
6. Make lower high after higher high → TIGHTEN STOP
7. Volume drying up on gains → EXIT
8. Failed bounce (gap recover on weak volume) → TIGHTEN STOP

EARNINGS MANAGEMENT:
9. 1 week before earnings → Exit 50%
10. 3 days before earnings → Exit all remaining

TIME-BASED EXITS:
11. Flat 10+ days → EXIT (capital not working)
12. No new high in 20 days → EXIT
13. In position 30+ days → EXIT

POSITION MANAGEMENT:
14. Never add to losing positions
15. Only scale up when already winning (+20%+)
16. Always tighten stops as profits grow

FORBIDDEN ACTS:
✗ Never hold through earnings events
✗ Never add to losing trades
✗ Never hope for recovery (it usually doesn't)
✗ Never ignore 21 EMA break signal
✗ Never let winner turn into loser

═══════════════════════════════════════════════

SIGNED: ___________________  DATE: __________

POST THIS AT YOUR TRADING DESK AND READ DAILY
═══════════════════════════════════════════════
```

---

## YOUR NEXT STEPS

**This Week**:
- [ ] Read Section 5 completely
- [ ] Understand the 3-stage profit-taking system
- [ ] Study all weakness signals
- [ ] Practice Stage 1-3 calculations (5 examples)

**Next Week**:
- [ ] Paper trade 5 positions with complete exits
- [ ] Take Stage 1, 2, 3 profits at exact levels
- [ ] Practice recognizing weakness signals
- [ ] Journal each exit and rationale

**Before Live Trading**:
- [ ] Paper trade 20+ positions with all stages
- [ ] Test trailing stop methods (21 EMA vs ATR vs Fixed)
- [ ] Practice earnings management (exit early on 3 positions)
- [ ] Perfect your exit discipline (never hold hoping)

---

**You now have an EXACT exit system with specific rules for every scenario. Most traders have no plan for exits - they "will decide when the time comes." You'll know exactly where to exit BEFORE you enter, removing emotion from the decision.**

**Next Section**: Section 6 (Post-Analysis & Journaling) - How to learn from every trade and continuously improve your system.

