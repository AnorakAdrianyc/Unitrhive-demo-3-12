"""AI Chat and Time Management Pydantic models for UniThrive."""

from datetime import datetime, time, date, timedelta
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Roles for chat messages."""
    
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class RiskLevel(str, Enum):
    """Risk levels detected in chat."""
    
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ChatMessage(BaseModel):
    """Single chat message."""
    
    role: MessageRole
    content: str = Field(..., max_length=2000)
    timestamp: datetime
    risk_flags: List[str] = Field(default_factory=list)
    detected_risk_level: RiskLevel = RiskLevel.NONE


class ChatSession(BaseModel):
    """Complete chat session."""
    
    session_id: str
    user_id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    summary: Optional[str] = None
    detected_risk_level: RiskLevel = RiskLevel.NONE
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Request model for sending a chat message."""
    
    user_id: str
    message: str = Field(..., max_length=2000)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat."""
    
    session_id: str
    response: str
    detected_risk_level: RiskLevel
    risk_flags: List[str]
    suggestions: List[str] = Field(default_factory=list)
    timestamp: datetime


class StudyBlock(BaseModel):
    """A block of time for studying."""
    
    start_time: time
    end_time: time
    subject: str
    priority: int = Field(..., ge=1, le=5)
    break_after: bool = True


class ExamScheduleItem(BaseModel):
    """Item in an exam schedule."""
    
    exam_name: str
    exam_date: date
    subject: str
    priority: int = Field(..., ge=1, le=5)
    preparation_start_date: date
    recommended_daily_study_hours: float


class BreakReminder(BaseModel):
    """Reminder to take a break."""
    
    after_minutes: int
    break_duration_minutes: int
    reminder_type: str = Field(..., pattern=r"^(movement|mindfulness|hydration|eye_rest)$")


class TimePlan(BaseModel):
    """Complete time management plan."""
    
    plan_id: str
    user_id: str
    created_at: datetime
    exam_schedule: List[ExamScheduleItem] = Field(default_factory=list)
    daily_study_blocks: List[StudyBlock] = Field(default_factory=list)
    break_reminders: List[BreakReminder] = Field(default_factory=list)
    workload_balance_score: float = Field(..., ge=0.0, le=1.0)
    estimated_productivity_score: float = Field(..., ge=0.0, le=1.0)


class TimePlanRequest(BaseModel):
    """Request model for generating a time plan."""
    
    user_id: str
    upcoming_exams: List[ExamScheduleItem] = Field(default_factory=list)
    preferred_study_hours_per_day: float = Field(4.0, ge=0.0, le=12.0)
    preferred_productive_times: List[str] = Field(default_factory=list)  # e.g., ["morning", "evening"]
    constraints: List[str] = Field(default_factory=list)


class TimePlanResponse(BaseModel):
    """Response model for time plan."""
    
    plan: TimePlan
    recommendations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ScheduleOptimizationRequest(BaseModel):
    """Request model for optimizing an existing schedule."""
    
    user_id: str
    current_plan_id: str
    issues: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)


class TimeManagementSuggestion(BaseModel):
    """A personalized time management suggestion."""
    
    suggestion_type: str
    title: str
    description: str
    priority: int = Field(..., ge=1, le=5)
    based_on_data: List[str] = Field(default_factory=list)


class TimeManagementSuggestionsResponse(BaseModel):
    """Response model for time management suggestions."""
    
    user_id: str
    suggestions: List[TimeManagementSuggestion]
    overall_efficiency_score: float = Field(..., ge=0.0, le=1.0)
    areas_for_improvement: List[str] = Field(default_factory=list)
