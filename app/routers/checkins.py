"""Check-ins router for UniThrive.

Handles daily check-ins and activity logging endpoints.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query

from app.schemas.checkin import (
    CheckInCreate, CheckInHistoryResponse, ActivityRecordCreate,
    ActivityHistoryResponse, DailySummary
)
from app.services.checkin_service import checkin_service

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_checkin(checkin_data: CheckInCreate):
    """Create a new daily check-in.
    
    Records user's mood, stress, sleep, exercise, and social interactions.
    
    Args:
        checkin_data: Check-in data including mood_score (1-5), stress_score (1-5),
                     sleep_hours, exercise_minutes, social_interactions
                     
    Returns:
        The created check-in record
    """
    try:
        checkin = await checkin_service.create_checkin(checkin_data)
        return {
            "status": "success",
            "message": "Check-in recorded successfully",
            "data": checkin
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create check-in: {str(e)}"
        )


@router.get("/{user_id}", response_model=CheckInHistoryResponse)
async def get_checkin_history(
    user_id: str,
    days: int = Query(default=30, ge=1, le=365, description="Number of days to retrieve")
):
    """Get check-in history for a user.
    
    Args:
        user_id: The user ID
        days: Number of days to look back (1-365)
        
    Returns:
        List of check-ins for the specified period
    """
    checkins = await checkin_service.get_user_checkins(user_id, days=days)
    return CheckInHistoryResponse(
        user_id=user_id,
        check_ins=checkins,
        total_count=len(checkins)
    )


@router.get("/{user_id}/today")
async def get_today_checkins(user_id: str):
    """Get today's check-ins for a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        Today's check-ins
    """
    checkins = await checkin_service.get_today_checkins(user_id)
    return {
        "user_id": user_id,
        "date": date.today().isoformat(),
        "check_ins": checkins,
        "count": len(checkins)
    }


@router.get("/{user_id}/streak")
async def get_checkin_streak(user_id: str):
    """Get the current check-in streak for a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        Current streak count in days
    """
    streak = await checkin_service.get_checkin_streak(user_id)
    return {
        "user_id": user_id,
        "streak_days": streak,
        "message": f"{streak} day streak! Keep it up!" if streak > 0 else "Start your streak today!"
    }


@router.post("/activities", status_code=status.HTTP_201_CREATED)
async def create_activity(activity_data: ActivityRecordCreate):
    """Log a new activity.
    
    Records academic, exercise, skill, or social activities.
    
    Args:
        activity_data: Activity data including type, duration, and ring tag
        
    Returns:
        The created activity record
    """
    try:
        activity = await checkin_service.create_activity(activity_data)
        return {
            "status": "success",
            "message": "Activity logged successfully",
            "data": activity
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log activity: {str(e)}"
        )


@router.get("/activities/{user_id}", response_model=ActivityHistoryResponse)
async def get_activity_history(
    user_id: str,
    days: int = Query(default=30, ge=1, le=365),
    activity_type: Optional[str] = Query(default=None, description="Filter by activity type")
):
    """Get activity history for a user.
    
    Args:
        user_id: The user ID
        days: Number of days to look back
        activity_type: Optional filter by type (course, skill, exercise, social, event)
        
    Returns:
        List of activities for the specified period
    """
    activities = await checkin_service.get_user_activities(
        user_id, 
        days=days, 
        activity_type=activity_type
    )
    return ActivityHistoryResponse(
        user_id=user_id,
        activities=activities,
        total_count=len(activities)
    )


@router.get("/{user_id}/summary/{target_date}")
async def get_daily_summary(user_id: str, target_date: date):
    """Get a daily summary for a user.
    
    Args:
        user_id: The user ID
        target_date: The date to summarize
        
    Returns:
        Summary statistics for the day
    """
    summary = await checkin_service.get_daily_summary(user_id, target_date)
    return summary


@router.get("/{user_id}/summary/today")
async def get_today_summary(user_id: str):
    """Get today's summary for a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        Today's summary statistics
    """
    summary = await checkin_service.get_daily_summary(user_id, date.today())
    return summary
