"""Wellbeing Rings router for UniThrive.

Handles 3-ring scoring and history endpoints.
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Query

from app.schemas.rings import (
    RingScores, RingTrends, DailyRingScore, TodayRingResponse,
    RingHistoryResponse, WeeklySummary, AchievementBadge
)
from app.schemas.checkin import CheckIn, ActivityRecord
from app.services.ring_scoring_service import ring_scoring_service
from app.storage.json_storage import (
    JsonCheckInStorage, JsonActivityStorage, JsonRingScoreStorage,
    JsonWeeklySummaryStorage
)

router = APIRouter()

# Storage instances
checkin_storage = JsonCheckInStorage()
activity_storage = JsonActivityStorage()
ring_score_storage = JsonRingScoreStorage()
summary_storage = JsonWeeklySummaryStorage()


@router.get("/{user_id}/today", response_model=TodayRingResponse)
async def get_today_rings(user_id: str):
    """Get today's ring scores for a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        Today's ring scores and trends
    """
    # Get recent check-ins and activities
    today = date.today()
    checkins = await checkin_storage.get_by_user_and_date(user_id, today)
    activities = await activity_storage.get_by_user_id(
        user_id, 
        start_date=today,
        end_date=today
    )
    
    # Calculate scores
    ring_scores = ring_scoring_service.calculate_all_scores(
        checkins=checkins,
        activities=activities
    )
    
    # Get history for trends
    history = await ring_score_storage.get_by_user_id(user_id, days=7)
    trends = ring_scoring_service.calculate_trends(history)
    
    return TodayRingResponse(
        user_id=user_id,
        date=today,
        ring_scores=ring_scores,
        trend_since_last_week=trends
    )


@router.get("/{user_id}/history", response_model=RingHistoryResponse)
async def get_ring_history(
    user_id: str,
    days: int = Query(default=30, ge=1, le=365, description="Number of days to retrieve")
):
    """Get ring score history for a user.
    
    Args:
        user_id: The user ID
        days: Number of days of history to retrieve
        
    Returns:
        Historical ring scores and trends
    """
    end_date = date.today()
    start_date = end_date - __import__('datetime').timedelta(days=days)
    
    history = await ring_score_storage.get_by_user_id(
        user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    trends = ring_scoring_service.calculate_trends(history, period_days=min(days, 7))
    
    return RingHistoryResponse(
        user_id=user_id,
        history=history,
        trends=trends
    )


@router.get("/{user_id}/scores")
async def calculate_ring_scores(user_id: str):
    """Calculate current ring scores for a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        Calculated ring scores
    """
    # Get recent data
    end_date = date.today()
    start_date = end_date - __import__('datetime').timedelta(days=7)
    
    checkins = await checkin_storage.get_by_user_id(
        user_id,
        start_date=start_date,
        end_date=end_date
    )
    activities = await activity_storage.get_by_user_id(
        user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Calculate scores
    ring_scores = ring_scoring_service.calculate_all_scores(
        checkins=checkins,
        activities=activities
    )
    
    return {
        "user_id": user_id,
        "ring_scores": ring_scores,
        "data_period_days": 7,
        "checkin_count": len(checkins),
        "activity_count": len(activities)
    }


@router.post("/{user_id}/calculate", status_code=status.HTTP_201_CREATED)
async def calculate_and_store_rings(user_id: str):
    """Calculate and store today's ring scores.
    
    Args:
        user_id: The user ID
        
    Returns:
        The stored ring score record
    """
    # Get recent data
    today = date.today()
    checkins = await checkin_storage.get_by_user_and_date(user_id, today)
    activities = await activity_storage.get_by_user_id(
        user_id,
        start_date=today,
        end_date=today
    )
    
    # Calculate scores
    ring_scores = ring_scoring_service.calculate_all_scores(
        checkins=checkins,
        activities=activities
    )
    
    # Create and store daily score
    daily_score = DailyRingScore(
        id="",
        user_id=user_id,
        date=today,
        mental_score=ring_scores.mental,
        psychological_score=ring_scores.psychological,
        physical_score=ring_scores.physical,
        calculated_at=__import__('datetime').datetime.now()
    )
    
    stored = await ring_score_storage.create(daily_score)
    
    return {
        "status": "success",
        "message": "Ring scores calculated and stored",
        "data": stored
    }


@router.get("/{user_id}/weekly-summary")
async def get_weekly_summary(user_id: str):
    """Get the latest weekly summary for a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        The most recent weekly summary
    """
    summary = await summary_storage.get_latest_for_user(user_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No weekly summary found. Run batch processing to generate summaries."
        )
    return summary


@router.get("/{user_id}/weekly-summary/all")
async def get_all_weekly_summaries(user_id: str, limit: int = Query(default=10, ge=1, le=52)):
    """Get all weekly summaries for a user.
    
    Args:
        user_id: The user ID
        limit: Maximum number of summaries to return
        
    Returns:
        List of weekly summaries
    """
    summaries = await summary_storage.get_by_user_id(user_id)
    return {
        "user_id": user_id,
        "summaries": summaries[:limit],
        "total_count": len(summaries)
    }


@router.get("/{user_id}/badge")
async def get_achievement_badge(user_id: str):
    """Get the current achievement badge for a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        Achievement badge information
    """
    # Get current scores and history
    today = date.today()
    checkins = await checkin_storage.get_by_user_and_date(user_id, today)
    activities = await activity_storage.get_by_user_id(
        user_id,
        start_date=today,
        end_date=today
    )
    
    ring_scores = ring_scoring_service.calculate_all_scores(
        checkins=checkins,
        activities=activities
    )
    
    # Get history for trend analysis
    history = await ring_score_storage.get_by_user_id(user_id, days=14)
    
    badge = ring_scoring_service.determine_achievement_badge(ring_scores, history)
    
    return {
        "user_id": user_id,
        "badge": badge.value if badge else None,
        "badge_name": badge.name if badge else None,
        "ring_scores": ring_scores,
        "message": f"Congratulations! You've earned the {badge.value} badge!" if badge else "Keep working on your rings to earn badges!"
    }


@router.get("/trends/{user_id}")
async def get_ring_trends(
    user_id: str,
    period_days: int = Query(default=7, ge=3, le=30)
):
    """Get trend analysis for ring scores.
    
    Args:
        user_id: The user ID
        period_days: Number of days to analyze for trends
        
    Returns:
        Trend directions for each ring
    """
    end_date = date.today()
    start_date = end_date - __import__('datetime').timedelta(days=period_days * 2)  # Get enough data
    
    history = await ring_score_storage.get_by_user_id(
        user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    trends = ring_scoring_service.calculate_trends(history, period_days=period_days)
    
    return {
        "user_id": user_id,
        "trends": trends,
        "analysis_period_days": period_days,
        "data_points_used": len(history)
    }
