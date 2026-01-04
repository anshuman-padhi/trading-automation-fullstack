
import sys
import os
import logging
# Add project root
sys.path.append(os.getcwd())

from src.modules.data_fetcher import DataFetcher

logging.basicConfig(level=logging.INFO)

def test_fetch():
    fetcher = DataFetcher()
    print("Fetching NVDA fundamentals...")
    data = fetcher.get_fundamental_data('NVDA')
    
    if data:
        print(f"Symbol: {data.symbol}")
        print(f"Sector: {data.sector}")
        print(f"Data Object: {data}")
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    test_fetch()
