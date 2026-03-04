"""Mental Ring Pydantic models for UniThrive.

This module defines schemas for tracking intellectual growth including
course engagement, workshop attendance, skill development, and academic projects.
"""

from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class SkillCategory(str, Enum):
    """Categories of skills."""
    
    LANGUAGE = "language"
    CODING = "coding"
    DESIGN = "design"
    RESEARCH = "research"
    COMMUNICATION = "communication"
    LEADERSHIP = "leadership"
    ANALYTICS = "analytics"
    OTHER = "other"


class ProjectStatus(str, Enum):
    """Status of academic projects."""
    
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class CourseEngagement(BaseModel):
    """Course engagement tracking."""
    
    id: str
    user_id: str
    course_id: str
    course_name: str = Field(..., max_length=200)
    attendance_rate: float = Field(..., ge=0.0, le=1.0)
    assignment_completion: float = Field(..., ge=0.0, le=1.0)
    participation_score: float = Field(..., ge=0.0, le=1.0)
    current_grade: Optional[str] = None
    last_updated: datetime
    
    class Config:
        from_attributes = True


class WorkshopAttendance(BaseModel):
    """Workshop attendance record."""
    
    id: str
    user_id: str
    workshop_id: str
    title: str = Field(..., max_length=200)
    date: date
    duration_minutes: int = Field(..., ge=0)
    skills_gained: List[str] = Field(default_factory=list)
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class SkillDevelopment(BaseModel):
    """Skill development tracking."""
    
    id: str
    user_id: str
    skill_name: str = Field(..., max_length=100)
    category: SkillCategory
    proficiency_level: int = Field(..., ge=1, le=10)
    hours_invested: int = Field(..., ge=0)
    certifications: List[str] = Field(default_factory=list)
    started_date: date
    last_practiced: Optional[date] = None
    goal_level: Optional[int] = Field(None, ge=1, le=10)
    
    class Config:
        from_attributes = True


class AcademicProject(BaseModel):
    """Academic project participation."""
    
    id: str
    user_id: str
    project_id: str
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    role: str = Field(..., max_length=100)
    start_date: date
    end_date: Optional[date] = None
    status: ProjectStatus
    outcomes: List[str] = Field(default_factory=list)
    collaborators: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class LearningGoal(BaseModel):
    """Learning goal setting."""
    
    id: str
    user_id: str
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    target_date: date
    progress_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    related_ring: str = Field(default="mental")
    milestones: List[str] = Field(default_factory=list)
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MentalRingSummary(BaseModel):
    """Summary of Mental Ring for a user."""
    
    user_id: str
    period_start: date
    period_end: date
    course_engagement_avg: float = Field(..., ge=0.0, le=1.0)
    skills_count: int
    avg_skill_proficiency: float = Field(..., ge=1.0, le=10.0)
    workshops_attended: int
    active_projects: int
    completed_projects: int
    learning_goals_active: int
    learning_goals_completed: int
    overall_score: float = Field(..., ge=0.0, le=1.0)
    recommendations: List[str] = Field(default_factory=list)


class CourseEngagementCreate(BaseModel):
    """Request model for creating course engagement."""
    
    user_id: str
    course_id: str
    course_name: str
    attendance_rate: float = Field(..., ge=0.0, le=1.0)
    assignment_completion: float = Field(..., ge=0.0, le=1.0)
    participation_score: float = Field(..., ge=0.0, le=1.0)


class WorkshopAttendanceCreate(BaseModel):
    """Request model for recording workshop attendance."""
    
    user_id: str
    workshop_id: str
    title: str
    date: date
    duration_minutes: int = Field(..., ge=0)
    skills_gained: List[str] = Field(default_factory=list)


class SkillDevelopmentCreate(BaseModel):
    """Request model for adding skill development."""
    
    user_id: str
    skill_name: str
    category: SkillCategory
    proficiency_level: int = Field(..., ge=1, le=10)
    hours_invested: int = Field(default=0, ge=0)


class AcademicProjectCreate(BaseModel):
    """Request model for creating academic project."""
    
    user_id: str
    project_id: str
    title: str
    role: str
    start_date: date
    status: ProjectStatus = ProjectStatus.PLANNING


class LearningGoalCreate(BaseModel):
    """Request model for setting learning goal."""
    
    user_id: str
    title: str
    description: Optional[str] = None
    target_date: date
    related_ring: str = "mental"
