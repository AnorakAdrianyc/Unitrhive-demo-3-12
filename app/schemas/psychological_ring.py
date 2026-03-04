"""Psychological Ring Pydantic models for UniThrive.

This module defines schemas for self-discovery, emotional resilience,
risk analysis, and neurocognitive tracking.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class AssessmentType(str, Enum):
    """Types of personality assessments."""
    
    MBTI = "mbti"
    BIG_FIVE = "big_five"
    ENNEAGRAM = "enneagram"
    STRENGTHS_FINDER = "strengths_finder"


class MBTIType(str, Enum):
    """MBTI personality types."""
    
    ISTJ = "ISTJ"
    ISFJ = "ISFJ"
    INFJ = "INFJ"
    INTJ = "INTJ"
    ISTP = "ISTP"
    ISFP = "ISFP"
    INFP = "INFP"
    INTP = "INTP"
    ESTP = "ESTP"
    ESFP = "ESFP"
    ENFP = "ENFP"
    ENTP = "ENTP"
    ESTJ = "ESTJ"
    ESFJ = "ESFJ"
    ENFJ = "ENFJ"
    ENTJ = "ENTJ"


class NeuroTestType(str, Enum):
    """Types of neurocognitive tests."""
    
    MEMORY = "memory"
    REACTION_TIME = "reaction_time"
    ATTENTION = "attention"
    COGNITIVE_SPEED = "cognitive_speed"
    EXECUTIVE_FUNCTION = "executive_function"


class RiskFactorType(str, Enum):
    """Types of risk factors."""
    
    STRESS = "stress"
    MOOD = "mood"
    SLEEP = "sleep"
    SOCIAL = "social"
    ACADEMIC = "academic"
    BEHAVIORAL = "behavioral"


class RiskSeverity(str, Enum):
    """Severity levels for risk."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PersonalityAssessment(BaseModel):
    """Personality assessment results."""
    
    id: str
    user_id: str
    assessment_type: AssessmentType
    results: Dict[str, Any]
    mbti_type: Optional[MBTIType] = None
    traits: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    study_preferences: List[str] = Field(default_factory=list)
    completed_at: datetime
    
    class Config:
        from_attributes = True


class SelfDiscoveryTest(BaseModel):
    """Self-discovery test record."""
    
    id: str
    user_id: str
    test_id: str
    test_name: str
    responses: Dict[str, Any]
    insights_generated: List[str] = Field(default_factory=list)
    reflection_notes: Optional[str] = None
    completed_at: datetime
    
    class Config:
        from_attributes = True


class BehavioralRiskProfile(BaseModel):
    """Behavioral risk profile."""
    
    id: str
    user_id: str
    risk_factors: List[Dict[str, Any]] = Field(default_factory=list)
    overall_risk_score: float = Field(..., ge=0.0, le=10.0)
    risk_level: RiskSeverity
    analysis_date: date
    recommendations: List[str] = Field(default_factory=list)
    contributing_factors: List[str] = Field(default_factory=list)
    protective_factors: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class LearningPattern(BaseModel):
    """Learning pattern insights."""
    
    id: str
    user_id: str
    pattern_type: str
    description: str
    strengths: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    suggested_strategies: List[str] = Field(default_factory=list)
    detected_at: datetime
    
    class Config:
        from_attributes = True


class NeurocognitiveTest(BaseModel):
    """Neurocognitive test results."""
    
    id: str
    user_id: str
    test_type: NeuroTestType
    score: float
    percentile: Optional[int] = Field(None, ge=0, le=100)
    baseline_comparison: Optional[float] = None  # percentage change from baseline
    test_date: date
    duration_seconds: Optional[int] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class LongTermMetric(BaseModel):
    """Long-term health metric tracking."""
    
    id: str
    user_id: str
    metric_type: str  # heart_rate, reaction_speed, cognitive_perf, etc.
    value: float
    unit: str
    recorded_at: datetime
    trend_direction: Optional[str] = None  # improving, stable, declining
    
    class Config:
        from_attributes = True


class PsychologicalAlert(BaseModel):
    """Psychological risk alert record."""
    
    id: str
    user_id: str
    alert_type: str
    severity: RiskSeverity
    description: str
    triggered_by: List[str] = Field(default_factory=list)
    status: str = "active"  # active, acknowledged, resolved
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PsychologicalRingSummary(BaseModel):
    """Summary of Psychological Ring for a user."""
    
    user_id: str
    period_start: date
    period_end: date
    emotional_stability_score: float = Field(..., ge=0.0, le=1.0)
    self_awareness_score: float = Field(..., ge=0.0, le=1.0)
    cognitive_health_score: float = Field(..., ge=0.0, le=1.0)
    risk_mitigation_score: float = Field(..., ge=0.0, le=1.0)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    mbti_type: Optional[str] = None
    tests_completed: int
    active_alerts: int
    avg_neuro_percentile: Optional[float] = None
    risk_level: Optional[float] = None
    recommendations: List[str] = Field(default_factory=list)


class PersonalityAssessmentCreate(BaseModel):
    """Request model for submitting personality assessment."""
    
    user_id: str
    assessment_type: AssessmentType
    results: Dict[str, Any]
    mbti_type: Optional[MBTIType] = None


class SelfDiscoveryTestCreate(BaseModel):
    """Request model for completing self-discovery test."""
    
    user_id: str
    test_id: str
    test_name: str
    responses: Dict[str, Any]
    reflection_notes: Optional[str] = None


class NeurocognitiveTestCreate(BaseModel):
    """Request model for submitting neurocognitive test."""
    
    user_id: str
    test_type: NeuroTestType
    score: float
    percentile: Optional[int] = None
    duration_seconds: Optional[int] = None


class LongTermMetricCreate(BaseModel):
    """Request model for recording health metric."""
    
    user_id: str
    metric_type: str
    value: float
    unit: str


class RiskAnalysisRequest(BaseModel):
    """Request model for triggering risk analysis."""
    
    user_id: str
    analysis_period_days: int = Field(default=7, ge=1, le=30)
