#!/bin/bash
# Refresh Static Data (VIX and Sectors) to S3
# Run this script periodically (e.g., weekly or before manual report triggers) 
# if scraping on Lambda is blocked.
# usage: ./scripts/utils/refresh_static_data.sh (from project root)

set -e

echo "🔄 Refreshing VIX and Sector Cache..."

echo "📊 Fetching VIX (Local yfinance)..."
python3 scripts/utils/cache_vix.py

echo "🏢 Fetching Sectors (Local yfinance)..."
# This might take a few minutes for 500 stocks
# python3 scripts/utils/cache_sectors.py 

echo "✅ Cache updated."
echo "Note: scripts/utils/cache_sectors.py interacts with 500 tickers, run it manually if needed."
