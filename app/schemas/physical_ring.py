"""Physical Ring Pydantic models for UniThrive.

This module defines schemas for time management, sleep tracking,
fitness routines, and wearable device integration.
"""

from datetime import datetime, date, time, timedelta
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class DayOfWeek(str, Enum):
    """Days of the week for scheduling."""
    
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class FitnessType(str, Enum):
    """Types of fitness activities."""
    
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    SPORTS = "sports"
    MIND_BODY = "mind_body"


class ExerciseIntensity(str, Enum):
    """Intensity levels for exercise."""
    
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class DeviceType(str, Enum):
    """Types of wearable devices."""
    
    SMARTWATCH = "smartwatch"
    FITNESS_TRACKER = "fitness_tracker"
    NEUROFEEDBACK_HEADBAND = "neurofeedback_headband"
    SMART_RING = "smart_ring"
    HEART_RATE_MONITOR = "heart_rate_monitor"
    SLEEP_TRACKER = "sleep_tracker"


class SleepStage(str, Enum):
    """Stages of sleep."""
    
    AWAKE = "awake"
    LIGHT = "light"
    DEEP = "deep"
    REM = "rem"


class TimeManagementBehavior(BaseModel):
    """Daily time management behavior tracking."""
    
    id: str
    user_id: str
    date: date
    schedule_adherence: float = Field(..., ge=0.0, le=1.0)
    procrastination_instances: int = Field(default=0, ge=0)
    productive_hours: float = Field(..., ge=0.0, le=24.0)
    distraction_score: float = Field(..., ge=0.0, le=1.0)  # lower is better
    tasks_completed: int = Field(default=0, ge=0)
    tasks_planned: int = Field(default=0, ge=0)
    focus_sessions_count: int = Field(default=0, ge=0)
    avg_focus_duration_minutes: Optional[float] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class DailyActivity(BaseModel):
    """Daily physical activity tracking."""
    
    id: str
    user_id: str
    date: date
    steps: int = Field(default=0, ge=0)
    active_minutes: int = Field(default=0, ge=0)
    sedentary_hours: float = Field(default=0.0, ge=0.0)
    movement_breaks_taken: int = Field(default=0, ge=0)
    distance_km: Optional[float] = None
    calories_burned: Optional[int] = None
    floors_climbed: Optional[int] = None
    
    class Config:
        from_attributes = True


class SleepRecord(BaseModel):
    """Sleep tracking record."""
    
    id: str
    user_id: str
    date: date
    bed_time: time
    wake_time: time
    total_hours: float = Field(..., ge=0.0, le=24.0)
    sleep_quality: int = Field(..., ge=1, le=5)
    rem_minutes: Optional[int] = Field(None, ge=0)
    deep_minutes: Optional[int] = Field(None, ge=0)
    light_minutes: Optional[int] = Field(None, ge=0)
    awake_minutes: Optional[int] = Field(None, ge=0)
    position_changes: Optional[int] = None
    sleep_stages: Optional[List[dict]] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class FitnessRoutine(BaseModel):
    """Fitness routine definition."""
    
    id: str
    user_id: str
    name: str = Field(..., max_length=100)
    type: FitnessType
    description: Optional[str] = None
    scheduled_days: List[DayOfWeek] = Field(default_factory=list)
    target_duration_minutes: int = Field(..., ge=0)
    target_intensity: ExerciseIntensity
    exercises: List[str] = Field(default_factory=list)
    created_at: datetime
    is_active: bool = True
    streak_count: int = Field(default=0, ge=0)
    total_sessions_completed: int = Field(default=0, ge=0)
    
    class Config:
        from_attributes = True


class ExerciseSession(BaseModel):
    """Individual exercise session record."""
    
    id: str
    user_id: str
    routine_id: Optional[str] = None
    date: date
    start_time: time
    end_time: time
    duration_minutes: int = Field(..., ge=0)
    intensity: ExerciseIntensity
    calories_burned: Optional[int] = None
    heart_rate_avg: Optional[int] = Field(None, ge=0)
    heart_rate_max: Optional[int] = Field(None, ge=0)
    exercises_completed: List[str] = Field(default_factory=list)
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class WearableData(BaseModel):
    """Raw data from wearable device."""
    
    id: str
    user_id: str
    device_id: str
    timestamp: datetime
    heart_rate: Optional[int] = Field(None, ge=0)
    steps: Optional[int] = Field(None, ge=0)
    sleep_stage: Optional[SleepStage] = None
    vo2_max_estimate: Optional[float] = None
    breathing_rate: Optional[float] = None
    stress_level: Optional[int] = Field(None, ge=0, le=100)
    blood_oxygen: Optional[float] = Field(None, ge=0, le=100)
    
    class Config:
        from_attributes = True


class DeviceIntegration(BaseModel):
    """Wearable device integration record."""
    
    id: str
    user_id: str
    device_id: str
    device_name: str
    device_type: DeviceType
    manufacturer: Optional[str] = None
    connection_status: str = "connected"  # connected, disconnected, error
    last_sync: Optional[datetime] = None
    data_points_count: int = Field(default=0, ge=0)
    api_token: Optional[str] = None  # encrypted in production
    created_at: datetime
    
    class Config:
        from_attributes = True


class PhysicalRingSummary(BaseModel):
    """Summary of Physical Ring for a user."""
    
    user_id: str
    period_start: date
    period_end: date
    time_management_score: float = Field(..., ge=0.0, le=1.0)
    activity_score: float = Field(..., ge=0.0, le=1.0)
    sleep_score: float = Field(..., ge=0.0, le=1.0)
    fitness_score: float = Field(..., ge=0.0, le=1.0)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    avg_daily_steps: int
    avg_sleep_hours: float
    weekly_workouts: int
    schedule_adherence_rate: float
    connected_devices: int
    recommendations: List[str] = Field(default_factory=list)


class TimeManagementCreate(BaseModel):
    """Request model for logging time management."""
    
    user_id: str
    date: date
    schedule_adherence: float = Field(..., ge=0.0, le=1.0)
    productive_hours: float = Field(..., ge=0.0, le=24.0)
    procrastination_instances: int = Field(default=0, ge=0)
    tasks_completed: int = Field(default=0, ge=0)
    tasks_planned: int = Field(default=0, ge=0)


class DailyActivityCreate(BaseModel):
    """Request model for recording daily activity."""
    
    user_id: str
    date: date
    steps: int = Field(default=0, ge=0)
    active_minutes: int = Field(default=0, ge=0)
    sedentary_hours: float = Field(default=0.0, ge=0.0)
    movement_breaks_taken: int = Field(default=0, ge=0)


class SleepRecordCreate(BaseModel):
    """Request model for logging sleep."""
    
    user_id: str
    date: date
    bed_time: time
    wake_time: time
    sleep_quality: int = Field(..., ge=1, le=5)
    rem_minutes: Optional[int] = None
    deep_minutes: Optional[int] = None


class FitnessRoutineCreate(BaseModel):
    """Request model for creating fitness routine."""
    
    user_id: str
    name: str
    type: FitnessType
    scheduled_days: List[DayOfWeek] = Field(default_factory=list)
    target_duration_minutes: int = Field(..., ge=0)
    target_intensity: ExerciseIntensity


class ExerciseSessionCreate(BaseModel):
    """Request model for logging exercise session."""
    
    user_id: str
    routine_id: Optional[str] = None
    date: date
    start_time: time
    duration_minutes: int = Field(..., ge=0)
    intensity: ExerciseIntensity
    exercises_completed: List[str] = Field(default_factory=list)


class DeviceConnectRequest(BaseModel):
    """Request model for connecting wearable device."""
    
    user_id: str
    device_name: str
    device_type: DeviceType
    manufacturer: Optional[str] = None


class WearableDataSubmit(BaseModel):
    """Request model for submitting wearable data."""
    
    user_id: str
    device_id: str
    timestamp: datetime
    heart_rate: Optional[int] = None
    steps: Optional[int] = None
    sleep_stage: Optional[SleepStage] = None
    stress_level: Optional[int] = None
