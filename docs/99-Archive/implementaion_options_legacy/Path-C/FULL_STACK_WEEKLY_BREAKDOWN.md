# FULL_STACK_WEEKLY_BREAKDOWN.md
## Path C: Week-by-Week Implementation (20+ weeks)
**December 31, 2025 onwards**

---

## WEEKS 1-2: BACKEND FOUNDATION (Local Development)

### Week 1: Project Setup & Database

**Day 1-2: Environment Setup (4 hours)**

```bash
# Create project structure
mkdir -p trading-automation-fullstack
cd trading-automation-fullstack
git init

# Backend directory
mkdir -p backend/{app,tests}
mkdir -p backend/app/{models,schemas,api,services,tasks}
mkdir -p docker
mkdir -p frontend
mkdir -p infrastructure
mkdir -p docs

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local

# Database
*.db
*.sqlite

# Docker
docker-compose.override.yml

# Node
node_modules/
build/
dist/

# Other
.DS_Store
*.log
.coverage
htmlcov/
EOF

# Initialize git
git add .
git commit -m "Initial project structure"
```

**Day 3-4: Docker & Database Setup (4 hours)**

```bash
# Create docker-compose for local development
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: trading_postgres
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
    container_name: trading_redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: trading_pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - postgres

volumes:
  postgres_data:

networks:
  default:
    name: trading_network
EOF

# Start services
docker-compose up -d

# Verify
docker-compose ps
docker-compose logs postgres
```

**Day 5-7: Backend Project Setup (6 hours)**

```bash
# Setup Python environment
cd backend
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Validation
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0

# Background tasks
celery==5.3.4
redis==5.0.1

# Data processing
pandas==2.1.3
numpy==1.26.2
yfinance==0.2.32

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1

# Security (later)
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# AWS
boto3==1.29.7

# Utilities
requests==2.31.0
aiohttp==3.9.1
EOF

pip install -r requirements.txt

# Create directory structure
mkdir -p app/{models,schemas,api,services,tasks,utils}
mkdir -p tests
mkdir -p migrations

# Create initial files
touch app/__init__.py
touch app/main.py
touch app/config.py
touch app/database.py
touch app/models/__init__.py
touch app/models/trade.py
touch app/models/watchlist.py
touch app/models/market_data.py
touch app/models/performance.py
touch app/models/alert.py

touch app/schemas/__init__.py
touch app/schemas/trade.py
touch app/schemas/position.py

touch app/api/__init__.py
touch app/api/trades.py
touch app/api/screening.py
touch app/api/dashboard.py
touch app/api/health.py

touch app/services/__init__.py
touch app/services/position_sizer.py
touch app/services/screener.py

touch app/tasks.py

# Create .env
cat > .env << 'EOF'
# Environment
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://trader:tradingpass123@localhost:5432/trading_db
SQLALCHEMY_ECHO=False

# Redis
REDIS_URL=redis://localhost:6379/0

# Trading
ACCOUNT_EQUITY=25000
RISK_PER_TRADE=1

# API
API_TITLE=Trading Automation API
API_VERSION=1.0.0
SECRET_KEY=your-secret-key-change-in-production
EOF

git add .
git commit -m "Backend initial setup with Docker"
```

### Week 2: Database Models & Initial API

**Day 1-2: Database Models (4 hours)**

```python
# File: backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://trader:tradingpass123@localhost:5432/trading_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Trading
    ACCOUNT_EQUITY: float = 25000
    RISK_PER_TRADE: float = 1
    
    # API
    API_TITLE: str = "Trading Automation API"
    API_VERSION: str = "1.0.0"
    SECRET_KEY: str = "dev-secret-key"
    
    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
```

```python
# File: backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    echo=settings.SQLALCHEMY_ECHO,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# File: backend/app/models/__init__.py
from .trade import Trade
from .watchlist import WatchlistEntry
from .market_data import MarketData
from .performance import PerformanceMetric
from .alert import Alert

__all__ = [
    "Trade",
    "WatchlistEntry",
    "MarketData",
    "PerformanceMetric",
    "Alert",
]
```

```python
# File: backend/app/models/trade.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Trade(Base):
    __tablename__ = "trades"
    
    # IDs
    id = Column(Integer, primary_key=True, index=True)
    
    # Entry Information
    symbol = Column(String(10), index=True, nullable=False)
    entry_date = Column(DateTime, index=True, nullable=False)
    entry_price = Column(Float, nullable=False)
    shares = Column(Integer, nullable=False)
    
    # Setup Information
    setup_type = Column(String(50), nullable=False)  # VCP, FLAT_BASE, etc
    edges = Column(Integer, nullable=False)
    checklist_score = Column(Integer, nullable=False)
    
    # Exit Information
    exit_date = Column(DateTime, nullable=True)
    exit_price = Column(Float, nullable=True)
    exit_reason = Column(String(100), nullable=True)
    setup_grade = Column(String(1), nullable=True)  # A, B, C, F
    execution_grade = Column(String(1), nullable=True)  # A, B, C, F
    
    # Calculated Fields
    pnl_dollars = Column(Float, default=0, nullable=False)
    pnl_percent = Column(Float, default=0, nullable=False)
    days_held = Column(Integer, default=0, nullable=False)
    quadrant = Column(String(5), nullable=True)  # ✓✓, ✓✗, ✗✓, ✗✗
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def calculate_pnl(self):
        """Auto-calculate P&L metrics"""
        if self.exit_price:
            self.pnl_dollars = (self.exit_price - self.entry_price) * self.shares
            self.pnl_percent = ((self.exit_price - self.entry_price) / self.entry_price) * 100
            
            if self.exit_date and self.entry_date:
                days = (self.exit_date - self.entry_date).days
                self.days_held = max(days, 0)
    
    def calculate_quadrant(self):
        """Calculate quadrant based on grades"""
        if self.setup_grade and self.execution_grade:
            if self.setup_grade == 'A' and self.execution_grade == 'A':
                self.quadrant = '✓✓'
            elif self.setup_grade == 'A' and self.execution_grade != 'A':
                self.quadrant = '✓✗'
            elif self.setup_grade != 'A' and self.execution_grade == 'A':
                self.quadrant = '✗✓'
            else:
                self.quadrant = '✗✗'
    
    def __repr__(self):
        return f"<Trade {self.symbol} {self.entry_price} @ {self.entry_date}>"
```

```python
# File: backend/app/models/watchlist.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WatchlistEntry(Base):
    __tablename__ = "watchlist"
    __table_args__ = (
        Index('idx_symbol_grade', 'symbol', 'grade'),
        Index('idx_score', 'total_score'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Stock Information
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    
    # Scores
    fund_score = Column(Integer, nullable=False)      # 0-3
    tech_score = Column(Integer, nullable=False)      # 0-3
    rs_rating = Column(Float, nullable=False)         # Relative strength %
    sector_score = Column(Integer, nullable=False)    # 0-2
    catalyst_score = Column(Integer, nullable=False)  # 0-2
    total_score = Column(Integer, index=True, nullable=False)  # 0-10
    
    # Grade
    grade = Column(String(1), index=True, nullable=False)  # A, B, C, F
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<WatchlistEntry {self.symbol} Grade:{self.grade} Score:{self.total_score}/10>"
```

**Day 3-4: Schemas & API Structure (4 hours)**

```python
# File: backend/app/schemas/trade.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TradeCreateRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    entry_date: datetime
    entry_price: float = Field(..., gt=0)
    shares: int = Field(..., gt=0)
    setup_type: str
    edges: int = Field(..., ge=0, le=10)
    checklist_score: int = Field(..., ge=0, le=100)

class TradeExitRequest(BaseModel):
    exit_date: datetime
    exit_price: float = Field(..., gt=0)
    exit_reason: str
    setup_grade: str = Field(..., regex="^[A-F]$")
    execution_grade: str = Field(..., regex="^[A-F]$")

class TradeResponse(TradeCreateRequest):
    id: int
    pnl_dollars: float
    pnl_percent: float
    days_held: int
    quadrant: Optional[str]
    created_at: datetime
    updated_at: datetime
    exit_date: Optional[datetime]
    exit_price: Optional[float]
    exit_reason: Optional[str]
    setup_grade: Optional[str]
    execution_grade: Optional[str]
    
    class Config:
        from_attributes = True
```

```python
# File: backend/app/api/health.py
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Trading Automation API",
        "docs": "/docs",
        "version": "1.0.0"
    }
```

```python
# File: backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import engine
from app.models import Base

# Import routers
from app.api import health

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description="Full stack trading automation system",
    version=settings.API_VERSION,
    debug=settings.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.LOG_LEVEL.lower(),
    )
```

**Day 5-7: Testing & First API (6 hours)**

```bash
# Test backend locally
cd backend

# Run FastAPI
python -m uvicorn app.main:app --reload

# In another terminal, test API
curl http://localhost:8000/health
curl http://localhost:8000/

# Expected responses:
# {"status":"healthy","timestamp":"...","version":"1.0.0"}
# {"message":"Trading Automation API","docs":"/docs","version":"1.0.0"}

# Visit http://localhost:8000/docs for interactive API docs!
```

---

## WEEKS 3-4: TRADES API & SERVICES

### Week 3: Trade CRUD Operations

**Complete Trade API endpoint:**

```python
# File: backend/app/api/trades.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import List

from app.database import get_db
from app.models import Trade
from app.schemas.trade import TradeCreateRequest, TradeExitRequest, TradeResponse

router = APIRouter(prefix="/api/trades", tags=["Trades"])

@router.post("", response_model=TradeResponse, status_code=201)
async def create_trade(
    request: TradeCreateRequest,
    db: Session = Depends(get_db)
):
    """Create new trade entry"""
    db_trade = Trade(**request.dict())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(trade_id: int, db: Session = Depends(get_db)):
    """Get trade by ID"""
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@router.get("", response_model=List[TradeResponse])
async def list_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    symbol: str = Query(None),
    grade: str = Query(None),
    db: Session = Depends(get_db)
):
    """List trades with filtering"""
    query = db.query(Trade)
    
    if symbol:
        query = query.filter(Trade.symbol == symbol.upper())
    if grade:
        query = query.filter(Trade.quadrant == grade)
    
    trades = query.order_by(desc(Trade.entry_date)).offset(skip).limit(limit).all()
    return trades

@router.put("/{trade_id}", response_model=TradeResponse)
async def update_trade_exit(
    trade_id: int,
    request: TradeExitRequest,
    db: Session = Depends(get_db)
):
    """Update trade with exit info"""
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    trade.exit_date = request.exit_date
    trade.exit_price = request.exit_price
    trade.exit_reason = request.exit_reason
    trade.setup_grade = request.setup_grade
    trade.execution_grade = request.execution_grade
    
    # Calculate P&L and quadrant
    trade.calculate_pnl()
    trade.calculate_quadrant()
    
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade

@router.delete("/{trade_id}", status_code=204)
async def delete_trade(trade_id: int, db: Session = Depends(get_db)):
    """Delete trade"""
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    db.delete(trade)
    db.commit()
    return None

@router.get("/stats/summary")
async def get_trade_stats(db: Session = Depends(get_db)):
    """Get trading statistics"""
    trades = db.query(Trade).filter(Trade.exit_date.isnot(None)).all()
    
    if not trades:
        return {
            "message": "No completed trades",
            "total_trades": 0,
            "win_rate": 0,
            "expectancy": 0
        }
    
    winners = [t for t in trades if t.pnl_dollars > 0]
    losers = [t for t in trades if t.pnl_dollars < 0]
    
    total_profit = sum(t.pnl_dollars for t in winners)
    total_loss = sum(abs(t.pnl_dollars) for t in losers)
    
    avg_win = total_profit / len(winners) if winners else 0
    avg_loss = total_loss / len(losers) if losers else 0
    
    win_pct = len(winners) / len(trades)
    expectancy = (win_pct * avg_win) - ((1 - win_pct) * avg_loss)
    
    return {
        "total_trades": len(trades),
        "winning_trades": len(winners),
        "losing_trades": len(losers),
        "win_rate": round((len(winners) / len(trades) * 100), 1) if trades else 0,
        "total_profit": round(total_profit, 2),
        "total_loss": round(total_loss, 2),
        "net_pnl": round(total_profit - total_loss, 2),
        "profit_factor": round(total_profit / total_loss, 2) if total_loss > 0 else 0,
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "expectancy": round(expectancy, 2),
    }
```

### Week 4: Position Sizer & Screening Services

**Position Sizer Service:**

```python
# File: backend/app/services/position_sizer.py
from app.config import settings
from typing import Dict

class PositionSizer:
    def __init__(self, account_equity: float = None):
        self.account_equity = account_equity or settings.ACCOUNT_EQUITY
        self.risk_per_trade = settings.RISK_PER_TRADE
    
    def calculate_position_size(
        self,
        environment: str,  # A, B, C, D
        edges: int,
        entry: float,
        stop: float,
        target: float
    ) -> Dict:
        """Calculate position size based on risk"""
        
        # Base size by environment
        base_sizes = {
            'A': 0.08,  # 8% of account
            'B': 0.06,  # 6% of account
            'C': 0.04,  # 4% of account
            'D': 0.02,  # 2% of account
        }
        
        base_size = base_sizes.get(environment, 0.06)
        
        # Edge adjustment multiplier
        edge_multipliers = {
            1: 0.5,
            2: 0.7,
            3: 0.85,
            4: 1.0,
            5: 1.2,
            6: 1.4,
            7: 1.6,
            8: 1.8,
            9: 2.0,
            10: 2.2,
        }
        
        edge_mult = edge_multipliers.get(min(edges, 10), 1.0)
        
        # Calculate risk amount
        risk_per_share = abs(entry - stop)
        if risk_per_share == 0:
            raise ValueError("Stop loss cannot equal entry price")
        
        # Determine shares
        risk_amount = self.account_equity * self.risk_per_trade / 100
        shares = int((risk_amount / risk_per_share) * base_size * edge_mult)
        
        # Verify against risk formula
        actual_risk = (shares * risk_per_share) / self.account_equity * 100
        
        if actual_risk > self.risk_per_trade * 2:
            # Reduce shares if risk too high
            shares = int(shares * 0.5)
        
        # Calculate metrics
        position_size = shares * entry
        potential_profit = shares * (target - entry)
        reward_to_risk = (target - entry) / (entry - stop) if stop < entry else 0
        
        return {
            "shares": shares,
            "position_size": round(position_size, 2),
            "entry_price": entry,
            "stop_price": stop,
            "target_price": target,
            "risk_amount": round(shares * risk_per_share, 2),
            "potential_profit": round(potential_profit, 2),
            "reward_to_risk": round(reward_to_risk, 2),
            "environment": environment,
            "edges": edges,
        }
```

**Position Size API:**

```python
# Add to backend/app/api/trades.py

from pydantic import BaseModel

class PositionSizeRequest(BaseModel):
    environment: str
    edges: int
    entry_price: float
    stop_price: float
    target_price: float

@router.post("/calculate-position")
async def calculate_position(request: PositionSizeRequest):
    """Calculate position size"""
    from app.services.position_sizer import PositionSizer
    
    sizer = PositionSizer()
    result = sizer.calculate_position_size(
        environment=request.environment,
        edges=request.edges,
        entry=request.entry_price,
        stop=request.stop_price,
        target=request.target_price
    )
    return result
```

---

## WEEKS 5-6: ADVANCED APIS (Screening, Dashboard, Alerts)

**Stock Screening API:**

```python
# File: backend/app/api/screening.py
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import WatchlistEntry
from app.schemas.watchlist import WatchlistResponse

router = APIRouter(prefix="/api/screening", tags=["Screening"])

@router.post("/run")
async def run_screening(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run stock screening (background task)"""
    background_tasks.add_task(screening_task, db)
    return {"status": "Screening started in background"}

def screening_task(db: Session):
    """Background screening task"""
    from app.modules.stock_screener import StockScreener
    
    screener = StockScreener()
    results = screener.run()
    
    for stock in results:
        # Update or create
        entry = db.query(WatchlistEntry).filter(
            WatchlistEntry.symbol == stock['symbol']
        ).first()
        
        if entry:
            for key, value in stock.items():
                setattr(entry, key, value)
        else:
            entry = WatchlistEntry(**stock)
            db.add(entry)
    
    db.commit()

@router.get("/watchlist")
async def get_watchlist(
    grade: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get watchlist entries"""
    query = db.query(WatchlistEntry)
    
    if grade:
        query = query.filter(WatchlistEntry.grade == grade)
    
    results = query.order_by(WatchlistEntry.total_score.desc()).offset(skip).limit(limit).all()
    return results

@router.get("/grades-summary")
async def get_grades_summary(db: Session = Depends(get_db)):
    """Get summary by grade"""
    from sqlalchemy import func
    
    grades = db.query(
        WatchlistEntry.grade,
        func.count(WatchlistEntry.id).label("count")
    ).group_by(WatchlistEntry.grade).all()
    
    return {grade: count for grade, count in grades}
```

**Dashboard API:**

```python
# File: backend/app/api/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Trade, WatchlistEntry

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("")
async def get_dashboard(db: Session = Depends(get_db)):
    """Get comprehensive dashboard data"""
    
    # Get all completed trades
    all_trades = db.query(Trade).filter(Trade.exit_date.isnot(None)).all()
    
    if not all_trades:
        return {"message": "No trading data"}
    
    # Overall stats
    winners = [t for t in all_trades if t.pnl_dollars > 0]
    losers = [t for t in all_trades if t.pnl_dollars < 0]
    
    total_profit = sum(t.pnl_dollars for t in winners)
    total_loss = sum(abs(t.pnl_dollars) for t in losers)
    net_pnl = total_profit - total_loss
    
    # Monthly stats
    today = datetime.now()
    month_start = today.replace(day=1)
    monthly_trades = [t for t in all_trades if t.exit_date >= month_start]
    
    # Watchlist stats
    watchlist_counts = db.query(
        WatchlistEntry.grade,
        func.count(WatchlistEntry.id).label("count")
    ).group_by(WatchlistEntry.grade).all()
    
    # Recent trades
    recent = sorted(all_trades, key=lambda x: x.exit_date, reverse=True)[:10]
    
    return {
        "overall": {
            "total_trades": len(all_trades),
            "winning_trades": len(winners),
            "losing_trades": len(losers),
            "win_rate": round((len(winners) / len(all_trades) * 100), 1) if all_trades else 0,
            "total_profit": round(total_profit, 2),
            "total_loss": round(total_loss, 2),
            "net_pnl": round(net_pnl, 2),
            "profit_factor": round(total_profit / total_loss, 2) if total_loss > 0 else 0,
            "best_trade": round(max([t.pnl_dollars for t in all_trades]), 2) if all_trades else 0,
            "worst_trade": round(min([t.pnl_dollars for t in all_trades]), 2) if all_trades else 0,
        },
        "monthly": {
            "trades": len(monthly_trades),
            "pnl": round(sum(t.pnl_dollars for t in monthly_trades), 2),
            "win_rate": round((len([t for t in monthly_trades if t.pnl_dollars > 0]) / len(monthly_trades) * 100), 1) if monthly_trades else 0,
        },
        "watchlist": {grade: count for grade, count in watchlist_counts},
        "recent_trades": [
            {
                "id": t.id,
                "symbol": t.symbol,
                "entry": t.entry_price,
                "exit": t.exit_price,
                "shares": t.shares,
                "pnl": round(t.pnl_dollars, 2),
                "pnl_pct": round(t.pnl_percent, 1),
                "grade": t.quadrant,
                "days_held": t.days_held,
            }
            for t in recent
        ]
    }
```

---

## WEEKS 7-8: CELERY, DOCKER & DEPLOYMENT

**Celery Configuration:**

```python
# File: backend/app/celery_app.py
from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    'trading_tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.tasks.screening',
        'app.tasks.market_analysis',
        'app.tasks.dashboard',
        'app.tasks.alerts',
    ]
)

# Task routing
celery_app.conf.task_routes = {
    'app.tasks.screening.run_screening': {'queue': 'screening'},
    'app.tasks.market_analysis.run_analysis': {'queue': 'analysis'},
    'app.tasks.alerts.check_alerts': {'queue': 'alerts'},
}

# Beat schedule (periodic tasks)
celery_app.conf.beat_schedule = {
    'market-analysis-weekly': {
        'task': 'app.tasks.market_analysis.run_analysis',
        'schedule': crontab(day_of_week=6, hour=18, minute=0),  # Sunday 6 PM
    },
    'stock-screening-daily': {
        'task': 'app.tasks.screening.run_screening',
        'schedule': crontab(hour=16, minute=15),  # Daily 4:15 PM
    },
    'dashboard-update-daily': {
        'task': 'app.tasks.dashboard.update_dashboard',
        'schedule': crontab(hour=20, minute=0),  # Daily 8 PM
    },
    'alerts-check-5min': {
        'task': 'app.tasks.alerts.check_alerts',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
```

**Docker Setup:**

```dockerfile
# File: Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# File: docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
      ENVIRONMENT: production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: always

  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile.backend
    command: celery -A app.celery_app worker -l info
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
      ENVIRONMENT: production
    depends_on:
      - postgres
      - redis
    restart: always

  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile.backend
    command: celery -A app.celery_app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
      ENVIRONMENT: production
    depends_on:
      - postgres
      - redis
      - backend
    restart: always

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always

volumes:
  postgres_data:

networks:
  default:
    name: trading_network
```

---

## WEEKS 9-14: FRONTEND DEVELOPMENT

Implement React components for:
- Trading dashboard
- Trade entry/exit forms
- Watchlist display
- Performance charts
- Real-time alerts

---

## WEEKS 15-20: DEPLOYMENT & OPTIMIZATION

Deploy to AWS ECS, set up CI/CD, performance tuning.

---

## NEXT STEP

**This Week:**
1. [ ] Review this breakdown
2. [ ] Commit to 20-week timeline
3. [ ] Start Week 1: Backend Foundation (today)

**Starting Tomorrow:**
Follow Week 1 instructions exactly.

Would you like me to continue with Weeks 9-20 details or start Week 1 implementation immediately?
