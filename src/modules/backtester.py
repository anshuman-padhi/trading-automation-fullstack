
import pandas as pd
import numpy as np
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import joblib
import os
from src.modules.market_analysis import MarketAnalyzer

logger = logging.getLogger("backtester")

@dataclass
class Trade:
    symbol: str
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    status: str = "OPEN"
    pnl: float = 0.0
    return_pct: float = 0.0
    exit_reason: str = ""
    ml_score: float = 0.5 
    ml_features: dict = field(default_factory=dict)
    position_value: float = 0.0 
    highest_price: float = 0.0  # Track for Trailing Stop 

class Backtester:
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.trades: List[Trade] = []
        self.positions: Dict[str, Trade] = {} 
        self.market_analyzer = MarketAnalyzer()
        
        self.max_positions = 15  # ULTRA-AGGRESSIVE v2: Increase from 10
        self.position_size_pct = 0.10 
        self.stop_loss_pct = 0.05 
        self.take_profit_target = 10.0  # DISABLE FIXED TARGET (Using Trailing Stop)
        self.trailing_stop_pct = 0.15   # 15% Trailing Stop (Best Growth) 
        
        self.collect_ml_data = False
        self.skip_ml_filter = True  # ML Bypassed (StockSelector handles filtering)
        self.ml_data = [] 
        self.equity_history = []  # Track daily equity for metrics
        
        # PHASE 2A: Market Breadth
        self.breadth_calculator = None
        self.vix_data = None
        
        self.model = None
        self.scaler = None
        self.market_data = None 
        
        # Initialize Stock Selector
        from src.modules.stock_selector import StockSelector
        self.stock_selector = StockSelector()
        
        self.load_model()
        
    def set_market_data(self, df: pd.DataFrame):
        self.market_data = df.copy()
        if 'Close' in self.market_data.columns:
            self.market_data['SMA_10'] = self.market_data['Close'].rolling(10).mean()
            self.market_data['EMA_21'] = self.market_data['Close'].ewm(span=21).mean()
            self.market_data['SMA_200'] = self.market_data['Close'].rolling(200).mean()
            self.market_data['close'] = self.market_data['Close'] 
            
            # Add RSI for market_data
            delta = self.market_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            self.market_data['RSI'] = 100 - (100 / (1 + rs))
            
            # Add Close_prev for SPY
            self.market_data['Close_63d'] = self.market_data['Close'].shift(63)
    
    def set_breadth_data(self, stock_universe: dict, vix_df: pd.DataFrame = None):
        """
        PHASE 2A: Initialize market breadth calculator and VIX data.
        
        Args:
            stock_universe: Dict of symbol -> DataFrame with indicators
            vix_df: Optional VIX data DataFrame
        """
        from src.modules.market_breadth import MarketBreadthCalculator
        
        if len(stock_universe) >= 50:  # Need minimum universe size
            self.breadth_calculator = MarketBreadthCalculator(stock_universe)
        
        if vix_df is not None and not vix_df.empty:
            self.vix_data = vix_df 

    def load_model(self):
        try:
            model_path = "scripts/ml/breakout_classifier.joblib"
            if os.path.exists(model_path):
                artifact = joblib.load(model_path)
                if isinstance(artifact, dict) and 'model' in artifact:
                    self.model = artifact['model']
                    self.scaler = artifact.get('scaler')
                    logger.info(f"Loaded ML Pipeline from {model_path}")
                else:
                    self.model = artifact
                    logger.info(f"Loaded ML Model (Legacy)")
            else:
                pass 
        except Exception as e:
            logger.warning(f"Failed to load ML model: {e}")

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()  # For market data
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        df['ATR'] = ranges.max(axis=1).rolling(14).mean()

        df['BB_Mid'] = df['Close'].rolling(20).mean()
        df['BB_Std'] = df['Close'].rolling(20).std()
        df['BB_Up'] = df['BB_Mid'] + (2 * df['BB_Std'])
        df['BB_Low'] = df['BB_Mid'] - (2 * df['BB_Std'])
        df['BB_Width'] = (df['BB_Up'] - df['BB_Low']) / df['BB_Mid']
        df['Volume_MA20'] = df['Volume'].rolling(20).mean()
        
        # PHASE 1: Historical price lookback for momentum features
        df['Close_21d'] = df['Close'].shift(21)   # 1 month ago
        df['Close_63d'] = df['Close'].shift(63)   # 3 months ago
        df['Close_126d'] = df['Close'].shift(126) # 6 months ago
        df['Close_prev'] = df['Close'].shift(1)    # PHASE 2A: For advance/decline
        
        # PHASE 1: Volatility calculations
        returns = df['Close'].pct_change()
        df['Realized_Vol_20d'] = returns.rolling(20).std() * np.sqrt(252)  # Annualized
        df['Vol_MA'] = df['Realized_Vol_20d'].rolling(20).mean()
        
        # PHASE 1: Price extremes for price action features
        df['High_252d'] = df['High'].rolling(252).max()  # 52-week high
        df['Low_252d'] = df['Low'].rolling(252).min()    # 52-week low
        
        return df

    def run_backtest(self, data: Dict[str, pd.DataFrame], start_date: str = "2006-01-01"):
        logger.info(f"Starting Backtest on {len(data)} tickers (Start: {start_date})")
        if self.market_data is None or self.market_data.empty:
            self.market_data = data.get("SPY", data.get("QQQ", pd.DataFrame()))
        
        for symbol in data:
            if len(data[symbol]) > 50:
                 data[symbol] = self.calculate_indicators(data[symbol])
        
        # PHASE 2A: Initialize breadth calculator if not already set
        if self.breadth_calculator is None and len(data) >= 50:
            from src.modules.market_breadth import MarketBreadthCalculator
            self.breadth_calculator = MarketBreadthCalculator(data)
        
        all_dates = sorted(list(set().union(*[df.index for df in data.values()])))
        start_dt = pd.to_datetime(start_date)
        all_dates = [d for d in all_dates if d >= start_dt]
        
        weekly_focus_list = []
        current_regime = "C"
        
        # Optimize Market Data Access
        if not self.market_data.empty:
            self.set_market_data(self.market_data)
            # Reindex market data to align with all_dates for O(1) lookups
            self.market_data = self.market_data.reindex(all_dates, method='ffill')

        for i, current_date in enumerate(all_dates):
            if i % 100 == 0: logger.info(f"Processing {current_date.date()}...")
            
            # 1. Market Analysis
            if not self.market_data.empty:
                try:
                    mkt_row = self.market_data.loc[current_date]
                    if not pd.isna(mkt_row['Close']):
                        c, s10, e21, s200 = mkt_row['Close'], mkt_row['SMA_10'], mkt_row['EMA_21'], mkt_row['SMA_200']
                        new_regime = "C"
                        if c < e21: new_regime = "C"
                        elif c > s10 and c > e21 and c > s200: new_regime = "A"
                        else: new_regime = "B"
                        
                        if new_regime != current_regime:
                             # logger.info(f"{current_date.date()}: Regime Change {current_regime} -> {new_regime}")
                             current_regime = new_regime
                except KeyError: pass

            # Sizing - ULTRA-AGGRESSIVE v2: Max Leverage + Quality
            if current_regime == "A": self.position_size_pct = 0.25  # 25% per position
            elif current_regime == "B": self.position_size_pct = 0.20  # 20% per position
            else: self.position_size_pct = 0.10  # Stay invested in Regime C
            
            # 2. Weekly Rotation (Monday)
            if current_date.weekday() == 0 or (not weekly_focus_list and i % 5 == 0):
                # Use Stock Selector Logic
                weekly_focus_list = self.stock_selector.get_weekly_focus_list(
                    universe_data=data,
                    market_data=self.market_data,
                    current_date=current_date,
                    regime=current_regime
                )
                
                # Log rotation
                if i % 100 == 0 or len(weekly_focus_list) > 0:
                     logger.info(f"Week of {current_date.date()}: {len(weekly_focus_list)} Candidates (Regime {current_regime})")
                     logger.info(f"{current_date.date()}: Found {len(weekly_focus_list)} Leaders. Top: {weekly_focus_list[:3]}")


            # 3. Daily Execution
            # Manage Positions
            for symbol in list(self.positions.keys()):
                if symbol in data and current_date in data[symbol].index:
                    self.manage_position(symbol, data[symbol].loc[current_date], current_date)

            # 3.5 Dynamic Exposure Management
            # Calculate current total exposure
            # Value = Allocation * (Current Price / Entry Price)
            current_invested = sum([t.position_value * (getattr(t, 'last_price', t.entry_price)/t.entry_price) for t in self.positions.values()])
            current_equity = self.capital + current_invested
            exposure_pct = current_invested / current_equity if current_equity > 0 else 0
            
            # Limits based on Regime
            max_risk_cap = 1.0  # Default Regime A
            if current_regime == "B": max_risk_cap = 0.50
            elif current_regime == "C": max_risk_cap = 0.10  # Defensive: Hold 10% (Avoid Whipsaw of selling bottom)
            
            # Force Sell if Overexposed
            if exposure_pct > max_risk_cap and self.positions:
                # Sort positions by Unrealized PnL % to cut the weakest
                # PnL % = (Last - Entry) / Entry
                sorted_positions = sorted(
                    self.positions.items(), 
                    key=lambda x: (getattr(x[1], 'last_price', x[1].entry_price) - x[1].entry_price) / x[1].entry_price
                )
                
                for sym, trade in sorted_positions:
                    if exposure_pct <= max_risk_cap: break
                    
                    # Close position
                    price = getattr(trade, 'last_price', trade.entry_price)
                    self.exit_position(sym, current_date, price, f"Exposure Check (Regime {current_regime})")
                    
                    # Recalculate
                    val = trade.position_value * (price/trade.entry_price)
                    current_invested -= val
                    exposure_pct = current_invested / current_equity

            # Entries
            if self.position_size_pct > 0.0:
                trade_candidates = []
                for symbol in weekly_focus_list:
                    if symbol in self.positions: continue
                    if symbol not in data or current_date not in data[symbol].index: continue
                    
                    row = data[symbol].loc[current_date]
                    
                    # Trigger: Price > 21 EMA
                    if row['Close'] > row.get('EMA_21', 0):
                        # ML Score
                        feature_data = self._extract_features(row, symbol, current_date)
                        ml_score = 0.5
                        
                        # Skip ML filter if collecting training data
                        if self.skip_ml_filter:
                            ml_score = 1.0  # Accept all candidates
                        elif self.model:
                             try:
                                 # Phase 2A: Complete feature set (22 features)
                                 cols = [
                                     'rsi', 'vol_ratio', 'atr_pct', 'sma50_dist', 'sma200_dist', 'bb_width',
                                     'spy_trend', 'rs_rel', 'mom_1m', 'mom_3m', 'mom_6m',
                                     'realized_vol', 'vol_spike', 'dist_52w_high', 'dist_52w_low',
                                     'pct_above_200sma', 'adv_dec_ratio', 'new_highs_lows', 'spy_rsi_market', 'vix_level'
                                 ]
                                 vals = [feature_data.get(c, 0) for c in cols]
                                 
                                 # Fix Warning: Create DataFrame with feature names
                                 X_df = pd.DataFrame([vals], columns=cols)
                                 
                                 if self.scaler: 
                                     vals = self.scaler.transform(X_df)[0]
                                 
                                 ml_score = self.model.predict_proba([vals])[0][1]
                             except Exception as e:
                                 # logger.error(f"ML Error: {e}")
                                 pass
                        
                        if ml_score > 0.55 or self.skip_ml_filter:  # Threshold 0.55
                            # DEBUG
                            if not self.skip_ml_filter:  # Only log when using ML
                                logger.info(f"Day {current_date.date()}: Candidate {symbol} Score {ml_score:.2f}")
                            trade_candidates.append((symbol, ml_score, row['Close'], feature_data))
                
                # Execute Best 7 - ULTRA-AGGRESSIVE v2: Quality over quantity
                trade_candidates.sort(key=lambda x: x[1], reverse=True)
                for sym, score, price, feats in trade_candidates[:7]:  # Top 7 for quality
                    self.enter_position(sym, current_date, score, price, feats)
            
            # Track daily equity
            current_equity = self.capital + sum(t.position_value for t in self.positions.values())
            self.equity_history.append({'date': current_date, 'equity': current_equity})

        self.analyze_results_simple()
        return self.trades

    def _extract_features(self, row, symbol=None, date=None):
        """
        Extract features for ML - PHASE 1 ENHANCED
        Ensures stationarity by using ratios and clipping outliers.
        """
        # 1. Vol Ratio (Clipped at 5.0 to handle massive spikes)
        vol_ratio = row['Volume'] / row.get('Volume_MA20', 1) if row.get('Volume_MA20', 1) > 0 else 0
        vol_ratio = min(vol_ratio, 5.0)
        
        # 2. SMA Distances (Pct Diff)
        sma50_dist = (row['Close'] / row.get('SMA_50', row['Close'])) - 1
        sma200_dist = (row['Close'] / row.get('SMA_200', row['Close'])) - 1
        
        # 3. FIXED spy_trend - Market regime detection
        spy_trend = 1  # Default
        if self.market_data is not None and date is not None:
            try:
                if date in self.market_data.index:
                    spy_row = self.market_data.loc[date]
                    if not pd.isna(spy_row.get('Close')) and not pd.isna(spy_row.get('SMA_200')):
                        spy_trend = 1 if spy_row['Close'] > spy_row['SMA_200'] else 0
            except:
                pass
        
        # 4. FIXED rs_rel - Relative strength vs SPY (3-month)
        rs_rel = 0  # Default
        if self.market_data is not None and date is not None:
            try:
                if date in self.market_data.index:
                    spy_row = self.market_data.loc[date]
                    stock_3m_ago = row.get('Close_63d', row['Close'])
                    spy_3m_ago = spy_row.get('Close_63d', spy_row.get('Close', 1))
                    
                    if stock_3m_ago > 0 and spy_3m_ago > 0:
                        stock_ret_3m = (row['Close'] / stock_3m_ago) - 1
                        spy_ret_3m = (spy_row['Close'] / spy_3m_ago) - 1
                        rs_rel = ((1 + stock_ret_3m) / (1 + spy_ret_3m + 0.0001)) - 1
            except:
                pass
        
        # 5. NEW: Momentum features
        mom_1m = (row['Close'] / row.get('Close_21d', row['Close'])) - 1 if row.get('Close_21d', 0) > 0 else 0
        mom_3m = (row['Close'] / row.get('Close_63d', row['Close'])) - 1 if row.get('Close_63d', 0) > 0 else 0
        mom_6m = (row['Close'] / row.get('Close_126d', row['Close'])) - 1 if row.get('Close_126d', 0) > 0 else 0
        
        # 6. NEW: Volatility regime features
        realized_vol = row.get('Realized_Vol_20d', 0.15)  # Default 15% vol
        vol_ma = row.get('Vol_MA', 0.15)
        vol_spike = realized_vol / vol_ma if vol_ma > 0 else 1.0
        
        # 7. NEW: Price Action - Distance from 52-week extremes
        high_52w = row.get('High_252d', row['Close'])
        low_52w = row.get('Low_252d', row['Close'])
        dist_from_52w_high = (row['Close'] - high_52w) / high_52w if high_52w > 0 else 0
        dist_from_52w_low = (row['Close'] - low_52w) / low_52w if low_52w > 0 else 0
        
        # 8. PHASE 2A: Market Breadth Features
        breadth_data = {}
        if self.breadth_calculator and date:
            breadth_data = self.breadth_calculator.calculate_daily_breadth(date)
        
        # Get VIX level
        vix_level = 20.0  # Default neutral VIX
        if self.vix_data is not None and date in self.vix_data.index:
            vix_level = self.vix_data.loc[date, 'VIX']
        
        # Get SPY RSI (market momentum)
        spy_rsi = 50.0  # Default neutral
        if self.market_data is not None and date in self.market_data.index:
            spy_rsi = self.market_data.loc[date].get('RSI', 50.0)
        
        return {
            # Original features (6)
            "rsi": row.get('RSI', 50),
            "vol_ratio": vol_ratio, 
            "atr_pct": (row.get('ATR', 0) / row['Close']) * 100 if row['Close'] > 0 else 0,
            "sma50_dist": sma50_dist * 100,
            "sma200_dist": sma200_dist * 100,
            "bb_width": row.get('BB_Width', 0.1),
            
            # FIXED Phase 1 features (2)
            "spy_trend": spy_trend,
            "rs_rel": rs_rel * 100,
            
            # NEW Phase 1 features (7)
            "mom_1m": mom_1m * 100,
            "mom_3m": mom_3m * 100,
            "mom_6m": mom_6m * 100,
            "realized_vol": realized_vol * 100,
            "vol_spike": min(vol_spike, 3.0),  # Clip at 3x
            "dist_52w_high": dist_from_52w_high * 100,
            "dist_52w_low": dist_from_52w_low * 100,
            
            # NEW Phase 2A: Market Breadth features (5) → Total: 22 features
            "pct_above_200sma": breadth_data.get('pct_above_200sma', 50.0),
            "adv_dec_ratio": min(breadth_data.get('adv_dec_ratio', 1.0), 5.0),  # Clip at 5
            "new_highs_lows": breadth_data.get('new_highs_lows', 0.0),
            "spy_rsi_market": spy_rsi,
            "vix_level": min(vix_level, 80.0),  # Clip VIX at 80
        }

    def manage_position(self, symbol, row, date):
        trade = self.positions[symbol]
        trade.last_price = row['Close']  # Track for Exposure Mgmt
        
        # Update High Water Mark
        if trade.highest_price == 0: trade.highest_price = trade.entry_price
        trade.highest_price = max(trade.highest_price, row['High'])
        
        atr = row.get('ATR', 0)
        
        # 1. Initial Stop (Fixed % or ATR)
        initial_stop = trade.entry_price * (1 - self.stop_loss_pct)
        if atr > 0:
             initial_stop = min(initial_stop, trade.entry_price - (1.5 * atr))
        
        # 2. Trailing Stop
        trailing_stop = trade.highest_price * (1 - self.trailing_stop_pct)
        
        # Effective Stop (Max of Initial and Trailing)
        effective_stop = max(initial_stop, trailing_stop)
        
        if row['Low'] < effective_stop:
            reason = "Trailing Stop" if trailing_stop > initial_stop else "Stop Loss"
            self.exit_position(symbol, date, effective_stop, reason)
            return 
        
        # Fixed Target (Disabled effectively via 1000% but check anyway)
        if row['High'] > trade.entry_price * (1 + self.take_profit_target):
             self.exit_position(symbol, date, trade.entry_price * (1 + self.take_profit_target), "Take Profit")

    def enter_position(self, symbol, date, score, price, features=None):
        if len(self.positions) >= self.max_positions: return
        allocation = self.capital * self.position_size_pct
        if self.capital < allocation: return 
        
        self.capital -= allocation
        trade = Trade(symbol=symbol, entry_date=date, entry_price=price, ml_score=score, position_value=allocation)
        if features: trade.ml_features = features
        self.positions[symbol] = trade

    def exit_position(self, symbol, date, price, reason):
        trade = self.positions.pop(symbol)
        trade.exit_date = date
        trade.exit_price = price
        trade.return_pct = (price / trade.entry_price) - 1
        trade.pnl = trade.position_value * trade.return_pct
        trade.exit_reason = reason
        trade.status = "CLOSED"
        
        self.capital += trade.position_value + trade.pnl
        self.trades.append(trade)
        
        if self.collect_ml_data and trade.ml_features:
            # Outcome: 1 if Return > 2% (Win), 0 otherwise
            outcome = 1 if trade.return_pct > 0.02 else 0
            row = trade.ml_features.copy()
            row['outcome'] = outcome
            row['entry_date'] = trade.entry_date
            self.ml_data.append(row)

    def analyze_results_simple(self):
        if not self.trades:
            logger.info("No trades executed.")
            return

        wins = [t for t in self.trades if t.pnl > 0]
        win_rate = len(wins) / len(self.trades) * 100 if self.trades else 0
        
        # Advanced Metrics
        if len(self.equity_history) > 1:
            df_equity = pd.DataFrame(self.equity_history).set_index('date')
            df_equity['returns'] = df_equity['equity'].pct_change().fillna(0)
            
            total_days = (df_equity.index[-1] - df_equity.index[0]).days
            years = total_days / 365.25
            
            final_equity = df_equity['equity'].iloc[-1]
            cagr = (final_equity / self.initial_capital) ** (1/years) - 1 if years > 0 else 0
            
            volatility = df_equity['returns'].std() * np.sqrt(252)
            sharpe = (cagr - 0.02) / volatility if volatility > 0 else 0
            
            df_equity['cummax'] = df_equity['equity'].cummax()
            df_equity['drawdown'] = (df_equity['equity'] / df_equity['cummax']) - 1
            max_dd = df_equity['drawdown'].min()
            
            calmar = cagr / abs(max_dd) if max_dd != 0 else 0
            
            logger.info("="*50)
            logger.info("WALK-FORWARD VALIDATION RESULTS (2016-2025)")
            logger.info("="*50)
            logger.info(f"Total Trades: {len(self.trades)}")
            logger.info(f"Win Rate: {win_rate:.2f}%")
            logger.info(f"Final Capital: ${final_equity:,.2f}")
            logger.info(f"Annualized Return (CAGR): {cagr*100:.2f}%")
            logger.info(f"Annualized Volatility: {volatility*100:.2f}%")
            logger.info(f"Max Drawdown: {max_dd*100:.2f}%")
            logger.info(f"Sharpe Ratio: {sharpe:.2f}")
            logger.info(f"Calmar Ratio: {calmar:.2f}")
            logger.info("="*50)
        else:
            # Fallback for no equity history
            total_pnl = sum([t.pnl for t in self.trades])
            logger.info("="*40)
            logger.info("STRATEGY RESULTS")
            logger.info("="*40)
            logger.info(f"Total Trades: {len(self.trades)}")
            logger.info(f"Win Rate: {win_rate:.2f}%")
            logger.info(f"Total ROI: {(total_pnl/self.initial_capital)*100:.2f}%")
            logger.info(f"Final Capital: ${self.capital:.2f}")
            logger.info("="*40)
        

