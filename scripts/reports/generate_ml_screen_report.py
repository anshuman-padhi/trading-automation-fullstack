import sys
import os
import logging
import pandas as pd
import numpy as np
import boto3
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modules.stock_screener import CANSLIMScreener
from src.modules.data_fetcher import DataFetcher
from src.modules.backtester import Backtester

# Config
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("ml_screener")
# Suppress yfinance noise
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

def generate_report():
    logger.info("🚀 Starting ML-Enhanced Daily Stock Screener...")
    
    # 1. Base Screening (CANSLIM)
    # ---------------------------
    screener = CANSLIMScreener()
    fetcher = DataFetcher()
    
    # Use full universe
    universe = fetcher.fetch_full_universe()
    logger.info(f"Screening {len(universe)} stocks (Rule-Based)...")
    
    # Batch Fetch (Stage 1)
    batch_data = fetcher.fetch_batch_data(universe)
    
    scored_candidates = []
    for symbol, (fund_data, tech_data) in batch_data.items():
        if not tech_data: continue
        score = screener.screen_stock(fund_data, tech_data)
        
        # We rely on Technicals + RS for Stage 1 (since fundamentals are partial/empty)
        # RS Rating is 0-99. Technical Score is 0-3.
        # Combined Metric: Tech Score + (RS / 33)
        sort_metric = score.technical_score + (tech_data.rs_rating / 33.3)
        scored_candidates.append((symbol, sort_metric, score))
            
    # Sort and take Top 50 for ML Validation
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    top_candidates = [x[0] for x in scored_candidates[:50]]
            
    logger.info(f"Selected Top {len(top_candidates)} Rule-Based Candidates for ML Validation.")
    
    # 2. ML Validation
    # ----------------
    logger.info("🧠 Validating with Advanced ML Model...")
    
    bt = Backtester()
    
    # Load SPY for Context
    try:
        spy_df = yf.download("SPY", period="2y", progress=False)
        # Flatten if needed
        if isinstance(spy_df.columns, pd.MultiIndex):
            spy_df.columns = spy_df.columns.get_level_values(0)
        
        if not spy_df.empty:
            bt.set_market_data(spy_df)
    except Exception as e:
        logger.warning(f"SPY Data missing: {e}")
        
    ml_results = []
    
    for symbol in top_candidates:
        try:
            # Check yfinance download
            df = yf.download(symbol, period="2y", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            if df.empty or len(df) < 200:
                continue
                
            # Run Indicators
            df = bt.calculate_indicators(df)
            
            # Predict on LATEST candle
            last_row = df.iloc[-1]
            date = df.index[-1]
            
            # Construct Feature Dict (Must match backtester logic)
            # Need to manually construct it or expose a helper in backtester
            # Accessing internal logic is messy, ideally backtester has `predict_single(row)`
            # We will manually recreate the feature dict for now as it's quick
            
            # RS Calculation
            rs_ranking = 0.5
            spy_trend = 1
            if bt.market_data is not None and date in bt.market_data.index:
                 spy_row = bt.market_data.loc[date]
                 spy_trend = spy_row['SPY_Trend'] if 'SPY_Trend' in spy_row else 1
                 # Approx RS
                 try:
                     spy_prev = bt.market_data.loc[:date].iloc[-64]
                     spy_3m = (spy_row['Close'] / spy_prev['Close']) - 1
                     stock_row_prev = df.iloc[-64]
                     stock_3m = (last_row['Close'] / stock_row_prev['Close']) - 1
                     rs_ranking = stock_3m - spy_3m
                 except:
                     pass

            features = {
                "rsi": last_row['RSI'],
                "vol_ratio": last_row['Volume'] / last_row['AvgVol_50'] if last_row['AvgVol_50'] > 0 else 0,
                "atr_pct": (last_row['ATR'] / last_row['Close']) * 100 if last_row['Close'] > 0 else 0,
                "sma50_dist": (last_row['Close'] - last_row['SMA_50']) / last_row['SMA_50'] * 100,
                "sma200_dist": (last_row['Close'] - last_row['SMA_200']) / last_row['SMA_200'] * 100,
                "bb_width": last_row['BB_Width'] if 'BB_Width' in last_row else 0,
                "spy_trend": spy_trend,
                "rs_rel": rs_ranking
            }
            
            # Predict
            X_pred = pd.DataFrame([features])
            # Align cols (simple list)
            cols = ['rsi', 'vol_ratio', 'atr_pct', 'sma50_dist', 'sma200_dist', 'bb_width', 'spy_trend', 'rs_rel']
            X_pred = X_pred[cols]
            
            if bt.scaler:
                 X_pred = bt.scaler.transform(X_pred)
            
            prob = bt.model.predict_proba(X_pred)[0][1]
            
            # Calculate Exit/Entry
            atr = last_row['ATR']
            close = last_row['Close']
            
            # Entry: If breakout, Buy Stop above High. If pullback, Buy Limit?
            # Strategy is Breakout.
            entry_price = last_row['High_20'] if 'High_20' in last_row else close
            # If current close > High_20, we already broke out.
            if close > entry_price:
                entry_msg = f"Market Buy (Broke {entry_price:.2f})"
            else:
                entry_msg = f"Buy Stop @ {entry_price:.2f}"
                
            # Stop Loss (2 ATR)
            stop_loss = close - (2 * atr)
            
            # Target (3R)
            risk = close - stop_loss
            target = close + (3 * risk)
            
            ml_results.append({
                "Symbol": symbol,
                "Price": close,
                "ML_Conf": prob,
                "Entry": entry_msg,
                "Stop": stop_loss,
                "Target": target,
                "ATR": atr
            })
            
        except Exception as e:
            logger.error(f"Error validating {symbol}: {e}")

    # 3. Format Output
    # ----------------
    # Sort by ML Confidence
    ml_results.sort(key=lambda x: x['ML_Conf'], reverse=True)
    top_picks = ml_results[:20]
    
    print("\n" + "="*80)
    print("🤖 ML-ENHANCED DAILY STOCK SCREENER (TOP 20)")
    print("="*80)
    print(f"{'SYMBOL':<8} {'PRICE':<10} {'ML CONF':<10} {'ENTRY':<25} {'STOP':<10} {'TARGET':<10}")
    print("-" * 80)
    
    for p in top_picks:
        conf_str = f"{p['ML_Conf']*100:.1f}%"
        # Color code?
        print(f"{p['Symbol']:<8} ${p['Price']:<9.2f} {conf_str:<10} {p['Entry']:<25} ${p['Stop']:<9.2f} ${p['Target']:<9.2f}")
        
    print("="*80)

if __name__ == "__main__":
    generate_report()
