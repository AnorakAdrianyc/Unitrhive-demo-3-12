"""Recommendations and Alerts Pydantic models for UniThrive."""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class OpportunityType(str, Enum):
    """Types of opportunities."""
    
    WORKSHOP = "workshop"
    EVENT = "event"
    COUNSELLING = "counselling"
    COMMUNITY = "community"
    COURSE = "course"
    ACTIVITY = "activity"


class Opportunity(BaseModel):
    """An opportunity available to students."""
    
    id: str
    title: str = Field(..., max_length=200)
    type: OpportunityType
    description: Optional[str] = Field(None, max_length=1000)
    tags: List[str] = Field(default_factory=list)
    campus: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    registration_link: Optional[str] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True


class Recommendation(BaseModel):
    """A personalized recommendation for a user."""
    
    id: str
    user_id: str
    opportunity_id: str
    opportunity: Optional[Opportunity] = None
    ring_target: str = Field(..., pattern=r"^(mental|psychological|physical)$")
    score: float = Field(..., ge=0.0, le=1.0)
    explanation: str = Field(..., max_length=500)
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_viewed: bool = False
    is_accepted: Optional[bool] = None
    
    class Config:
        from_attributes = True


class RiskLevel(str, Enum):
    """Risk levels for alerts."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskAlert(BaseModel):
    """A risk alert for a user."""
    
    id: str
    user_id: str
    risk_level: RiskLevel
    reason: str = Field(..., max_length=500)
    triggered_at: datetime
    escalated_to_counselor: bool = False
    counselor_id: Optional[str] = None
    is_acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    suggested_actions: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class RecommendationPreview(BaseModel):
    """Preview of a recommendation for dashboard display."""
    
    id: str
    title: str
    ring_target: str
    explanation: str


class DashboardSummary(BaseModel):
    """Summary data for the dashboard."""
    
    user_id: str
    ring_scores: dict
    streak_days: int = 0
    unread_alerts: int = 0
    recommendation_preview: List[RecommendationPreview] = Field(default_factory=list)


class AlertAcknowledgeRequest(BaseModel):
    """Request model for acknowledging an alert."""
    
    user_id: str
    alert_id: str


class AlertAcknowledgeResponse(BaseModel):
    """Response model for acknowledging an alert."""
    
    success: bool
    message: str
    alert: Optional[RiskAlert] = None


class RecommendationListResponse(BaseModel):
    """Response model for recommendation list."""
    
    user_id: str
    recommendations: List[Recommendation]
    total_count: int
    unread_count: int


class AlertListResponse(BaseModel):
    """Response model for alert list."""
    
    user_id: str
    alerts: List[RiskAlert]
    total_count: int
    unread_count: int
    high_risk_count: int


class OpportunityListResponse(BaseModel):
    """Response model for opportunity list."""
    
    opportunities: List[Opportunity]
    total_count: int
    filtered_by_campus: Optional[str] = None
    filtered_by_type: Optional[OpportunityType] = None
