"""
AWS Lambda Handler: Stock Screening
Triggered: Daily (4:15 PM UTC) via EventBridge
Purpose: Screen stocks using CANSLIM methodology and send watchlist
"""
import json
import os
import logging
from datetime import datetime
import io
from io import BytesIO
import boto3
import pandas as pd
# Removed yfinance import
try:
    import joblib
    ML_AVAILABLE = True
except ImportError:
    joblib = None
    ML_AVAILABLE = False
    print("⚠️ ML Dependencies not found. Running in Technical-Only mode.")

# Import core module
import sys
sys.path.insert(0, '/opt/python')
from src.modules.stock_screener import CANSLIMScreener
from src.modules.data_fetcher import DataFetcher

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
ses_client = boto3.client('ses')

# Environment variables
S3_BUCKET = os.getenv('S3_BUCKET', 'trading-automation-data')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'trading@example.com')
TO_EMAIL = os.getenv('TO_EMAIL', 'your-email@example.com')
UNIVERSE = os.getenv('STOCK_UNIVERSE', 'SP500')  # SP500, NASDAQ100, etc.


def lambda_handler(event, context):
    """
    Main Lambda handler for stock screening

    Returns:
        dict: Response with screening results
    """
    logger.info(f"Stock Screener Lambda triggered at {datetime.utcnow().isoformat()}Z")

    try:
        # Initialize screener and fetcher
        screener = CANSLIMScreener()
        fetcher = DataFetcher()

        # Load stock universe (Dynamic Full Universe)
        stock_universe = fetcher.fetch_full_universe()
        logger.info(f"Screening {len(stock_universe)} stocks from Full Universe")
        
        # Load ML Model
        ml_model, scaler = load_ml_model()
        
        # Fetch SPY Context for ML
        spy_df = None
        try:
            # Use DataFetcher instead of yfinance
            spy_df = fetcher.fetch_price_history("SPY", days=400)
        except Exception as e:
            logger.warning(f"Could not fetch SPY history for ML: {e}")
        
        # STAGE 1: Broad Scan (Technical Focus)
        # Batch Fetch Data (Technicals + RS Rating, empty Fundamentals)
        logger.info("Stage 1: Broad Scan (Technical Focus)...")
        logger.info("Fetching batch data and calculating RS ratings...")
        batch_data = fetcher.fetch_batch_data(stock_universe)
        
        logger.info(f"Successfully fetched partial data for {len(batch_data)} stocks")

        # Preliminary Screen
        candidates = []
        for symbol, (fund_data, tech_data) in batch_data.items():
            try:
                if not tech_data:
                    continue
                
                # Screen with partial data
                score = screener.screen_stock(fund_data, tech_data)
                
                if score:
                    # We value Technical Score + RS Rating for the broad scan
                    # RS Rating (0-100) normalized to 0-3 approx: rs / 33.3
                    sort_metric = score.technical_score + (tech_data.rs_rating / 33.3)
                    candidates.append((symbol, score, fund_data, tech_data, sort_metric))
                    
            except Exception as e:
                logger.warning(f"Failed to pre-screen {symbol}: {str(e)}")

        # Sort by technical strength and take Top 50
        candidates.sort(key=lambda x: x[4], reverse=True)
        top_candidates = candidates[:50]
        
        logger.info(f"Stage 1 Complete. Selected top {len(top_candidates)} candidates for Deep Dive.")

        # STAGE 2: Deep Dive (Fetch Fundamentals)
        final_results = []
        logger.info("Stage 2: Deep Dive (Fetching Fundamentals)...")
        
        for idx, (symbol, score, fund_partial, tech_full, _) in enumerate(top_candidates):
            try:
                # Fetch full fundamentals
                fund_full = fetcher.get_fundamental_data(symbol)
                
                if fund_full:
                    # Re-screen with full data
                    final_score = screener.screen_stock(fund_full, tech_full)
                    
                    if final_score:
                        # [ML Integration]
                        ml_prob = 0.0
                        if ml_model:
                            try:
                                # Fetch History for ML Features
                                hist = fetcher.fetch_price_history(symbol, days=400)
                                if not hist.empty:
                                    features = calculate_ml_features(hist, spy_df)
                                    if features:
                                        # Predict
                                        X_pred = pd.DataFrame([features])
                                        cols = ['rsi', 'vol_ratio', 'atr_pct', 'sma50_dist', 'sma200_dist', 'bb_width', 'spy_trend', 'rs_rel']
                                        X_pred = X_pred[cols]
                                        
                                        if scaler:
                                            try: X_pred = scaler.transform(X_pred)
                                            except: pass
                                            
                                        ml_prob = ml_model.predict_proba(X_pred)[0][1]
                            except Exception as e:
                                logger.warning(f"ML Inference failed for {symbol}: {e}")

                        score_dict = {
                            'symbol': final_score.symbol,
                            'grade': final_score.grade,
                            'total_score': final_score.total_score,
                            'fundamental_score': final_score.fundamental_score,
                            'technical_score': final_score.technical_score,
                            'rs_rating': tech_full.rs_rating,
                            'ml_probability': round(ml_prob, 2), # Add P(Win)
                            'sector': fund_full.sector or 'N/A',
                            'breakdown': final_score.breakdown,
                            'trade_setup': {}
                        }
                        
                        # Calculate Trade Parameters
                        try:
                             # Re-Use history logic or fetch if missing (already fetched above)
                             if ml_model and 'hist' in locals() and not hist.empty:
                                 # Calculate ATR and Highs (Lowecase keys)
                                 # hist columns already normalized to lowercase in calculate_ml_features if called, 
                                 # but let's ensure we are safe if that didn't run or modified inplace
                                 hist.columns = [c.lower() for c in hist.columns]
                                 close = hist['close']
                                 current_price = close.iloc[-1]
                                 
                                 # ATR (14)
                                 high_low = hist['high'] - hist['low']
                                 high_close = (hist['high'] - close.shift()).abs()
                                 low_close = (hist['low'] - close.shift()).abs()
                                 tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                                 atr = tr.rolling(14).mean().iloc[-1]
                                 
                                 # Entry: 20 Day High (Breakout)
                                 high_20 = hist['high'].rolling(20).max().iloc[-1]
                                 # If Current Price is close to High 20 (> 95%), use High 20 as Entry.
                                 # Else use Current Price * 1.01 (Momentum)
                                 # Let's standardize on High 20 for "Breakout" style.
                                 entry_price = high_20 if high_20 > current_price else current_price
                                 
                                 stop_loss = entry_price - (2 * atr)
                                 risk = entry_price - stop_loss
                                 target = entry_price + (3 * risk)
                                 
                                 # Success Classification
                                 success_prob = "Low"
                                 if ml_prob >= 0.55: success_prob = "High"
                                 elif ml_prob >= 0.50: success_prob = "Med"
                                 
                                 score_dict['trade_setup'] = {
                                     'price': float(current_price),
                                     'entry': float(entry_price),
                                     'stop': float(stop_loss),
                                     'target': float(target),
                                     'success_prob': success_prob
                                 }
                        except Exception as e:
                            logger.warning(f"Failed to calc trade setup for {symbol}: {e}")
                        
                        # Boost Score if High Probability
                        if ml_prob > 0.55:
                            score_dict['total_score'] += 1.0 # Bonus for ML Validation
                            score_dict['grade'] += "+"
                            
                        final_results.append(score_dict)
                        logger.info(f"Refined {symbol}: Score {final_score.total_score:.2f} (ML: {ml_prob:.2f})")
                else:
                    # Fallback to partial if fetch fails
                    score_dict = {
                        'symbol': score.symbol,
                        'grade': score.grade,
                        'total_score': score.total_score,
                        'fundamental_score': score.fundamental_score,
                        'technical_score': score.technical_score,
                        'rs_rating': tech_full.rs_rating,
                        'breakdown': score.breakdown
                    }
                    final_results.append(score_dict)

            except Exception as e:
                logger.error(f"Error in Stage 2 for {symbol}: {e}")

        # Final Sort by Total Score
        results = final_results
        results.sort(key=lambda x: x.get('total_score', 0), reverse=True)

        # Filter to watchlist (A/B or top 10)
        watchlist = results[:20] # Take top 20 verified stocks

        logger.info(f"Finalizing {len(watchlist)} stocks for watchlist")

        # Save results to S3
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        s3_key = f"screening/{datetime.utcnow().strftime('%Y/%m/%d')}/watchlist_{timestamp}.json"

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps({'timestamp': timestamp, 'watchlist': watchlist}, indent=2),
            ContentType='application/json'
        )

        # Save CSV version
        if watchlist:
            df = pd.DataFrame(watchlist)
            csv_buffer = df.to_csv(index=False)
            csv_key = f"screening/{datetime.utcnow().strftime('%Y/%m/%d')}/watchlist_{timestamp}.csv"

            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=csv_key,
                Body=csv_buffer,
                ContentType='text/csv'
            )

        # Send email with top picks
        if watchlist:
            email_subject = f"Daily Stock Screening - {len(watchlist)} Candidates"
            email_body_text = format_watchlist_text(watchlist)
            email_body_html = format_watchlist_html(watchlist)
            send_email(email_subject, email_body_text, email_body_html)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Screening completed',
                'total_screened': len(results),
                'watchlist_count': len(watchlist),
                's3_location': f's3://{S3_BUCKET}/{s3_key}'
            })
        }

    except Exception as e:
        logger.error(f"Error in stock screening: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# --- ML Helper Functions ---
# --- ML Helper Functions ---
# Imports moved to top

ML_MODEL = None
SCALER = None

def load_ml_model():
    """Load ML Model from S3 (Cached)"""
    global ML_MODEL, SCALER
    
    if not ML_AVAILABLE:
        return None, None
        
    if ML_MODEL:
        return ML_MODEL, SCALER
        
    try:
        bucket = "trading-automation-data-904583676284" # Confirmed Bucket
        key = "models/breakout_classifier.joblib"
        
        logger.info(f"Downloading ML model from s3://{bucket}/{key}")
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        
        with BytesIO(obj['Body'].read()) as f:
            pipeline = joblib.load(f)
            
        # Handle Pipeline vs Dict
        if isinstance(pipeline, dict):
            ML_MODEL = pipeline.get('model')
            SCALER = pipeline.get('scaler')
        else:
            ML_MODEL = pipeline
            SCALER = None # Pipeline likely includes scaling
            
        logger.info("ML Model Loaded Successfully")
        return ML_MODEL, SCALER
    except Exception as e:
        logger.warning(f"Could not load ML Model: {e}")
        return None, None

def calculate_ml_features(df, spy_df):
    """
    Generate Advanced ML Features from Price History.
    Must match training schema: 
    ['rsi', 'vol_ratio', 'atr_pct', 'sma50_dist', 'sma200_dist', 'bb_width', 'spy_trend', 'rs_rel']
    """
    try:
        if df.empty: return None
        
        # Normalize columns to lowercase
        df.columns = [c.lower() for c in df.columns]
        
        row = df.iloc[-1]
        
        # 1. Technical Indicators
        close = df['close']
        window = 50
        sma50 = close.rolling(50).mean()
        sma200 = close.rolling(200).mean()
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(14).mean()
        
        # BB Width
        std = close.rolling(20).std()
        bb_upper = close.rolling(20).mean() + (std * 2)
        bb_lower = close.rolling(20).mean() - (std * 2)
        bb_width = (bb_upper - bb_lower) / close.rolling(20).mean()
        
        # Volume Ratio
        avg_vol = df['volume'].rolling(50).mean()
        
        # Get Latest Values
        curr_rsi = rsi.iloc[-1]
        curr_vol = df['volume'].iloc[-1]
        curr_avg_vol = avg_vol.iloc[-1]
        curr_atr = atr.iloc[-1]
        curr_close = close.iloc[-1]
        
        # SPY Trend & RS Rel
        spy_trend = 1
        rs_rel = 0
        if spy_df is not None and not spy_df.empty:
            # Ensure spy_df is lowercase
            spy_df.columns = [c.lower() for c in spy_df.columns]
            spy_close = spy_df['close']
            spy_sma50 = spy_close.rolling(50).mean()
            if spy_close.iloc[-1] < spy_sma50.iloc[-1]:
                spy_trend = 0
            
            # RS Rel (3 Month performance vs SPY)
            # Look back ~63 days
            start_idx = -63 if len(df) > 63 else 0
            spy_start_idx = -63 if len(spy_df) > 63 else 0
            
            stock_ret = (curr_close / df['close'].iloc[start_idx]) - 1
            spy_ret = (spy_close.iloc[-1] / spy_close.iloc[spy_start_idx]) - 1
            rs_rel = stock_ret - spy_ret
            
        features = {
            "rsi": curr_rsi,
            "vol_ratio": curr_vol / curr_avg_vol if curr_avg_vol > 0 else 1.0,
            "atr_pct": (curr_atr / curr_close) * 100 if curr_close > 0 else 0,
            "sma50_dist": (curr_close - sma50.iloc[-1]) / sma50.iloc[-1] * 100 if sma50.iloc[-1] > 0 else 0,
            "sma200_dist": (curr_close - sma200.iloc[-1]) / sma200.iloc[-1] * 100 if sma200.iloc[-1] > 0 else 0,
            "bb_width": bb_width.iloc[-1],
            "spy_trend": spy_trend,
            "rs_rel": rs_rel
        }
        
        # NaN safe
        for k, v in features.items():
            if pd.isna(v): features[k] = 0.0
            
        return features
        
    except Exception as e:
        logger.warning(f"Error calculating ML features: {e}")
        return None

def load_stock_universe():
    """Legacy: Load stock universe (Now handled by fetcher.fetch_sp500_tickers)"""
    return []


def format_watchlist_text(watchlist):
    """Format watchlist as plain text email"""
    # No limit, show all
    report = f"""
DAILY STOCK SCREENING RESULTS
{'=' * 70}
Date: {datetime.utcnow().strftime('%Y-%m-%d')}
Total Candidates: {len(watchlist)}

TOP CANDIDATES:
{'=' * 70}
"""
    
    # Headers
    report += f"{'Symbol':<8} {'Price':<10} {'ML Conf':<10} {'Success %':<10} {'Entry Signal':<20} {'Stop (2ATR)':<12} {'Target (3R)':<12} {'Sector':<15}\n"
    report += "-" * 110 + "\n"
    
    for stock in watchlist:
        setup = stock.get('trade_setup', {})
        price = setup.get('price', 0)
        entry = setup.get('entry', 0)
        stop = setup.get('stop', 0)
        target = setup.get('target', 0)
        prob_label = setup.get('success_prob', 'Low')
        ml_conf = stock.get('ml_probability', 0)
        sector = stock.get('sector', 'N/A')[:15] # Truncate
        
        entry_str = f"Buy Stop @ {entry:.2f}"
        
        report += f"{stock['symbol']:<8} ${price:<9.2f} {ml_conf:<9.1%} {prob_label:<10} {entry_str:<20} ${stop:<11.2f} ${target:<11.2f} {sector:<15}\n"

    report += "-" * 110 + "\n"

    report += f"""
{'=' * 70}
Full watchlist available in S3.
"""
    return report

def format_watchlist_html(watchlist):
    """Format watchlist as HTML email"""
    
    rows = ""
    for stock in watchlist:
        setup = stock.get('trade_setup', {})
        price = setup.get('price', 0)
        entry = setup.get('entry', 0)
        stop = setup.get('stop', 0)
        target = setup.get('target', 0)
        prob_label = setup.get('success_prob', 'Low')
        ml_conf = stock.get('ml_probability', 0)
        sector = stock.get('sector', 'N/A')
        
        if stop < entry:
            risk_per_share = entry - stop
            # $1000 Risk (1% of $100k)
            shares = int(1000 / risk_per_share) if risk_per_share > 0 else 0
            position_value = shares * entry
        else:
            shares = 0
            position_value = 0
            
        # Color coding for probability
        prob_color = "#28a745" if prob_label == "High" else "#ffc107" if prob_label == "Med" else "#6c757d"
        
        rows += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>{stock['symbol']}</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;">${price:.2f}</td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;">{ml_conf:.1%}</td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;"><span style="color: white; background-color: {prob_color}; padding: 4px 8px; border-radius: 4px; font-size: 0.9em;">{prob_label}</span></td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;">Buy Stop @ <strong>{entry:.2f}</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd; color: #dc3545;">${stop:.2f}</td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd; color: #28a745;">${target:.2f}</td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>{shares}</strong> (${position_value/1000:.1f}k)</td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;">{sector}</td>
        </tr>
        """

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 1100px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px;">Daily Stock Screening Results</h2>
            <p><strong>Date:</strong> {datetime.utcnow().strftime('%Y-%m-%d')}<br>
            <strong>Total Candidates:</strong> {len(watchlist)}</p>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; color: #6c757d;">Symbol</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; color: #6c757d;">Price</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; color: #6c757d;">ML Conf</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; color: #6c757d;">Success %</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; color: #6c757d;">Entry Signal</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; color: #6c757d;">Stop (2ATR)</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; color: #6c757d;">Target (3R)</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; color: #6c757d;">Pos Size (1% Risk)</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; color: #6c757d;">Sector</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            
            <p style="margin-top: 20px; color: #6c757d; font-size: 0.9em;">
                <em>This is an automated report generated by QuantZ Trading Lab. Past performance is not indicative of future results.</em>
            </p>
        </div>
    </body>
    </html>
    """
    return html

def send_email(subject, body_text, body_html=None):
    """Send email via SES with optional HTML"""
    try:
        message = {
            'Subject': {'Data': subject, 'Charset': 'UTF-8'},
            'Body': {
                'Text': {'Data': body_text, 'Charset': 'UTF-8'}
            }
        }
        
        if body_html:
            message['Body']['Html'] = {'Data': body_html, 'Charset': 'UTF-8'}
            
        ses_client.send_email(
            Source=FROM_EMAIL,
            Destination={'ToAddresses': [TO_EMAIL]},
            Message=message
        )
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)
