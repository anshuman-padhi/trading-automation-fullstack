# System Architecture & Building Blocks

This document provides visual representations of the QuantZ Trading System's architecture, including its internal Python building blocks and its external cloud infrastructure.

## 1. High-Level Architecture (AWS System)

The system operates as a serverless application on AWS.
**Key Update (Jan 2026)**: A "Hybrid Data Fetching" strategy was implemented to resolve IP blocking issues for VIX and Sector data. Static data is now fetched locally and pushed to S3, while dynamic data is processed by Lambda.

```mermaid
graph TD
    subgraph "Local Environment (User Machine/EC2)"
        LocalScript["scripts/utils/refresh_static_data.sh"]
        LocalScript -->|Uploads JSON| S3
    end

    subgraph "External Data Providers"
        Alpaca["Alpaca Market Data API"]
        Yahoo["Yahoo Finance API"]
        YahooFallback["Direct API Fallback"]
    end

    subgraph "AWS Cloud (us-east-1)"
        EventBridge["Amazon EventBridge"]
        
        subgraph "Lambda Functions"
            MarketAnalysis["Market Analysis Handler"]
            StockScreener["Stock Screener Handler"]
            Dashboard["Dashboard Handler"]
            MLTrainer["ML Trainer Handler"]
        end
        
        subgraph "Storage (S3)"
            S3["S3 Bucket: trading-automation-data"]
            Sectors["sectors.json"]
            VIX["vix_latest.json"]
            Reports["Reports/JSON Output"]
        end
        
        SES["Amazon SES (Email)"]
    end

    %% Event Triggers
    EventBridge -->|Weekly Schedule| MarketAnalysis
    EventBridge -->|Daily Schedule| StockScreener
    EventBridge -->|Daily Schedule| Dashboard
    EventBridge -->|Weekly Schedule| MLTrainer

    %% Data Flow
    MarketAnalysis -->|Read Cache| VIX
    MarketAnalysis -->|Fallback Request| Yahoo
    MarketAnalysis -->|Fallback Request| YahooFallback
    
    StockScreener -->|Read Cache| Sectors
    StockScreener -->|Request Prices| Alpaca
    
    MLTrainer -->|Read Data| S3
    Dashboard -->|Read Stats| S3

    %% Output
    MarketAnalysis -->|Write Report| Reports
    StockScreener -->|Write Report| Reports
    Reports -->|Send Email| SES
    
    %% Cache Link
    S3 -- contains --> Sectors
    S3 -- contains --> VIX
```

## 2. Internal Building Blocks (Python Modules)

The logic is organized into modular components in `src/modules`.

```mermaid
classDiagram
    class DataFetcher {
        +get_stock_data(symbol)
        +get_sector_data(symbol) (S3 Cache)
        +get_fundamental_data(symbol)
    }
    
    class MarketAnalyzer {
        +analyze_market(index_symbol)
        +analyze_vix() (S3 + Fallback)
        +determine_regime()
    }
    
    class StockScreener {
        +run_screen(universe)
        +filter_stocks(criteria)
    }
    
    class StockSelector {
        +select_stocks(screened_list)
        +rank_stocks()
    }
    
    class PositionSizer {
        +calculate_position_size(price, volatility)
        +apply_risk_management(portfolio_value)
    }
    
    class TradeJournal {
        +log_trade(trade_details)
        +get_performance_stats()
    }

    DataFetcher --* StockScreener : uses
    DataFetcher --* MarketAnalyzer : uses
    
    MarketAnalyzer --* StockScreener : provides regime info
    
    StockScreener --> StockSelector : passes candidates
    StockSelector --> PositionSizer : calculates size for selected
    
    PositionSizer -.-> TradeJournal : potential link
```

## Note on Data Flow
1.  **Market Analysis** runs first to determine the Regime (Bull/Bear).
2.  **Stock Screener** uses the Regime to adjust filtering criteria (Aggressive/Defensive).
3.  **Data Fetcher** handles the complexity of S3 Caching vs Live API calls transparently.
