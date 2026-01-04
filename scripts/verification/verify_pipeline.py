from datetime import datetime
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from src.modules.stock_screener import CANSLIMScreener
from src.modules.data_fetcher import DataFetcher

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verification")

def verify_pipeline():
    print("🚀 Starting Pipeline Verification")
    
    # 1. Initialize
    fetcher = DataFetcher()
    screener = CANSLIMScreener()
    
    # 2. Fetch Universe (Test limit to 20 for speed)
    print("\n1. Fetching Universe...")
    try:
        tickers = fetcher.fetch_sp500_tickers()
        print(f"✅ Fetched {len(tickers)} tickers. Sample: {tickers[:5]}")
    except Exception as e:
        print(f"❌ Failed to fetch tickers: {e}")
        return

    # Use a small subset for testing logic
    test_tickers = tickers[:20] if tickers else ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL']
    
    # 3. Batch Fetch & RS Calc
    print(f"\n2. Batch Fetching Data for {len(test_tickers)} stocks...")
    try:
        batch_results = fetcher.fetch_batch_data(test_tickers)
        print(f"✅ Fetched data for {len(batch_results)} stocks.")
        
        # Verify RS Ratings exist and are roughly distributed
        rs_ratings = [d[1].rs_rating for d in batch_results.values() if d[1]]
        print(f"   RS Ratings Sample: {rs_ratings[:5]}")
        
    except Exception as e:
        print(f"❌ Batch fetch failed: {e}")
        return

    # 4. Screening
    print("\n3. Screening...")
    screened_results = []
    for symbol, (fund, tech) in batch_results.items():
        if not fund or not tech: continue
        
        score = screener.screen_stock(fund, tech)
        screened_results.append(score)

    print(f"✅ Screened {len(screened_results)} stocks.")
    
    # Show Top Results
    screened_results.sort(key=lambda x: x.total_score, reverse=True)
    print("\n🏆 Top Results:")
    for r in screened_results[:3]:
        print(f"   {r.symbol}: Grade {r.grade} (Score: {r.total_score}) | RS: {r.breakdown['technical'].get('rs_rating', 'N/A')}")

if __name__ == "__main__":
    verify_pipeline()
