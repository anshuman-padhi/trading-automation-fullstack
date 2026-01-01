"""
Module 2: Stock Screener
CANSLIM-based stock screening with fundamental and technical analysis
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from src.config.constants import TREND_UP, TREND_DOWN, TREND_NEUTRAL
from src.utils.logger import setup_logger

logger = setup_logger("stock_screener", "stock_screener.log")


@dataclass
class FundamentalData:
    """Fundamental data for stock"""
    symbol: str
    eps_growth: float                  # YoY EPS growth %
    sales_growth: float                # YoY sales growth %
    profit_margin: float               # Net profit margin %
    roe: float                         # Return on equity %
    debt_to_equity: float              # Debt to equity ratio
    dividend_yield: float              # Dividend yield %
    current_ratio: float               # Current ratio
    earnings_date: Optional[str] = None


@dataclass
class TechnicalData:
    """Technical data for stock"""
    symbol: str
    price_52w_high: float              # 52-week high price
    current_price: float               # Current price
    price_52w_low: float               # 52-week low price
    days_from_52w_high: int            # Days from 52-week high
    rs_rating: float                   # Relative strength rating (0-100)
    avg_volume_20d: float              # 20-day average volume
    avg_volume_50d: float              # 50-day average volume
    volume_trend: str                  # UP, DOWN, NEUTRAL
    price_trend: str                   # UP, DOWN, NEUTRAL
    ma_50_distance: float              # % distance from 50-day MA
    ma_200_distance: float             # % distance from 200-day MA


@dataclass
class ScreenerScore:
    """Screening score breakdown"""
    symbol: str
    fundamental_score: float           # 0-3 points
    technical_score: float             # 0-3 points
    total_score: float                 # 0-6 points
    grade: str                         # A, B, C, F
    breakdown: Dict = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.symbol}: Grade {self.grade} ({self.total_score:.1f}/6.0)"


class CANSLIMScreener:
    """
    CANSLIM stock screener
    
    C: Current Quarterly Earnings
    A: Annual Earnings Growth
    N: New Products/Services
    S: Supply/Demand (Volume)
    L: Leader/Laggard (Relative Strength)
    I: Institutional Ownership
    M: Market Timing (Market Environment)
    """
    
    def __init__(self):
        """Initialize CANSLIM Screener"""
        logger.info("Initialized CANSLIMScreener")
    
    # ==================== FUNDAMENTAL ANALYSIS ====================
    
    def score_earnings_growth(self, fund_data: FundamentalData) -> Tuple[float, Dict]:
        """
        Score earnings growth (A & C in CANSLIM)
        
        Looks for:
        - Strong recent quarterly earnings
        - Strong annual earnings growth (25%+ YoY)
        
        Returns:
            Tuple of (score, breakdown)
        """
        score = 0
        breakdown = {}
        
        # Annual earnings growth (25%+ is good, 50%+ is great)
        if fund_data.eps_growth >= 50:
            score += 1.0
            breakdown['eps_growth_50plus'] = 1.0
        elif fund_data.eps_growth >= 25:
            score += 0.75
            breakdown['eps_growth_25plus'] = 0.75
        elif fund_data.eps_growth >= 15:
            score += 0.5
            breakdown['eps_growth_15plus'] = 0.5
        else:
            breakdown['eps_growth_low'] = 0
        
        logger.debug(f"Earnings growth score for {fund_data.symbol}: {score}")
        
        return score, breakdown
    
    def score_sales_growth(self, fund_data: FundamentalData) -> Tuple[float, Dict]:
        """
        Score sales growth
        
        Looks for:
        - Strong revenue growth (15%+ YoY)
        - Accelerating sales
        
        Returns:
            Tuple of (score, breakdown)
        """
        score = 0
        breakdown = {}
        
        # Sales growth (15%+ is minimum, 25%+ is good)
        if fund_data.sales_growth >= 25:
            score += 0.75
            breakdown['sales_growth_25plus'] = 0.75
        elif fund_data.sales_growth >= 15:
            score += 0.5
            breakdown['sales_growth_15plus'] = 0.5
        else:
            breakdown['sales_growth_low'] = 0
        
        # Profit margin (healthy margins show pricing power)
        if fund_data.profit_margin >= 15:
            score += 0.25
            breakdown['profit_margin_healthy'] = 0.25
        elif fund_data.profit_margin >= 10:
            score += 0.15
            breakdown['profit_margin_adequate'] = 0.15
        
        logger.debug(f"Sales growth score for {fund_data.symbol}: {score}")
        
        return score, breakdown
    
    def score_fundamentals(self, fund_data: FundamentalData) -> Tuple[float, Dict]:
        """
        Score fundamental health
        
        Looks for:
        - Good return on equity (15%+)
        - Reasonable debt levels
        - Strong balance sheet
        
        Returns:
            Tuple of (score, breakdown)
        """
        score = 0
        breakdown = {}
        
        # Return on equity (15%+ is good, 25%+ is excellent)
        if fund_data.roe >= 25:
            score += 0.5
            breakdown['roe_excellent'] = 0.5
        elif fund_data.roe >= 15:
            score += 0.3
            breakdown['roe_good'] = 0.3
        elif fund_data.roe >= 10:
            score += 0.1
            breakdown['roe_fair'] = 0.1
        else:
            breakdown['roe_low'] = 0
        
        # Debt to equity (less is better, < 1.0 is good)
        if fund_data.debt_to_equity < 0.5:
            score += 0.25
            breakdown['debt_low'] = 0.25
        elif fund_data.debt_to_equity < 1.0:
            score += 0.15
            breakdown['debt_moderate'] = 0.15
        elif fund_data.debt_to_equity >= 2.0:
            score -= 0.25  # Penalize high debt
            breakdown['debt_high'] = -0.25
        
        # Current ratio (1.5+ is healthy)
        if fund_data.current_ratio >= 1.5:
            score += 0.25
            breakdown['liquidity_strong'] = 0.25
        elif fund_data.current_ratio >= 1.0:
            score += 0.1
            breakdown['liquidity_adequate'] = 0.1
        
        logger.debug(f"Fundamentals score for {fund_data.symbol}: {score}")
        
        return score, breakdown
    
    def calculate_fundamental_score(
        self, 
        fund_data: FundamentalData
    ) -> Tuple[float, Dict]:
        """
        Calculate total fundamental score (max 3 points)
        
        Args:
            fund_data: FundamentalData object
        
        Returns:
            Tuple of (score, full_breakdown)
        """
        scores = {}
        breakdowns = {}
        
        # Earnings growth
        earn_score, earn_breakdown = self.score_earnings_growth(fund_data)
        scores['earnings'] = earn_score
        breakdowns.update(earn_breakdown)
        
        # Sales growth
        sales_score, sales_breakdown = self.score_sales_growth(fund_data)
        scores['sales'] = sales_score
        breakdowns.update(sales_breakdown)
        
        # Fundamentals
        fund_score, fund_breakdown = self.score_fundamentals(fund_data)
        scores['fundamentals'] = fund_score
        breakdowns.update(fund_breakdown)
        
        # Cap at 3 points
        total = min(sum(scores.values()), 3.0)
        
        return total, breakdowns
    
    # ==================== TECHNICAL ANALYSIS ====================
    
    def score_price_action(self, tech_data: TechnicalData) -> Tuple[float, Dict]:
        """
        Score price action and trend (L in CANSLIM)
        
        Looks for:
        - Price near 52-week high (within 25%)
        - Uptrend confirmed
        - Making new highs
        
        Returns:
            Tuple of (score, breakdown)
        """
        score = 0
        breakdown = {}
        
        # Distance from 52-week high
        distance_percent = (
            (tech_data.price_52w_high - tech_data.current_price) / 
            tech_data.current_price * 100
        )
        
        if distance_percent <= 5:  # Within 5% of high
            score += 0.75
            breakdown['price_near_high'] = 0.75
        elif distance_percent <= 15:  # Within 15% of high
            score += 0.5
            breakdown['price_moderate_high'] = 0.5
        elif distance_percent <= 25:  # Within 25% of high
            score += 0.25
            breakdown['price_fair_high'] = 0.25
        else:
            breakdown['price_far_high'] = 0
        
        # Uptrend confirmation
        if tech_data.price_trend == TREND_UP:
            score += 0.5
            breakdown['trend_up'] = 0.5
        elif tech_data.price_trend == TREND_DOWN:
            score -= 0.25
            breakdown['trend_down'] = -0.25
        
        logger.debug(f"Price action score for {tech_data.symbol}: {score}")
        
        return score, breakdown
    
    def score_relative_strength(self, tech_data: TechnicalData) -> Tuple[float, Dict]:
        """
        Score relative strength rating (L in CANSLIM)
        
        Looks for:
        - RS rating 70+ (top 30% of market)
        - RS rating 85+ (top 15% of market)
        - Outperforming market and sector
        
        Returns:
            Tuple of (score, breakdown)
        """
        score = 0
        breakdown = {}
        
        # RS rating (0-100)
        if tech_data.rs_rating >= 85:
            score += 0.75
            breakdown['rs_excellent'] = 0.75
        elif tech_data.rs_rating >= 70:
            score += 0.5
            breakdown['rs_good'] = 0.5
        elif tech_data.rs_rating >= 50:
            score += 0.25
            breakdown['rs_moderate'] = 0.25
        else:
            breakdown['rs_weak'] = 0
        
        logger.debug(f"RS rating score for {tech_data.symbol}: {score}")
        
        return score, breakdown
    
    def score_volume_trend(self, tech_data: TechnicalData) -> Tuple[float, Dict]:
        """
        Score volume and supply/demand (S in CANSLIM)
        
        Looks for:
        - Increasing volume
        - Volume >50% of 20-day average
        - Strong supply/demand
        
        Returns:
            Tuple of (score, breakdown)
        """
        score = 0
        breakdown = {}
        
        # Volume trend
        if tech_data.volume_trend == TREND_UP:
            score += 0.5
            breakdown['volume_increasing'] = 0.5
        elif tech_data.volume_trend == TREND_DOWN:
            score -= 0.25
            breakdown['volume_decreasing'] = -0.25
        
        # Volume relative to average
        if tech_data.avg_volume_20d > 0:
            volume_ratio = tech_data.avg_volume_50d / tech_data.avg_volume_20d
            if volume_ratio >= 1.2:  # 20% above average
                score += 0.5
                breakdown['volume_above_avg'] = 0.5
            elif volume_ratio >= 1.0:  # At or above average
                score += 0.25
                breakdown['volume_at_avg'] = 0.25
        
        logger.debug(f"Volume score for {tech_data.symbol}: {score}")
        
        return score, breakdown
    
    def score_moving_averages(self, tech_data: TechnicalData) -> Tuple[float, Dict]:
        """
        Score price position relative to moving averages
        
        Looks for:
        - Price above 50-day MA
        - Price above 200-day MA
        - Proper support structure
        
        Returns:
            Tuple of (score, breakdown)
        """
        score = 0
        breakdown = {}
        
        # 50-day MA
        if tech_data.ma_50_distance > 0:  # Above 50-day
            if tech_data.ma_50_distance <= 5:  # Close to MA
                score += 0.35
                breakdown['price_above_50ma_close'] = 0.35
            elif tech_data.ma_50_distance <= 15:  # Moderate distance
                score += 0.25
                breakdown['price_above_50ma_moderate'] = 0.25
        elif tech_data.ma_50_distance < -10:  # Below 50-day by >10%
            score -= 0.2
            breakdown['price_below_50ma'] = -0.2
        
        # 200-day MA
        if tech_data.ma_200_distance > 0:  # Above 200-day
            score += 0.4
            breakdown['price_above_200ma'] = 0.4
        elif tech_data.ma_200_distance < -15:  # Far below 200-day
            score -= 0.3
            breakdown['price_below_200ma'] = -0.3
        
        logger.debug(f"Moving average score for {tech_data.symbol}: {score}")
        
        return score, breakdown
    
    def calculate_technical_score(
        self,
        tech_data: TechnicalData
    ) -> Tuple[float, Dict]:
        """
        Calculate total technical score (max 3 points)
        
        Args:
            tech_data: TechnicalData object
        
        Returns:
            Tuple of (score, full_breakdown)
        """
        scores = {}
        breakdowns = {}
        
        # Price action
        price_score, price_breakdown = self.score_price_action(tech_data)
        scores['price_action'] = price_score
        breakdowns.update(price_breakdown)
        
        # Relative strength
        rs_score, rs_breakdown = self.score_relative_strength(tech_data)
        scores['relative_strength'] = rs_score
        breakdowns.update(rs_breakdown)
        
        # Volume
        volume_score, volume_breakdown = self.score_volume_trend(tech_data)
        scores['volume'] = volume_score
        breakdowns.update(volume_breakdown)
        
        # Moving averages
        ma_score, ma_breakdown = self.score_moving_averages(tech_data)
        scores['moving_averages'] = ma_score
        breakdowns.update(ma_breakdown)
        
        # Cap at 3 points
        total = min(sum(scores.values()), 3.0)
        
        return total, breakdowns
    
    # ==================== OVERALL SCREENING ====================
    
    def screen_stock(
        self,
        fund_data: FundamentalData,
        tech_data: TechnicalData,
        market_environment: str = "A"
    ) -> ScreenerScore:
        """
        Screen stock using CANSLIM methodology
        
        Args:
            fund_data: FundamentalData object
            tech_data: TechnicalData object
            market_environment: Market environment (A-E)
        
        Returns:
            ScreenerScore object with grades
        """
        logger.info(f"Screening stock: {fund_data.symbol}")
        
        # Calculate scores
        fund_score, fund_breakdown = self.calculate_fundamental_score(fund_data)
        tech_score, tech_breakdown = self.calculate_technical_score(tech_data)
        
        # Combine breakdowns
        full_breakdown = {
            'fundamental': fund_breakdown,
            'technical': tech_breakdown
        }
        
        # Total score (0-6)
        total_score = fund_score + tech_score
        
        # Grade assignment
        if total_score >= 5.0:
            grade = "A"
        elif total_score >= 4.0:
            grade = "B"
        elif total_score >= 3.0:
            grade = "C"
        else:
            grade = "F"
        
        # Create result
        result = ScreenerScore(
            symbol=fund_data.symbol,
            fundamental_score=fund_score,
            technical_score=tech_score,
            total_score=total_score,
            grade=grade,
            breakdown=full_breakdown
        )
        
        logger.info(f"Screen result: {result}")
        
        return result
    
    def batch_screen(
        self,
        stocks: List[Tuple[FundamentalData, TechnicalData]],
        market_environment: str = "A"
    ) -> List[ScreenerScore]:
        """
        Screen multiple stocks
        
        Args:
            stocks: List of (FundamentalData, TechnicalData) tuples
            market_environment: Market environment
        
        Returns:
            List of ScreenerScore objects
        """
        logger.info(f"Batch screening {len(stocks)} stocks")
        
        results = []
        for fund_data, tech_data in stocks:
            score = self.screen_stock(
                fund_data, tech_data, market_environment
            )
            results.append(score)
        
        return results
    
    def get_screen_summary(
        self,
        results: List[ScreenerScore]
    ) -> Dict:
        """
        Get summary of screening results
        
        Args:
            results: List of ScreenerScore objects
        
        Returns:
            Summary dictionary
        """
        if not results:
            return {"total": 0, "grades": {}}
        
        # Grade distribution
        grades = {"A": 0, "B": 0, "C": 0, "F": 0}
        for result in results:
            grades[result.grade] += 1
        
        # Statistics
        scores = [r.total_score for r in results]
        
        return {
            "total_screened": len(results),
            "grade_distribution": grades,
            "average_score": np.mean(scores),
            "median_score": np.median(scores),
            "best_score": np.max(scores),
            "worst_score": np.min(scores),
            "top_picks": sorted(results, key=lambda x: x.total_score, reverse=True)[:5]
        }


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*70)
    print("MODULE 2: STOCK SCREENER (CANSLIM) - TEST")
    print("="*70)
    
    screener = CANSLIMScreener()
    
    # Test Case 1: High-quality growth stock
    print("\n\n🔍 TEST CASE 1: High-Quality Growth Stock (NVDA-like)")
    print("-" * 70)
    
    fund1 = FundamentalData(
        symbol="EXAMPLE1",
        eps_growth=85,          # Strong EPS growth
        sales_growth=45,        # Strong revenue growth
        profit_margin=28,       # Excellent margins
        roe=32,                 # Excellent ROE
        debt_to_equity=0.3,     # Low debt
        dividend_yield=0.0,     # Tech growth stock
        current_ratio=2.1       # Strong balance sheet
    )
    
    tech1 = TechnicalData(
        symbol="EXAMPLE1",
        price_52w_high=250.00,
        current_price=240.00,
        price_52w_low=180.00,
        days_from_52w_high=15,
        rs_rating=92,           # Very strong RS
        avg_volume_20d=50000000,
        avg_volume_50d=55000000,
        volume_trend=TREND_UP,
        price_trend=TREND_UP,
        ma_50_distance=3.5,     # Above 50-day MA
        ma_200_distance=8.2     # Above 200-day MA
    )
    
    result1 = screener.screen_stock(fund1, tech1, "A")
    print(result1)
    print(f"Breakdown: {result1.breakdown}")
    
    # Test Case 2: Moderate quality stock
    print("\n\n🔍 TEST CASE 2: Moderate Quality Stock")
    print("-" * 70)
    
    fund2 = FundamentalData(
        symbol="EXAMPLE2",
        eps_growth=20,
        sales_growth=12,
        profit_margin=12,
        roe=16,
        debt_to_equity=0.8,
        dividend_yield=1.5,
        current_ratio=1.3
    )
    
    tech2 = TechnicalData(
        symbol="EXAMPLE2",
        price_52w_high=100.00,
        current_price=92.00,
        price_52w_low=75.00,
        days_from_52w_high=45,
        rs_rating=65,
        avg_volume_20d=5000000,
        avg_volume_50d=4800000,
        volume_trend=TREND_NEUTRAL,
        price_trend=TREND_UP,
        ma_50_distance=1.2,
        ma_200_distance=5.0
    )
    
    result2 = screener.screen_stock(fund2, tech2, "B")
    print(result2)
    
    # Test Case 3: Lower quality stock
    print("\n\n🔍 TEST CASE 3: Lower Quality Stock")
    print("-" * 70)
    
    fund3 = FundamentalData(
        symbol="EXAMPLE3",
        eps_growth=5,
        sales_growth=3,
        profit_margin=5,
        roe=8,
        debt_to_equity=1.8,
        dividend_yield=4.2,
        current_ratio=1.0
    )
    
    tech3 = TechnicalData(
        symbol="EXAMPLE3",
        price_52w_high=50.00,
        current_price=40.00,
        price_52w_low=35.00,
        days_from_52w_high=120,
        rs_rating=35,
        avg_volume_20d=2000000,
        avg_volume_50d=1800000,
        volume_trend=TREND_DOWN,
        price_trend=TREND_DOWN,
        ma_50_distance=-5.0,
        ma_200_distance=-12.0
    )
    
    result3 = screener.screen_stock(fund3, tech3, "C")
    print(result3)
    
    # Batch screening
    print("\n\n" + "="*70)
    print("BATCH SCREENING RESULTS")
    print("="*70)
    
    stocks = [(fund1, tech1), (fund2, tech2), (fund3, tech3)]
    batch_results = screener.batch_screen(stocks, "A")
    
    summary = screener.get_screen_summary(batch_results)
    
    print(f"\nTotal Screened: {summary['total_screened']}")
    print(f"Grade Distribution: {summary['grade_distribution']}")
    print(f"Average Score: {summary['average_score']:.2f}/6.0")
    print(f"Best Score: {summary['best_score']:.2f}/6.0")
    print(f"Worst Score: {summary['worst_score']:.2f}/6.0")
    
    print("\nTop Picks:")
    for i, pick in enumerate(summary['top_picks'], 1):
        print(f"  {i}. {pick.symbol}: Grade {pick.grade} ({pick.total_score:.1f}/6.0)")
    
    print("\n✅ Module 2: Stock Screener - Testing Complete!")
