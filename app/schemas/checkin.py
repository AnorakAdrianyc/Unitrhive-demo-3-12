"""Check-in and Activity Pydantic models for UniThrive."""

from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class ActivityType(str, Enum):
    """Types of activities that can be logged."""
    
    COURSE = "course"
    SKILL = "skill"
    EXERCISE = "exercise"
    SOCIAL = "social"
    EVENT = "event"


class RingTag(str, Enum):
    """Tags indicating which ring the activity contributes to."""
    
    MENTAL = "mental"
    PSYCHOLOGICAL = "psychological"
    PHYSICAL = "physical"


class CheckInBase(BaseModel):
    """Base check-in model with common attributes."""
    
    mood_score: int = Field(..., ge=1, le=5, description="Mood rating from 1-5")
    stress_score: int = Field(..., ge=1, le=5, description="Stress level from 1-5")
    sleep_hours: float = Field(..., ge=0, le=24, description="Hours of sleep")
    exercise_minutes: int = Field(..., ge=0, description="Minutes of exercise")
    social_interactions: int = Field(..., ge=0, description="Number of social interactions")
    notes_text: Optional[str] = Field(None, max_length=1000)


class CheckInCreate(CheckInBase):
    """Model for creating a new check-in."""
    
    user_id: str


class CheckIn(CheckInBase):
    """Complete check-in model with ID and timestamp."""
    
    id: str
    user_id: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ActivityRecordBase(BaseModel):
    """Base activity record model."""
    
    type: ActivityType
    duration_minutes: int = Field(..., ge=0)
    tag_ring: RingTag
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)


class ActivityRecordCreate(ActivityRecordBase):
    """Model for creating a new activity record."""
    
    user_id: str
    date: date


class ActivityRecord(ActivityRecordBase):
    """Complete activity record model."""
    
    id: str
    user_id: str
    date: date
    created_at: datetime
    
    class Config:
        from_attributes = True


class CheckInWithActivities(BaseModel):
    """Combined check-in and activities for a day."""
    
    check_in: Optional[CheckIn] = None
    activities: List[ActivityRecord] = Field(default_factory=list)
    date: date


class DailySummary(BaseModel):
    """Summary of a user's day."""
    
    date: date
    check_in_count: int
    activity_count: int
    total_activity_minutes: int
    mood_average: Optional[float] = None
    stress_average: Optional[float] = None
    sleep_average: Optional[float] = None


class CheckInHistoryResponse(BaseModel):
    """Response model for check-in history."""
    
    user_id: str
    check_ins: List[CheckIn]
    total_count: int


class ActivityHistoryResponse(BaseModel):
    """Response model for activity history."""
    
    user_id: str
    activities: List[ActivityRecord]
    total_count: int
