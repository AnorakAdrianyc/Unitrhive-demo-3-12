"""3-Ring Wellbeing Scoring Pydantic models for UniThrive."""

from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class RingType(str, Enum):
    """The three rings of wellbeing."""
    
    MENTAL = "mental"
    PSYCHOLOGICAL = "psychological"
    PHYSICAL = "physical"


class TrendDirection(str, Enum):
    """Trend direction for ring scores."""
    
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


class RingScore(BaseModel):
    """Score for a single ring (0-1 scale)."""
    
    ring_type: RingType
    score: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime
    

class RingScores(BaseModel):
    """All three ring scores."""
    
    mental: float = Field(..., ge=0.0, le=1.0)
    psychological: float = Field(..., ge=0.0, le=1.0)
    physical: float = Field(..., ge=0.0, le=1.0)
    calculated_at: datetime


class RingTrends(BaseModel):
    """Trend directions for each ring."""
    
    mental: TrendDirection
    psychological: TrendDirection
    physical: TrendDirection
    period_days: int = 7


class DailyRingScore(BaseModel):
    """Daily ring scores for a user."""
    
    id: str
    user_id: str
    date: date
    mental_score: float = Field(..., ge=0.0, le=1.0)
    psychological_score: float = Field(..., ge=0.0, le=1.0)
    physical_score: float = Field(..., ge=0.0, le=1.0)
    calculated_at: datetime
    
    class Config:
        from_attributes = True


class WeeklySummary(BaseModel):
    """Weekly summary of all three rings."""
    
    id: str
    user_id: str
    week_start: date
    week_end: date
    mental_summary: str
    psych_summary: str
    physical_summary: str
    spotlight_opportunity: str
    achievement_badge: Optional[str] = None
    ring_scores: RingScores
    created_at: datetime
    
    class Config:
        from_attributes = True


class AchievementBadge(str, Enum):
    """Achievement badges that can be awarded."""
    
    BALANCE_SEEKER = "Balance Seeker"
    STRESS_FIGHTER = "Stress Fighter"
    COMEBACK_KID = "Comeback Kid"
    SCHOLAR = "Scholar"
    MINDFUL_MASTER = "Mindful Master"
    FITNESS_CHAMPION = "Fitness Champion"
    SLEEP_GUARDIAN = "Sleep Guardian"
    SOCIAL_BUTTERFLY = "Social Butterfly"


class RingHistoryResponse(BaseModel):
    """Response model for ring score history."""
    
    user_id: str
    history: List[DailyRingScore]
    trends: RingTrends


class TodayRingResponse(BaseModel):
    """Response model for today's ring scores."""
    
    user_id: str
    date: date
    ring_scores: RingScores
    trend_since_last_week: Optional[RingTrends] = None


class RingSummaryComponent(BaseModel):
    """Component of a ring summary (for dashboard display)."""
    
    ring_type: RingType
    score: float
    trend: TrendDirection
    key_metric: str
    recommendation: Optional[str] = None
