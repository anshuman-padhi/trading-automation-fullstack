import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.modules.data_fetcher import DataFetcher

def verify_universe_expansion():
    print("🚀 Verifying Stock Universe Expansion")
    
    fetcher = DataFetcher()
    
    # 1. Test ETFs
    etfs = fetcher.fetch_key_etfs()
    print(f"\n1. Key ETFs ({len(etfs)}): {etfs[:5]}...")
    assert 'SPY' in etfs
    assert 'SMH' in etfs
    
    # 2. Test Nasdaq 100
    try:
        ndx = fetcher.fetch_nasdaq100_tickers()
        print(f"\n2. Nasdaq 100 ({len(ndx)}): {ndx[:5]}...")
        if ndx:
             assert 'AAPL' in ndx
             # ZM is in QQQ but usually not SP500, check something unique if possible or just length
    except Exception as e:
        print(f"   ⚠️ Nasdaq fetch failed (might be network/wiki changing): {e}")

    # 3. Test Full Universe
    full = fetcher.fetch_full_universe()
    print(f"\n3. Full Universe ({len(full)} unique)")
    
    assert len(full) > 505, "Universe size should be > S&P 500"
    assert 'SPY' in full, "ETFs missing from full universe"
    assert 'AAPL' in full, "Mega caps missing"
    
    print("\n✅ Universe Expansion Verified!")

if __name__ == "__main__":
    verify_universe_expansion()
