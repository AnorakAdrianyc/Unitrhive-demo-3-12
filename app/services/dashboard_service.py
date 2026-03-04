"""Dashboard service for UniThrive.

Aggregates data from all sources for the main dashboard display.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional

from app.schemas.recommendations import DashboardSummary, RecommendationPreview
from app.schemas.rings import RingScores
from app.services.checkin_service import checkin_service
from app.services.ring_scoring_service import ring_scoring_service
from app.storage.json_storage import (
    JsonAlertStorage, JsonRecommendationStorage, JsonRingScoreStorage,
    JsonWeeklySummaryStorage
)


class DashboardService:
    """Service for aggregating dashboard data."""
    
    def __init__(self):
        self.alert_storage = JsonAlertStorage()
        self.recommendation_storage = JsonRecommendationStorage()
        self.ring_score_storage = JsonRingScoreStorage()
        self.summary_storage = JsonWeeklySummaryStorage()
    
    async def get_dashboard_summary(self, user_id: str) -> DashboardSummary:
        """Get complete dashboard summary for a user.
        
        Aggregates:
        - Current ring scores
        - Check-in streak
        - Unread alerts
        - Top recommendations
        
        Args:
            user_id: The user ID
            
        Returns:
            DashboardSummary with all aggregated data
        """
        # Get ring scores
        latest_scores = await self.ring_score_storage.get_latest_for_user(user_id)
        ring_scores_dict = {
            "mental": latest_scores.mental_score if latest_scores else 0.5,
            "psychological": latest_scores.psychological_score if latest_scores else 0.5,
            "physical": latest_scores.physical_score if latest_scores else 0.5
        }
        
        # Get streak
        streak = await checkin_service.get_checkin_streak(user_id)
        
        # Get unread alerts
        alerts = await self.alert_storage.get_by_user_id(user_id, active_only=True)
        unread_alerts = len(alerts)
        
        # Get top recommendations
        recommendations = await self.recommendation_storage.get_by_user_id(
            user_id,
            unread_only=False
        )
        
        # Create preview of top 3 recommendations
        preview = []
        for rec in recommendations[:3]:
            opportunity = rec.opportunity
            if opportunity:
                preview.append(RecommendationPreview(
                    id=rec.id,
                    title=opportunity.title,
                    ring_target=rec.ring_target,
                    explanation=rec.explanation
                ))
        
        return DashboardSummary(
            user_id=user_id,
            ring_scores=ring_scores_dict,
            streak_days=streak,
            unread_alerts=unread_alerts,
            recommendation_preview=preview
        )
    
    async def get_ring_score_today(self, user_id: str) -> Optional[RingScores]:
        """Get today's ring scores for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Today's ring scores or None if not calculated yet
        """
        latest = await self.ring_score_storage.get_latest_for_user(user_id)
        if latest and latest.date == date.today():
            return RingScores(
                mental=latest.mental_score,
                psychological=latest.psychological_score,
                physical=latest.physical_score,
                calculated_at=latest.calculated_at
            )
        return None
    
    async def get_weekly_highlight(self, user_id: str) -> dict:
        """Get the weekly highlight (spotlight opportunity and achievement).
        
        Args:
            user_id: The user ID
            
        Returns:
            Weekly highlight information
        """
        summary = await self.summary_storage.get_latest_for_user(user_id)
        
        if not summary:
            return {
                "user_id": user_id,
                "spotlight_opportunity": "Complete your daily check-in to get personalized recommendations!",
                "achievement_badge": None,
                "has_summary": False
            }
        
        return {
            "user_id": user_id,
            "week_start": summary.week_start.isoformat() if summary.week_start else None,
            "week_end": summary.week_end.isoformat() if summary.week_end else None,
            "spotlight_opportunity": summary.spotlight_opportunity,
            "achievement_badge": summary.achievement_badge,
            "has_summary": True,
            "ring_summaries": {
                "mental": summary.mental_summary,
                "psychological": summary.psych_summary,
                "physical": summary.physical_summary
            }
        }
    
    async def get_quick_stats(self, user_id: str) -> dict:
        """Get quick statistics for dashboard widgets.
        
        Args:
            user_id: The user ID
            
        Returns:
            Quick statistics dictionary
        """
        # Get last 7 days of data
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        # Ring scores
        ring_history = await self.ring_score_storage.get_by_user_id(
            user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        avg_mental = sum(r.mental_score for r in ring_history) / len(ring_history) if ring_history else 0
        avg_psych = sum(r.psychological_score for r in ring_history) / len(ring_history) if ring_history else 0
        avg_physical = sum(r.physical_score for r in ring_history) / len(ring_history) if ring_history else 0
        
        # Check-in count
        checkins = await checkin_service.get_user_checkins(user_id, days=7)
        
        # Activities
        activities = await checkin_service.get_user_activities(user_id, days=7)
        total_activity_hours = sum(a.duration_minutes for a in activities) / 60
        
        # Alerts
        active_alerts = await self.alert_storage.get_by_user_id(user_id, active_only=True)
        high_risk_alerts = len([a for a in active_alerts if a.risk_level == "high"])
        
        return {
            "user_id": user_id,
            "period_days": 7,
            "ring_averages": {
                "mental": round(avg_mental, 2),
                "psychological": round(avg_psych, 2),
                "physical": round(avg_physical, 2),
                "overall": round((avg_mental + avg_psych + avg_physical) / 3, 2)
            },
            "check_ins_this_week": len(checkins),
            "activities_logged": len(activities),
            "total_activity_hours": round(total_activity_hours, 1),
            "active_alerts": len(active_alerts),
            "high_risk_alerts": high_risk_alerts,
            "streak_days": await checkin_service.get_checkin_streak(user_id)
        }


# Global service instance
dashboard_service = DashboardService()
