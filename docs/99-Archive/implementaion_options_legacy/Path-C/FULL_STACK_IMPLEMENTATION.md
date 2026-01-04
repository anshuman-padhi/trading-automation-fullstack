# FULL_STACK_IMPLEMENTATION_GUIDE.md
## Path C: Complete Full Stack Architecture
**Version: 1.0 | December 31, 2025**

---

## OVERVIEW: Full Stack vs Lambda

### Why Full Stack (Path C)?

**You Get:**
✓ Complete control over infrastructure
✓ Real-time API endpoints (not just scheduled tasks)
✓ Web dashboard you can access anytime
✓ WebSocket support for live alerts
✓ Scalable from day 1
✓ Professional production setup
✓ Better for team collaboration
✓ Database flexibility (SQL/NoSQL)

**Trade-off:**
- More complex to setup initially (20+ hours)
- Slightly higher cost ($50-200/month vs $2-5)
- More to manage and monitor
- But: Professional-grade system

### Architecture Comparison

```
LAMBDA (Path B):
Mac → Code → AWS Lambda (scheduled tasks)
Cost: $2-5/month
Setup: 4 weeks
Ideal for: Fully automated, set-and-forget

FULL STACK (Path C):
Mac → Code → Docker → AWS ECS/EC2 → PostgreSQL
       ↓
    Web Dashboard
    REST APIs
    WebSocket alerts
    
Cost: $50-200/month
Setup: 6-8 weeks
Ideal for: Professional trading, real-time monitoring, team use
```

---

## TECH STACK (Path C - Full Stack)

### Backend (Python)
- **Framework:** FastAPI (modern, fast, built-in async)
- **Server:** Uvicorn (ASGI server)
- **Database:** PostgreSQL (production-grade SQL)
- **Task Queue:** Celery + Redis (background jobs)
- **WebSocket:** FastAPI WebSockets (real-time alerts)

### Frontend (Web Dashboard)
- **Framework:** React + TypeScript
- **Styling:** Tailwind CSS
- **Charts:** Chart.js or Recharts
- **State:** Redux or Zustand
- **HTTP Client:** Axios

### DevOps & Deployment
- **Containerization:** Docker
- **Orchestration:** Docker Compose (local) → AWS ECS (production)
- **CI/CD:** GitHub Actions
- **Monitoring:** CloudWatch + Prometheus
- **Infrastructure as Code:** Terraform (optional)

### Cloud Services (AWS)
- **Compute:** EC2 or ECS Fargate (containers)
- **Database:** RDS PostgreSQL
- **Cache:** ElastiCache Redis
- **Storage:** S3 (backup CSVs)
- **API Gateway:** AWS API Gateway (optional)
- **Load Balancer:** ALB (Application Load Balancer)

---

## ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                    FULL STACK ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────┘

FRONTEND LAYER:
┌──────────────────────────────────────────────────────────┐
│  React Web Dashboard (Hosted on S3 + CloudFront)         │
│  ├─ Real-time charts & metrics                           │
│  ├─ Trade entry/exit forms                               │
│  ├─ Position sizing calculator                           │
│  ├─ Performance dashboard                                │
│  └─ Alert management                                     │
└──────────────────────────────────────────────────────────┘
         ↓ HTTPS / WebSocket
┌──────────────────────────────────────────────────────────┐
│  API Gateway (AWS API Gateway)                           │
│  Routes: /api/trades, /api/screening, /api/positions    │
│  WebSocket: /ws/alerts                                   │
└──────────────────────────────────────────────────────────┘
         ↓
BACKEND LAYER:
┌──────────────────────────────────────────────────────────┐
│  FastAPI Backend (ECS Fargate)                           │
│  ├─ REST APIs (CRUD operations)                          │
│  ├─ WebSocket handlers (real-time alerts)                │
│  ├─ Data validation & business logic                     │
│  └─ Error handling & logging                             │
├──────────────────────────────────────────────────────────┤
│  Celery Workers (Background Tasks)                       │
│  ├─ Market analysis (weekly)                             │
│  ├─ Stock screening (daily)                              │
│  ├─ Position sizing calculations                         │
│  ├─ Performance tracking                                 │
│  └─ Email alerts                                         │
├──────────────────────────────────────────────────────────┤
│  Redis Cache                                             │
│  ├─ Celery broker & backend                              │
│  ├─ Session management                                   │
│  ├─ Real-time data caching                               │
│  └─ Rate limiting                                        │
└──────────────────────────────────────────────────────────┘
         ↓
DATA LAYER:
┌──────────────────────────────────────────────────────────┐
│  PostgreSQL Database (RDS)                               │
│  ├─ trades table (trade history)                         │
│  ├─ watchlist table (screened stocks)                    │
│  ├─ market_data table (historical data)                  │
│  ├─ portfolio table (current positions)                  │
│  ├─ alerts table (alert history)                         │
│  └─ performance_metrics table (monthly stats)            │
├──────────────────────────────────────────────────────────┤
│  S3 Storage                                              │
│  ├─ CSV backups (daily export)                           │
│  ├─ Static assets (React build)                          │
│  └─ Historical reports                                   │
└──────────────────────────────────────────────────────────┘

EXTERNAL SERVICES:
├─ yfinance (stock data)
├─ AWS SES (email)
├─ AWS SNS (SMS alerts - optional)
└─ GitHub (code repository)
```

---

## DETAILED IMPLEMENTATION STEPS

### PHASE 1: LOCAL DEVELOPMENT (Weeks 1-2, 16 hours)

#### Week 1: Backend Foundation

**Day 1-2: Project Setup & Database Schema**

```bash
# Create project
mkdir trading-automation-fullstack
cd trading-automation-fullstack
git init

# Create directory structure
mkdir -p backend
mkdir -p frontend
mkdir -p docker
mkdir -p docs
mkdir -p tests
mkdir -p infrastructure

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
celery==5.3.4
redis==5.0.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
pandas==2.1.3
yfinance==0.2.32
email-validator==2.1.0
python-multipart==0.0.6
cors==1.0.1
python-jose==3.3.0
passlib==1.7.4
boto3==1.29.7
alembic==1.12.1
EOF

pip install -r requirements.txt

# Create .env template
cat > .env << 'EOF'
# Environment
ENVIRONMENT=development
DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/trading_db
SQLALCHEMY_ECHO=True

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=trading-automation-backups

# Email
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Trading System
ACCOUNT_EQUITY=25000
RISK_PER_TRADE=1

# API
API_TITLE=Trading Automation API
API_VERSION=1.0.0
API_DESCRIPTION=Full stack trading system
EOF

# PostgreSQL Docker setup (local development)
cd ..
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: trader
      POSTGRES_PASSWORD: tradingpass123
      POSTGRES_DB: trading_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U trader"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
EOF

# Start services
docker-compose up -d

# Verify
docker-compose ps
EOF
```

**Day 3-4: Database Models**

```python
# File: backend/app/models.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum

Base = declarative_base()

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    entry_date = Column(DateTime, index=True)
    entry_price = Column(Float)
    shares = Column(Integer)
    setup_type = Column(String(50))
    edges = Column(Integer)
    checklist_score = Column(Integer)
    
    exit_date = Column(DateTime, nullable=True)
    exit_price = Column(Float, nullable=True)
    exit_reason = Column(String(100), nullable=True)
    setup_grade = Column(String(1), nullable=True)
    execution_grade = Column(String(1), nullable=True)
    
    pnl_dollars = Column(Float, default=0)
    pnl_percent = Column(Float, default=0)
    days_held = Column(Integer, default=0)
    quadrant = Column(String(5), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_pnl(self):
        """Auto-calculate P&L when exit price set"""
        if self.exit_price:
            self.pnl_dollars = (self.exit_price - self.entry_price) * self.shares
            self.pnl_percent = ((self.exit_price - self.entry_price) / self.entry_price) * 100
            
            days = (self.exit_date - self.entry_date).days
            self.days_held = days if days >= 0 else 0

class WatchlistEntry(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True, unique=True)
    fund_score = Column(Integer)
    tech_score = Column(Integer)
    rs_rating = Column(Float)
    sector_score = Column(Integer)
    catalyst_score = Column(Integer)
    total_score = Column(Integer)
    grade = Column(String(1), index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    date = Column(DateTime, index=True)
    open_price = Column(Float)
    close_price = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    month = Column(String(7), index=True)  # YYYY-MM
    
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0)
    
    total_profit = Column(Float, default=0)
    total_loss = Column(Float, default=0)
    net_pnl = Column(Float, default=0)
    
    avg_win = Column(Float, default=0)
    avg_loss = Column(Float, default=0)
    profit_factor = Column(Float, default=0)
    expectancy = Column(Float, default=0)
    
    best_trade = Column(Float, default=0)
    worst_trade = Column(Float, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), index=True)  # WEAKNESS, BREAKDOWN, STOP_HIT, etc
    severity = Column(String(20), index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    symbol = Column(String(10), nullable=True, index=True)
    message = Column(Text)
    action = Column(Text)
    
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Day 5-7: API Endpoints (Module 1 & 3)**

```python
# File: backend/app/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import engine, SessionLocal
from app.models import Base, Trade, WatchlistEntry, PerformanceMetric
from app.schemas import TradeCreate, TradeUpdate, TradeResponse, PositionSizeRequest, PositionSizeResponse
from app.modules.market_analysis import MarketAnalyzer
from app.modules.position_sizer import PositionSizer

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="Trading Automation API",
    description="Full stack trading system",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== TRADES API ====================

@app.post("/api/trades", response_model=TradeResponse)
async def create_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    """Create new trade entry"""
    db_trade = Trade(**trade.dict())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

@app.get("/api/trades/{trade_id}", response_model=TradeResponse)
async def get_trade(trade_id: int, db: Session = Depends(get_db)):
    """Get specific trade"""
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@app.get("/api/trades", response_model=List[TradeResponse])
async def list_trades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all trades with pagination"""
    trades = db.query(Trade).offset(skip).limit(limit).all()
    return trades

@app.put("/api/trades/{trade_id}", response_model=TradeResponse)
async def update_trade(trade_id: int, trade_update: TradeUpdate, db: Session = Depends(get_db)):
    """Update trade with exit information"""
    db_trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    update_data = trade_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_trade, key, value)
    
    # Recalculate P&L
    db_trade.calculate_pnl()
    
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

@app.delete("/api/trades/{trade_id}")
async def delete_trade(trade_id: int, db: Session = Depends(get_db)):
    """Delete trade (soft delete in production)"""
    db_trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    db.delete(db_trade)
    db.commit()
    return {"status": "deleted"}

# ==================== POSITION SIZING API ====================

@app.post("/api/position-size", response_model=PositionSizeResponse)
async def calculate_position_size(request: PositionSizeRequest):
    """Calculate position size based on parameters"""
    sizer = PositionSizer(account_equity=request.account_equity)
    
    result = sizer.calculate_position_size(
        environment=request.environment,
        edges=request.edges,
        entry=request.entry_price,
        stop=request.stop_price,
        target=request.target_price
    )
    
    return PositionSizeResponse(**result)

# ==================== MARKET ANALYSIS API ====================

@app.post("/api/market-analysis")
async def analyze_market(symbols: List[str] = ["SPY", "QQQ", "IWM"]):
    """Run market analysis"""
    analyzer = MarketAnalyzer()
    results = analyzer.analyze_market_breadth(symbols)
    return results

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# ==================== STATS API ====================

@app.get("/api/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get trading statistics"""
    trades = db.query(Trade).filter(Trade.exit_date != None).all()
    
    if len(trades) == 0:
        return {"message": "No completed trades yet"}
    
    winners = [t for t in trades if t.pnl_dollars > 0]
    losers = [t for t in trades if t.pnl_dollars < 0]
    
    total_profit = sum(t.pnl_dollars for t in winners)
    total_loss = sum(abs(t.pnl_dollars) for t in losers)
    
    return {
        "total_trades": len(trades),
        "winning_trades": len(winners),
        "losing_trades": len(losers),
        "win_rate": (len(winners) / len(trades) * 100) if len(trades) > 0 else 0,
        "total_profit": total_profit,
        "total_loss": total_loss,
        "net_pnl": total_profit - total_loss,
        "profit_factor": total_profit / total_loss if total_loss > 0 else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Schemas for validation:**

```python
# File: backend/app/schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TradeCreate(BaseModel):
    symbol: str
    entry_date: datetime
    entry_price: float
    shares: int
    setup_type: str
    edges: int
    checklist_score: int

class TradeUpdate(BaseModel):
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    setup_grade: Optional[str] = None
    execution_grade: Optional[str] = None

class TradeResponse(TradeCreate):
    id: int
    pnl_dollars: float
    pnl_percent: float
    days_held: int
    quadrant: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PositionSizeRequest(BaseModel):
    account_equity: float
    environment: str  # A, B, C, D
    edges: int
    entry_price: float
    stop_price: float
    target_price: float

class PositionSizeResponse(BaseModel):
    shares: int
    position_size: float
    risk_amount: float
    potential_profit: float
    reward_to_risk: float
```

### PHASE 2: Backend Completion (Weeks 3-4, 20 hours)

**Module 2 & 4 APIs:**

```python
# Add to backend/app/main.py

# ==================== STOCK SCREENING API ====================

@app.post("/api/screening/run")
async def run_stock_screening(db: Session = Depends(get_db)):
    """Run stock screening and save to database"""
    from app.modules.stock_screener import StockScreener
    
    screener = StockScreener()
    results = screener.run()
    
    # Save to database
    for stock in results:
        existing = db.query(WatchlistEntry).filter(
            WatchlistEntry.symbol == stock['symbol']
        ).first()
        
        if existing:
            # Update existing
            for key, value in stock.items():
                setattr(existing, key, value)
        else:
            # Create new
            db_entry = WatchlistEntry(**stock)
            db.add(db_entry)
    
    db.commit()
    
    grade_a = [r for r in results if r['grade'] == 'A']
    grade_b = [r for r in results if r['grade'] == 'B']
    
    return {
        "total_screened": len(results),
        "grade_a": len(grade_a),
        "grade_b": len(grade_b),
        "watchlist": grade_a + grade_b
    }

@app.get("/api/watchlist")
async def get_watchlist(grade: str = None, db: Session = Depends(get_db)):
    """Get current watchlist"""
    query = db.query(WatchlistEntry)
    
    if grade:
        query = query.filter(WatchlistEntry.grade == grade)
    
    watchlist = query.order_by(WatchlistEntry.total_score.desc()).all()
    return watchlist

# ==================== DASHBOARD API ====================

@app.get("/api/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    """Get comprehensive dashboard data"""
    from datetime import datetime, timedelta
    
    # Get stats
    trades = db.query(Trade).filter(Trade.exit_date != None).all()
    
    if not trades:
        return {"message": "No completed trades"}
    
    winners = [t for t in trades if t.pnl_dollars > 0]
    losers = [t for t in trades if t.pnl_dollars < 0]
    
    # Monthly breakdown
    today = datetime.now()
    first_day_of_month = today.replace(day=1)
    monthly_trades = [t for t in trades if t.exit_date >= first_day_of_month]
    
    return {
        "overall": {
            "total_trades": len(trades),
            "win_rate": (len(winners) / len(trades) * 100) if trades else 0,
            "net_pnl": sum(t.pnl_dollars for t in trades),
            "profit_factor": sum(t.pnl_dollars for t in winners) / sum(abs(t.pnl_dollars) for t in losers) if losers else 0
        },
        "monthly": {
            "trades": len(monthly_trades),
            "pnl": sum(t.pnl_dollars for t in monthly_trades),
            "win_rate": (len([t for t in monthly_trades if t.pnl_dollars > 0]) / len(monthly_trades) * 100) if monthly_trades else 0
        },
        "recent_trades": [
            {
                "id": t.id,
                "symbol": t.symbol,
                "entry": t.entry_price,
                "exit": t.exit_price,
                "pnl": t.pnl_dollars,
                "grade": t.quadrant
            }
            for t in sorted(trades, key=lambda x: x.exit_date, reverse=True)[:10]
        ]
    }
```

**Background Tasks with Celery:**

```python
# File: backend/app/tasks.py

from celery import Celery
from app.modules.stock_screener import StockScreener
from app.modules.market_analysis import MarketAnalyzer
from app.modules.performance_dashboard import PerformanceDashboard

celery_app = Celery(
    'trading_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery_app.task(name="run_market_analysis")
def run_market_analysis():
    """Background task: Market analysis (weekly)"""
    analyzer = MarketAnalyzer()
    results = analyzer.run()
    return results

@celery_app.task(name="run_stock_screening")
def run_stock_screening():
    """Background task: Stock screening (daily)"""
    screener = StockScreener()
    results = screener.run()
    return results

@celery_app.task(name="update_dashboard")
def update_dashboard():
    """Background task: Dashboard update (daily)"""
    dashboard = PerformanceDashboard()
    dashboard.save_dashboard_json()
    return {"status": "dashboard_updated"}

@celery_app.task(name="check_alerts")
def check_alerts():
    """Background task: Alert monitoring (every 5 min)"""
    from app.modules.alerts_monitor import AlertsMonitor
    
    monitor = AlertsMonitor()
    monitor.run()
    return {"status": "alerts_checked"}

# Setup periodic tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'market-analysis-weekly': {
        'task': 'run_market_analysis',
        'schedule': crontab(day_of_week=6, hour=18, minute=0),  # Sunday 6 PM
    },
    'stock-screening-daily': {
        'task': 'run_stock_screening',
        'schedule': crontab(hour=16, minute=15),  # Daily 4:15 PM
    },
    'dashboard-update-daily': {
        'task': 'update_dashboard',
        'schedule': crontab(hour=20, minute=0),  # Daily 8 PM
    },
    'alerts-check-every-5min': {
        'task': 'check_alerts',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}
```

### PHASE 3: Frontend (Weeks 5-6, 16 hours)

**React Setup:**

```bash
# Create React frontend
cd frontend
npx create-react-app . --template typescript

# Install dependencies
npm install axios recharts zustand react-router-dom

# Create project structure
mkdir -p src/components
mkdir -p src/pages
mkdir -p src/services
mkdir -p src/store
mkdir -p src/types

# Configure API base URL
cat > src/services/api.ts << 'EOF'
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const tradingAPI = {
  // Trades
  getTrades: () => api.get('/trades'),
  createTrade: (data) => api.post('/trades', data),
  updateTrade: (id, data) => api.put(`/trades/${id}`, data),
  
  // Position Sizing
  calculatePosition: (data) => api.post('/position-size', data),
  
  // Screening
  runScreening: () => api.post('/screening/run'),
  getWatchlist: (grade?) => api.get('/watchlist', { params: { grade } }),
  
  // Dashboard
  getDashboard: () => api.get('/dashboard'),
  getStats: () => api.get('/stats'),
  
  // Market Analysis
  analyzeMarket: (symbols?) => api.post('/market-analysis', { symbols }),
};

export default api;
EOF
```

**Main Dashboard Component:**

```typescript
// File: frontend/src/pages/Dashboard.tsx

import React, { useEffect, useState } from 'react';
import { tradingAPI } from '../services/api';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DashboardData {
  overall: {
    total_trades: number;
    win_rate: number;
    net_pnl: number;
    profit_factor: number;
  };
  monthly: {
    trades: number;
    pnl: number;
    win_rate: number;
  };
  recent_trades: Array<any>;
}

export const Dashboard: React.FC = () => {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const response = await tradingAPI.getDashboard();
      setDashboard(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!dashboard) return <div>No data</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Trading Dashboard</h1>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-gray-600">Total Trades</div>
          <div className="text-3xl font-bold">{dashboard.overall.total_trades}</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-gray-600">Win Rate</div>
          <div className="text-3xl font-bold">{dashboard.overall.win_rate.toFixed(1)}%</div>
        </div>
        
        <div className={`bg-white p-6 rounded-lg shadow ${dashboard.overall.net_pnl > 0 ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'}`}>
          <div className="text-gray-600">Net P&L</div>
          <div className="text-3xl font-bold">${dashboard.overall.net_pnl.toFixed(2)}</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-gray-600">Profit Factor</div>
          <div className="text-3xl font-bold">{dashboard.overall.profit_factor.toFixed(2)}x</div>
        </div>
      </div>

      {/* Recent Trades Table */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Recent Trades</h2>
        <table className="w-full text-left">
          <thead>
            <tr className="border-b">
              <th>Symbol</th>
              <th>Entry</th>
              <th>Exit</th>
              <th>P&L</th>
              <th>Grade</th>
            </tr>
          </thead>
          <tbody>
            {dashboard.recent_trades.map((trade, idx) => (
              <tr key={idx} className="border-b hover:bg-gray-50">
                <td className="font-bold">{trade.symbol}</td>
                <td>${trade.entry.toFixed(2)}</td>
                <td>${trade.exit?.toFixed(2) || '-'}</td>
                <td className={trade.pnl > 0 ? 'text-green-600' : 'text-red-600'}>
                  ${trade.pnl.toFixed(2)}
                </td>
                <td>{trade.grade}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

**Trade Entry Component:**

```typescript
// File: frontend/src/components/TradeForm.tsx

import React, { useState } from 'react';
import { tradingAPI } from '../services/api';

export const TradeForm: React.FC = () => {
  const [formData, setFormData] = useState({
    symbol: '',
    entry_date: new Date().toISOString().split('T')[0],
    entry_price: 0,
    shares: 0,
    setup_type: 'VCP',
    edges: 5,
    checklist_score: 85,
  });

  const [positionSize, setPositionSize] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: isNaN(Number(value)) ? value : Number(value)
    }));
  };

  const calculatePosition = async () => {
    setLoading(true);
    try {
      const response = await tradingAPI.calculatePosition({
        account_equity: 25000,
        environment: 'A',
        edges: formData.edges,
        entry_price: formData.entry_price,
        stop_price: formData.entry_price * 0.95,  // 5% stop
        target_price: formData.entry_price * 1.20, // 20% target
      });
      setPositionSize(response.data);
    } catch (error) {
      console.error('Error calculating position size:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitTrade = async () => {
    try {
      await tradingAPI.createTrade(formData);
      alert('Trade recorded successfully!');
      setFormData({
        symbol: '',
        entry_date: new Date().toISOString().split('T')[0],
        entry_price: 0,
        shares: positionSize?.shares || 0,
        setup_type: 'VCP',
        edges: 5,
        checklist_score: 85,
      });
    } catch (error) {
      console.error('Error creating trade:', error);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow max-w-md">
      <h2 className="text-2xl font-bold mb-4">New Trade Entry</h2>
      
      <div className="space-y-4">
        <input
          type="text"
          name="symbol"
          placeholder="Symbol"
          value={formData.symbol}
          onChange={handleChange}
          className="w-full p-2 border rounded"
          maxLength="10"
        />
        
        <input
          type="date"
          name="entry_date"
          value={formData.entry_date}
          onChange={handleChange}
          className="w-full p-2 border rounded"
        />
        
        <input
          type="number"
          name="entry_price"
          placeholder="Entry Price"
          value={formData.entry_price}
          onChange={handleChange}
          className="w-full p-2 border rounded"
          step="0.01"
        />
        
        <select
          name="setup_type"
          value={formData.setup_type}
          onChange={handleChange}
          className="w-full p-2 border rounded"
        >
          <option>VCP</option>
          <option>FLAT BASE</option>
          <option>CUP & HANDLE</option>
          <option>POCKET PIVOT</option>
        </select>
        
        <input
          type="number"
          name="edges"
          placeholder="Edges"
          value={formData.edges}
          onChange={handleChange}
          className="w-full p-2 border rounded"
          min="0"
          max="10"
        />
        
        <button
          onClick={calculatePosition}
          disabled={!formData.entry_price}
          className="w-full bg-blue-500 text-white p-2 rounded disabled:bg-gray-300"
        >
          Calculate Position Size
        </button>
        
        {positionSize && (
          <div className="bg-blue-50 p-4 rounded">
            <div>Shares: {positionSize.shares}</div>
            <div>Position Size: ${positionSize.position_size.toFixed(2)}</div>
            <div>Risk: ${positionSize.risk_amount.toFixed(2)}</div>
            <div>Reward: ${positionSize.potential_profit.toFixed(2)}</div>
          </div>
        )}
        
        <input
          type="number"
          name="shares"
          placeholder="Shares"
          value={formData.shares}
          onChange={handleChange}
          className="w-full p-2 border rounded"
          min="0"
        />
        
        <button
          onClick={submitTrade}
          className="w-full bg-green-500 text-white p-2 rounded"
        >
          Record Trade
        </button>
      </div>
    </div>
  );
};
```

### PHASE 4: Dockerization & Deployment (Weeks 7-8, 16 hours)

**Docker Setup:**

```dockerfile
# File: docker/Dockerfile.backend

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend /app

# Run gunicorn
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]
```

```yaml
# File: docker-compose.prod.yml

version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://trader:${DB_PASSWORD}@postgres:5432/trading_db
      REDIS_URL: redis://redis:6379/0
      ENVIRONMENT: production
    depends_on:
      - postgres
      - redis
    restart: always

  celery:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    command: celery -A app.tasks worker -l info
    environment:
      DATABASE_URL: postgresql://trader:${DB_PASSWORD}@postgres:5432/trading_db
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  celery-beat:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    command: celery -A app.tasks beat -l info
    environment:
      DATABASE_URL: postgresql://trader:${DB_PASSWORD}@postgres:5432/trading_db
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: trader
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: trading_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

volumes:
  postgres_data:
```

**AWS Deployment with Terraform (Optional but recommended):**

```hcl
# File: infrastructure/main.tf

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# RDS PostgreSQL Database
resource "aws_db_instance" "trading_db" {
  identifier     = "trading-automation-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  
  allocated_storage = 20
  db_name          = "trading_db"
  username         = var.db_username
  password         = var.db_password
  
  skip_final_snapshot = false
  final_snapshot_identifier = "trading-db-final-snapshot"
  
  publicly_accessible = false
  
  tags = {
    Name = "trading-automation-db"
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "trading-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = 6379
  
  tags = {
    Name = "trading-redis"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "trading" {
  name = "trading-automation"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECR Repository for Docker images
resource "aws_ecr_repository" "trading_backend" {
  name                 = "trading-automation-backend"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
}

output "rds_endpoint" {
  value = aws_db_instance.trading_db.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "ecr_repository_url" {
  value = aws_ecr_repository.trading_backend.repository_url
}
```

---

## IMPLEMENTATION TIMELINE (Path C - Full Stack)

### Week 1-2: Backend Foundation
- [ ] Project setup & Docker environment
- [ ] Database schema design
- [ ] Core API endpoints (CRUD)
- [ ] Position sizing & market analysis APIs
- **Output:** Backend running locally with PostgreSQL

### Week 3-4: Backend Completion
- [ ] Screening & journal APIs
- [ ] Celery task scheduling
- [ ] Alert system
- [ ] Comprehensive testing
- **Output:** All 6 modules as APIs

### Week 5-6: Frontend Development
- [ ] React app setup
- [ ] Dashboard component
- [ ] Trade entry/exit forms
- [ ] Real-time charts
- [ ] Watchlist management
- **Output:** Full web interface

### Week 7-8: Deployment & Optimization
- [ ] Docker containerization
- [ ] AWS infrastructure setup (RDS, ElastiCache, ECS)
- [ ] Terraform automation
- [ ] CI/CD pipeline setup
- [ ] Performance optimization & monitoring
- **Output:** Production-ready system deployed

**Total Implementation Time: 20+ weeks vs 4 weeks (Lambda)**

---

## COST COMPARISON

### Lambda Path (B)
- Lambda: $0.20/month
- S3: $0.50/month
- SES: $0.10/month
- **Total: $1-5/month**

### Full Stack Path (C)
- ECS Fargate: $20-40/month
- RDS PostgreSQL: $30-60/month
- ElastiCache Redis: $10-20/month
- S3: $1/month
- Data transfer: $5-10/month
- **Total: $50-200/month**

**The trade-off:** Professionalism & scalability vs cost

---

## NEXT STEPS FOR FULL STACK

**This Week:**
1. [ ] Review this architecture document
2. [ ] Decide on full commitment (20+ weeks)
3. [ ] Set up Docker locally
4. [ ] Create PostgreSQL database

**Week 1:**
1. [ ] Follow "Phase 1: Backend Foundation" exactly
2. [ ] Get API running locally
3. [ ] Test database connections

---

Would you like me to create specific files for any phase?
