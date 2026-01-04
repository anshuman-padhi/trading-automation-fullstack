
import pandas as pd
import numpy as np
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger("backtester")

import joblib
import os

@dataclass
class Trade:
    symbol: str
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    status: str = "OPEN" # OPEN, CLOSED
    pnl: float = 0.0
    return_pct: float = 0.0
    exit_reason: str = ""

class Backtester:
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.trades: List[Trade] = []
        self.positions: Dict[str, Trade] = {} # Active positions
        
        # Strategy Parameters
        self.max_positions = 10
        self.position_size_pct = 0.10 # 10% per trade
        self.stop_loss_pct = 0.07 # 7% fixed stop
        self.take_profit_target = 0.20 # 20% target (basic)
        
        # ML Data Collection
        self.collect_ml_data = False
        self.ml_data = [] # List of dicts (Features + Target)
        
        # ML Integration
        self.model = None
        self.scaler = None
        self.market_data = None # SPY DataFrame
        self.load_model()
        
    def set_market_data(self, df: pd.DataFrame):
        """Set Market Index Data (SPY) for Relative Strength calc"""
        self.market_data = df.copy()
        # Pre-calculate Market Trend to save time
        if 'Close' in self.market_data.columns:
            self.market_data['SPY_SMA200'] = self.market_data['Close'].rolling(200).mean()
            self.market_data['SPY_Trend'] = (self.market_data['Close'] > self.market_data['SPY_SMA200']).astype(int)

    def load_model(self):
        """Try to load the ML model"""
        try:
            model_path = "scripts/ml/breakout_classifier.joblib"
            if os.path.exists(model_path):
                artifact = joblib.load(model_path)
                # Check if it's a pipeline dict or just a model
                if isinstance(artifact, dict) and 'model' in artifact:
                    self.model = artifact['model']
                    self.scaler = artifact.get('scaler')
                    logger.info(f"Loaded ML Pipeline from {model_path}")
                else:
                    self.model = artifact
                    logger.info(f"Loaded ML Model (Legacy) from {model_path}")
            else:
                pass 
        except Exception as e:
            logger.warning(f"Failed to load ML model: {e}")

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Technical Indicators for strategy"""
        df = df.copy()
        # ... (Existing Indicators) ...
        # Ensure calculated on Close
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # EMA 21 for dynamic trailing stop
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        # RSI (14-day)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # ATR (14-day)
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['ATR'] = true_range.rolling(14).mean()
        
        # [NEW] Bollinger Bands for Volatility Compression
        df['BB_Mid'] = df['Close'].rolling(20).mean()
        df['BB_Std'] = df['Close'].rolling(20).std()
        df['BB_Up'] = df['BB_Mid'] + (2 * df['BB_Std'])
        df['BB_Low'] = df['BB_Mid'] - (2 * df['BB_Std'])
        # BB Width %: (Up - Low) / Mid. Lower = Squeeze.
        df['BB_Width'] = (df['BB_Up'] - df['BB_Low']) / df['BB_Mid']
        
        # 20-Day High (Donchian Channel High) for Breakout
        df['High_20'] = df['High'].rolling(window=20).max().shift(1) # Previous 20 days high
        
        # Average Volume
        df['AvgVol_50'] = df['Volume'].rolling(window=50).mean()
        
        return df

    def run_backtest(self, symbol: str, df: pd.DataFrame) -> List[Trade]:
        """Run strategy on a single stock dataframe"""
        if df.empty or len(df) < 250:
            return []
            
        df = self.calculate_indicators(df)
        local_trades = []
        position: Optional[Trade] = None
        partial_profit_taken = False
        
        # Iterate day by day (skip first 200 for MA calc)
        for i in range(200, len(df)):
            date = df.index[i]
            row = df.iloc[i]
            prev = df.iloc[i-1]
            
            # --- EXIT LOGIC ---
            if position:
                current_pnl_pct = (row['Close'] - position.entry_price) / position.entry_price
                
                # 1. Profit Target: Sell 50% at +20%
                if not partial_profit_taken and current_pnl_pct >= self.take_profit_target:
                    # Logic: Record a partial trade exit (half size)
                    # For simplicity in this engine, we'll mark this event but keep tracking full PnL 
                    # with a weighted exit or just tighten stop aggressively.
                    # Implementation: Tighten stop to Break Even immediately.
                    partial_profit_taken = True
                    position.entry_price = position.entry_price # Update basis if needed, or keeping it simple
                    
                # 2. Dynamic Trailing Stop
                # If Profitable (>10%), use EMA 21 (tighter). Else use SMA 50 (looser).
                if current_pnl_pct > 0.10:
                    stop_price = row['EMA_21']
                    stop_reason = "Below EMA21 (Dynamic)"
                else:
                    stop_price = row['SMA_50']
                    stop_reason = "Below SMA50"
                    
                # Hard Stop Loss (Fixed 7%)
                hard_stop = position.entry_price * (1 - self.stop_loss_pct)
                
                # Check Exits
                if row['Low'] <= hard_stop:
                    position.exit_price = hard_stop
                    position.exit_date = date
                    position.exit_reason = "Stop Loss"
                    self._close_trade(position)
                    local_trades.append(position)
                    position = None
                    partial_profit_taken = False
                    continue
                
                elif row['Close'] < stop_price:
                    position.exit_price = row['Close']
                    position.exit_date = date
                    position.exit_reason = stop_reason
                    # If we took partial profit at +20%, outcomes are blended. 
                    # Simplified: We treat the whole trade as standard exit here.
                    self._close_trade(position)
                    local_trades.append(position)
                    position = None
                    partial_profit_taken = False
                    continue
            
            # --- ENTRY LOGIC ---
            elif not position:
                # Trend Filter: Price > SMA50 > SMA200
                is_uptrend = (row['Close'] > row['SMA_50']) and (row['SMA_50'] > row['SMA_200'])
                
                # Setup: Breakout above 20-day High
                breakout = (row['Close'] > row['High_20']) and (prev['Close'] <= prev['High_20'])
                
                # Volume Confirmation: Vol > 1.2 * AvgVol
                vol_confirm = row['Volume'] > (1.2 * row['AvgVol_50'])
                
                # [NEW] Look for Quality: RSI Not Overbought (< 70)
                # This ensures we aren't buying the top of a climax run
                rsi_ok = row['RSI'] < 70
                
                if is_uptrend and breakout and vol_confirm and rsi_ok:
                    trade = Trade(
                        symbol=symbol,
                        entry_date=date,
                        entry_price=row['Close'], 
                        status="OPEN"
                    )
                    
                    
                    # [Feature Engineering]
                    # Calculate Relative Strength (RS) on the fly if market data exists
                    rs_ranking = 0.5 # Default middle
                    spy_trend = 1 # Default Bull
                    
                    if self.market_data is not None and date in self.market_data.index:
                        spy_row = self.market_data.loc[date]
                        spy_trend = spy_row['SPY_Trend'] if 'SPY_Trend' in spy_row else 1
                        
                        # RS = (Stock / SPY)
                        # We use 3-month performance difference as proxy for RS Rating momentum
                        try:
                            # Look back 63 days (approx 3 months)
                            if i > 63:
                                stock_3m = (row['Close'] / df.iloc[i-63]['Close']) - 1
                                # We need SPY price 63 days ago relative to *this date*
                                # This is tricky with index alignment, simplified:
                                spy_prev = self.market_data.loc[:date].iloc[-64] if len(self.market_data.loc[:date]) > 64 else spy_row
                                spy_3m = (spy_row['Close'] / spy_prev['Close']) - 1
                                rs_ranking = stock_3m - spy_3m # Relative Performance
                        except:
                            rs_ranking = 0
                    
                    # Record ML Features
                    feature_data = {
                        "rsi": row['RSI'],
                        "vol_ratio": row['Volume'] / row['AvgVol_50'] if row['AvgVol_50'] > 0 else 0,
                        "atr_pct": (row['ATR'] / row['Close']) * 100 if row['Close'] > 0 else 0,
                        "sma50_dist": (row['Close'] - row['SMA_50']) / row['SMA_50'] * 100,
                        "sma200_dist": (row['Close'] - row['SMA_200']) / row['SMA_200'] * 100,
                        "bb_width": row['BB_Width'] if 'BB_Width' in row else 0,
                        "spy_trend": spy_trend,
                        "rs_rel": rs_ranking
                    }
                    
                    if self.collect_ml_data:
                        # We attach this dict to the Trade object to fill in the target later
                        trade.ml_features = feature_data
                        trade.ml_features['symbol'] = symbol
                        trade.ml_features['entry_date'] = date
                        
                    # [ML Integration] Filter by Model Confidence
                    if self.model and not self.collect_ml_data:
                        try:
                            # Create DataFrame for prediction
                            X_pred = pd.DataFrame([feature_data])
                            # Align features with training schema
                            cols = ['rsi', 'vol_ratio', 'atr_pct', 'sma50_dist', 'sma200_dist', 'bb_width', 'spy_trend', 'rs_rel']
                            # Handle case where old model used fewer features (Migration)
                            # If new features not in model, drop them? Or retraining required.
                            # For now, we assume retraining happens.
                            X_pred = X_pred[cols]
                            
                            # Apply Scaling if available
                            if self.scaler:
                                try:
                                    X_pred = self.scaler.transform(X_pred)
                                except:
                                    pass 
                            
                            prob = self.model.predict_proba(X_pred)[0][1] # Probability of Class 1 (Win)
                            
                            # Filter Threshold (Restored to Optimal: 0.55)
                            if prob < 0.55: 
                                continue 
                                
                        except Exception as e:
                            # logger.error(f"ML Prediction Error: {e}")
                            pass # Safely ignore if model not ready
                            
                    position = trade
                    partial_profit_taken = False
        
        # Close any open position at end
        if position:
            position.exit_price = df.iloc[-1]['Close']
            position.exit_date = df.index[-1]
            position.exit_reason = "End of Data"
            self._close_trade(position)
            local_trades.append(position)
            
        return local_trades

    def _close_trade(self, trade: Trade):
        trade.status = "CLOSED"
        trade.pnl = (trade.exit_price - trade.entry_price) / trade.entry_price
        trade.return_pct = trade.pnl * 100
        
        # [ML] Save the outcome (Target)
        if self.collect_ml_data and hasattr(trade, 'ml_features'):
            data_point = trade.ml_features.copy()
            data_point['outcome'] = 1 if trade.pnl > 0.05 else 0 # Win if > 5% profit
            data_point['return_pct'] = trade.return_pct
            self.ml_data.append(data_point)

    def analyze_results(self, trades: List[Trade], duration_years: float = 1.0) -> Dict:
        if not trades:
            return {
                "Total Trades": 0, 
                "Win Rate": 0.0, 
                "Total Return": 0.0,
                "CAGR": 0.0
            }
            
        wins = [t for t in trades if t.pnl > 0]
        losses = [t for t in trades if t.pnl <= 0]
        
        win_rate = len(wins) / len(trades) * 100
        avg_win = np.mean([t.return_pct for t in wins]) if wins else 0
        avg_loss = np.mean([t.return_pct for t in losses]) if losses else 0
        
        # Simple cumulative return (compounding)
        equity = 1.0
        for t in trades:
            equity *= (1 + t.pnl)
            
        total_return_pct = (equity - 1) * 100
        
        # Calculate CAGR: (End/Start)^(1/Years) - 1
        # Avoid division by zero or negative years
        if duration_years > 0:
            cagr = (equity ** (1 / duration_years) - 1) * 100
        else:
            cagr = 0.0

        # Advanced Metrics: Reconstruct Equity Curve
        # Simplification: Assume trades happen sequentially (no overlap handled perfectly here but good approx)
        returns_series = [t.pnl for t in trades]
        
        # Max Drawdown
        equity_curve = [1.0]
        running_equity = 1.0
        peak = 1.0
        max_drawdown = 0.0
        
        for pnl in returns_series:
            running_equity *= (1 + pnl)
            equity_curve.append(running_equity)
            if running_equity > peak:
                peak = running_equity
            dd = (peak - running_equity) / peak
            if dd > max_drawdown:
                max_drawdown = dd
        
        # Risk Ratios (Annualized)
        # Trades per year?
        trades_per_year = len(trades) / duration_years if duration_years > 0 else 0
        
        # Standard Deviation of returns
        std_dev = np.std(returns_series) if returns_series else 0
        
        # Annualized Volatility (Approx: Std * Sqrt(Trades/Year))
        import math
        ann_vol = std_dev * math.sqrt(trades_per_year) if trades_per_year > 0 else 0
        
        # Sharpe (Assuming Rf=3%)
        # Mean Annual Return approx CAGR
        rf = 0.03
        sharpe = (cagr/100 - rf) / ann_vol if ann_vol > 0 else 0
        
        # Sortino (Downside Dev)
        downside_returns = [r for r in returns_series if r < 0]
        downside_std = np.std(downside_returns) if downside_returns else 0
        ann_downside_vol = downside_std * math.sqrt(trades_per_year) if trades_per_year > 0 else 0
        sortino = (cagr/100 - rf) / ann_downside_vol if ann_downside_vol > 0 else 0
        
        # Calmar Ratio: CAGR / Max Drawdown
        calmar = (cagr/100) / max_drawdown if max_drawdown > 0 else 0

        return {
            "Total Trades": len(trades),
            "Win Rate": win_rate,
            "Avg Win": avg_win,
            "Avg Loss": avg_loss,
            "Total Return": total_return_pct,
            "CAGR": cagr,
            "Max Drawdown": max_drawdown * 100,
            "Sharpe Ratio": sharpe,
            "Sortino Ratio": sortino,
            "Calmar Ratio": calmar
        }
