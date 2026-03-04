"""Dashboard router for UniThrive.

Handles main dashboard data aggregation endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.recommendations import DashboardSummary
from app.services.dashboard_service import dashboard_service
from app.storage.json_storage import (
    JsonAlertStorage, JsonRecommendationStorage, JsonWeeklySummaryStorage
)

router = APIRouter()

# Storage instances
alert_storage = JsonAlertStorage()
recommendation_storage = JsonRecommendationStorage()
summary_storage = JsonWeeklySummaryStorage()


@router.get("/{user_id}")
async def get_dashboard(user_id: str):
    """Get complete dashboard data for a user.
    
    This is the main dashboard endpoint that aggregates:
    - Ring scores
    - Check-in streak
    - Alerts
    - Recommendations preview
    - Weekly summary
    
    Args:
        user_id: The user ID
        
    Returns:
        Complete dashboard data
    """
    try:
        summary = await dashboard_service.get_dashboard_summary(user_id)
        weekly_highlight = await dashboard_service.get_weekly_highlight(user_id)
        quick_stats = await dashboard_service.get_quick_stats(user_id)
        
        return {
            "status": "success",
            "user_id": user_id,
            "dashboard": summary,
            "weekly_highlight": weekly_highlight,
            "quick_stats": quick_stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load dashboard: {str(e)}"
        )


@router.get("/{user_id}/summary")
async def get_dashboard_summary(user_id: str):
    """Get dashboard summary for a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        DashboardSummary with ring scores, streak, alerts, recommendations
    """
    try:
        summary = await dashboard_service.get_dashboard_summary(user_id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load dashboard summary: {str(e)}"
        )


@router.get("/{user_id}/weekly-highlight")
async def get_weekly_highlight(user_id: str):
    """Get the weekly highlight (spotlight opportunity and achievement).
    
    Args:
        user_id: The user ID
        
    Returns:
        Weekly highlight information
    """
    highlight = await dashboard_service.get_weekly_highlight(user_id)
    return highlight


@router.get("/{user_id}/quick-stats")
async def get_quick_stats(user_id: str):
    """Get quick statistics for dashboard widgets.
    
    Args:
        user_id: The user ID
        
    Returns:
        Quick statistics
    """
    stats = await dashboard_service.get_quick_stats(user_id)
    return stats


@router.get("/{user_id}/alerts")
async def get_user_alerts(user_id: str, active_only: bool = True):
    """Get alerts for a user.
    
    Args:
        user_id: The user ID
        active_only: If True, only return unacknowledged alerts
        
    Returns:
        List of alerts
    """
    alerts = await alert_storage.get_by_user_id(user_id, active_only=active_only)
    return {
        "user_id": user_id,
        "alerts": alerts,
        "count": len(alerts),
        "active_only": active_only
    }


@router.post("/{user_id}/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(user_id: str, alert_id: str):
    """Acknowledge an alert.
    
    Args:
        user_id: The user ID
        alert_id: The alert ID to acknowledge
        
    Returns:
        Success status
    """
    success = await alert_storage.acknowledge(alert_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return {
        "status": "success",
        "message": "Alert acknowledged",
        "alert_id": alert_id
    }


@router.get("/{user_id}/recommendations")
async def get_recommendations(user_id: str, limit: int = 10):
    """Get recommendations for a user.
    
    Args:
        user_id: The user ID
        limit: Maximum number of recommendations to return
        
    Returns:
        List of personalized recommendations
    """
    recommendations = await recommendation_storage.get_by_user_id(user_id)
    
    # Enrich with opportunity data
    enriched = []
    for rec in recommendations[:limit]:
        if rec.opportunity:
            enriched.append({
                "id": rec.id,
                "title": rec.opportunity.title,
                "type": rec.opportunity.type,
                "ring_target": rec.ring_target,
                "explanation": rec.explanation,
                "score": rec.score,
                "is_viewed": rec.is_viewed,
                "opportunity": rec.opportunity
            })
    
    return {
        "user_id": user_id,
        "recommendations": enriched,
        "count": len(enriched),
        "total_available": len(recommendations)
    }


@router.get("/{user_id}/weekly-summary")
async def get_dashboard_weekly_summary(user_id: str):
    """Get weekly summary for dashboard display.
    
    Args:
        user_id: The user ID
        
    Returns:
        Weekly summary data
    """
    summary = await summary_storage.get_latest_for_user(user_id)
    if not summary:
        return {
            "user_id": user_id,
            "has_summary": False,
            "message": "No weekly summary available yet. Check in daily to generate your first summary!"
        }
    
    return {
        "user_id": user_id,
        "has_summary": True,
        "week_start": summary.week_start,
        "week_end": summary.week_end,
        "summaries": {
            "mental": summary.mental_summary,
            "psychological": summary.psych_summary,
            "physical": summary.physical_summary
        },
        "spotlight_opportunity": summary.spotlight_opportunity,
        "achievement_badge": summary.achievement_badge,
        "ring_scores": summary.ring_scores
    }
