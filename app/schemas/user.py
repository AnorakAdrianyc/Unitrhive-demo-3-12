"""User and Profile Pydantic models for UniThrive."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """Base user model with common attributes."""
    
    email: Optional[EmailStr] = None
    display_name: str = Field(..., min_length=1, max_length=100)
    is_anonymous: bool = False


class UserCreate(UserBase):
    """Model for creating a new user."""
    
    pass


class User(UserBase):
    """Complete user model with ID and timestamps."""
    
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProfileBase(BaseModel):
    """Base profile model with common attributes."""
    
    major: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1, le=7)
    campus: Optional[str] = Field(None, max_length=100)
    goals: List[str] = Field(default_factory=list)
    mbti_type: Optional[str] = Field(None, pattern=r"^[EI][NS][FT][JP]$")


class ProfileCreate(ProfileBase):
    """Model for creating a new profile."""
    
    user_id: str


class Profile(ProfileBase):
    """Complete profile model."""
    
    user_id: str
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserWithProfile(BaseModel):
    """Combined user and profile data."""
    
    user: User
    profile: Optional[Profile] = None


class UserLoginRequest(BaseModel):
    """Request model for user login."""
    
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    anonymous: bool = False


class UserLoginResponse(BaseModel):
    """Response model for user login."""
    
    user_id: str
    display_name: str
    is_anonymous: bool
    message: str
