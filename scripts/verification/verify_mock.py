import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from src.modules.data_fetcher import DataFetcher, TechnicalData, FundamentalData
from unittest.mock import MagicMock, patch

def verify_logic_with_mock():
    print("🚀 Starting Logic Verification (Mocked Data)")
    
    fetcher = DataFetcher()
    
    # 1. Mock Tickers
    tickers = ['STOCK_A', 'STOCK_B', 'STOCK_C', 'STOCK_D', 'STOCK_E']
    print(f"\n1. Mock Universe: {tickers}")
    
    # 2. Mock History Data
    # STOCK_A: +10%
    # STOCK_B: +50% (Best)
    # STOCK_C: -10% (Worst)
    # STOCK_D: +20%
    # STOCK_E: +5%
    
    mock_histories = {}
    performances = [1.1, 1.5, 0.9, 1.2, 1.05]
    
    for ticker, perf in zip(tickers, performances):
        # Create 250 days of data
        from datetime import datetime, timedelta
        dates = [datetime.now() - timedelta(days=x) for x in range(250)]
        dates.reverse()
        # Simple linear trend to achieve outcome
        start_price = 100.0
        end_price = 100.0 * perf
        prices = np.linspace(start_price, end_price, 250)
        
        df = pd.DataFrame({
            'Open': prices,
            'High': prices * 1.01,
            'Low': prices * 0.99,
            'Close': prices,
            'Volume': [1000000] * 250
        }, index=dates)
        mock_histories[ticker] = df

    # 3. Patch yfinance
    print("\n2. Running fetch_batch_data with mocks...")
    
    with patch('yfinance.Ticker') as MockTicker:
        # Configure mock to return specific history based on ticker symbol
        def side_effect(symbol):
            m = MagicMock()
            m.history.return_value = mock_histories.get(symbol, pd.DataFrame())
            m.info = {} # Empty mock info
            return m
            
        MockTicker.side_effect = side_effect
        
        # Run code under test
        results = fetcher.fetch_batch_data(tickers)
        
    print(f"✅ Processed {len(results)} stocks.")
    
    # 4. Verify Rankings
    print("\n3. Verifying RS Ratings...")
    # Expected Rank Estimate:
    # STOCK_B (+50%) -> Should be highest (~99)
    # STOCK_D (+20%) -> 2nd
    # STOCK_A (+10%) -> 3rd
    # STOCK_E (+5%)  -> 4th
    # STOCK_C (-10%) -> Lowest (~0)
    
    sorted_res = sorted(results.items(), key=lambda x: x[1][1].rs_rating, reverse=True)
    
    for symbol, (fund, tech) in sorted_res:
         print(f"   {symbol}: RS {tech.rs_rating:.1f}")
         
    # Check assertions
    top_stock = sorted_res[0][0]
    bottom_stock = sorted_res[-1][0]
    
    if top_stock == 'STOCK_B' and bottom_stock == 'STOCK_C':
        print("\n✅ SUCCESS: RS Logic identified Winner and Loser correctly.")
    else:
        print("\n❌ FAILURE: Ranking logic is incorrect.")

if __name__ == "__main__":
    verify_logic_with_mock()
