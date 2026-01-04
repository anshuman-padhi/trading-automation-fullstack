import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from datetime import datetime
from src.modules.market_analysis import MarketAnalyzer

def verify_environment_optimization():
    print("🚀 Verifying Environment Classification Optimization")
    
    analyzer = MarketAnalyzer()
    
    # Mock Data for Trends
    # We will simulate only the trend inputs by calling classify_market_environment directly
    # since we want to test the LOGIC, not the MA calculation again.
    
    test_cases = [
        {
            "name": "Bull Market (Grade A)",
            "inputs": {
                "short_trend": "UP", "intermediate_trend": "UP", "long_trend": "UP",
                "leadership_strong": True,
                "breadth_metrics": {"pct_above_50ma": 70.0}
            },
            "expected": "A"
        },
        {
            "name": "Bull Market but Weak Breadth (Grade B/Divergence)",
            "inputs": {
                "short_trend": "UP", "intermediate_trend": "UP", "long_trend": "UP",
                "leadership_strong": True,
                "breadth_metrics": {"pct_above_50ma": 30.0} # < 50%
            },
            "expected": "B"
        },
        {
            "name": "Bear Market (Grade C)",
            "inputs": {
                "short_trend": "DOWN", "intermediate_trend": "DOWN", "long_trend": "DOWN",
                "leadership_strong": False,
                "breadth_metrics": {"pct_above_50ma": 20.0}
            },
            "expected": "C"
        },
        {
            "name": "Correction/Recovery (Grade D)",
            "inputs": {
                "short_trend": "UP", "intermediate_trend": "UP", "long_trend": "DOWN",
                "leadership_strong": False,
                "breadth_metrics": {"pct_above_50ma": 45.0} # > 40% but Long trend DOWN
            },
            "expected": "D"
        }
    ]
    
    for case in test_cases:
        print(f"\nTesting: {case['name']}")
        result = analyzer.classify_market_environment(**case['inputs'])
        
        status = "✅ PASS" if result == case['expected'] else f"❌ FAIL (Got {result})"
        print(f"   Expected: {case['expected']} | Result: {result} -> {status}")

if __name__ == "__main__":
    verify_environment_optimization()
