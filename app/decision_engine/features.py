"""Feature extraction module for UniThrive decision engine.

Extracts relevant features from raw user data for recommendation and risk analysis.
"""

from datetime import date, datetime, timedelta
from statistics import mean, stdev
from typing import Dict, Any, List, Optional


class FeatureExtractor:
    """Extracts features from user wellbeing data."""
    
    def extract_checkin_features(self, checkins: List[Any]) -> Dict[str, Any]:
        """Extract features from check-in data.
        
        Args:
            checkins: List of check-in records
            
        Returns:
            Dictionary of extracted features
        """
        if not checkins:
            return {
                "checkin_count": 0,
                "avg_mood": None,
                "avg_stress": None,
                "avg_sleep": None,
                "avg_exercise": None,
                "mood_trend": None,
                "stress_trend": None,
                "sleep_trend": None
            }
        
        # Basic averages
        moods = [c.mood_score for c in checkins]
        stresses = [c.stress_score for c in checkins]
        sleeps = [c.sleep_hours for c in checkins]
        exercises = [c.exercise_minutes for c in checkins]
        
        # Calculate trends (compare first half vs second half)
        def calc_trend(values: List[float]) -> str:
            if len(values) < 2:
                return "stable"
            mid = len(values) // 2
            first_avg = mean(values[:mid]) if mid > 0 else values[0]
            second_avg = mean(values[mid:]) if values[mid:] else values[-1]
            
            diff = second_avg - first_avg
            if diff > 0.3:
                return "improving"
            elif diff < -0.3:
                return "declining"
            return "stable"
        
        return {
            "checkin_count": len(checkins),
            "avg_mood": round(mean(moods), 2),
            "avg_stress": round(mean(stresses), 2),
            "avg_sleep": round(mean(sleeps), 2),
            "avg_exercise": round(mean(exercises), 2),
            "mood_trend": calc_trend(moods),
            "stress_trend": calc_trend(stresses),
            "sleep_trend": calc_trend(sleeps),
            "mood_variance": round(stdev(moods), 2) if len(moods) > 1 else 0,
            "stress_variance": round(stdev(stresses), 2) if len(stresses) > 1 else 0,
            "days_since_last_checkin": (date.today() - max(c.timestamp.date() for c in checkins)).days
        }
    
    def extract_activity_features(self, activities: List[Any]) -> Dict[str, Any]:
        """Extract features from activity data.
        
        Args:
            activities: List of activity records
            
        Returns:
            Dictionary of extracted features
        """
        if not activities:
            return {
                "activity_count": 0,
                "total_duration": 0,
                "study_hours": 0,
                "exercise_hours": 0,
                "social_hours": 0
            }
        
        total_duration = sum(a.duration_minutes for a in activities)
        
        # Categorize by ring
        study_activities = [a for a in activities if a.type in ["course", "skill"]]
        exercise_activities = [a for a in activities if a.type == "exercise"]
        social_activities = [a for a in activities if a.type in ["social", "event"]]
        
        return {
            "activity_count": len(activities),
            "total_duration": total_duration,
            "total_hours": round(total_duration / 60, 1),
            "study_hours": round(sum(a.duration_minutes for a in study_activities) / 60, 1),
            "exercise_hours": round(sum(a.duration_minutes for a in exercise_activities) / 60, 1),
            "social_hours": round(sum(a.duration_minutes for a in social_activities) / 60, 1),
            "activity_frequency": len(activities) / 7  # per day over a week
        }
    
    def extract_ring_score_features(self, ring_scores: List[Any]) -> Dict[str, Any]:
        """Extract features from ring score history.
        
        Args:
            ring_scores: List of daily ring scores
            
        Returns:
            Dictionary of extracted features
        """
        if not ring_scores:
            return {
                "avg_mental": 0.5,
                "avg_psychological": 0.5,
                "avg_physical": 0.5,
                "weakest_ring": None,
                "strongest_ring": None
            }
        
        mental_scores = [r.mental_score for r in ring_scores]
        psych_scores = [r.psychological_score for r in ring_scores]
        physical_scores = [r.physical_score for r in ring_scores]
        
        avg_mental = mean(mental_scores)
        avg_psych = mean(psych_scores)
        avg_physical = mean(physical_scores)
        
        scores = {
            "mental": avg_mental,
            "psychological": avg_psych,
            "physical": avg_physical
        }
        
        weakest = min(scores, key=scores.get)
        strongest = max(scores, key=scores.get)
        
        return {
            "avg_mental": round(avg_mental, 2),
            "avg_psychological": round(avg_psych, 2),
            "avg_physical": round(avg_physical, 2),
            "weakest_ring": weakest,
            "strongest_ring": strongest,
            "overall_score": round((avg_mental + avg_psych + avg_physical) / 3, 2),
            "mental_trend": self._calc_trend(mental_scores),
            "psychological_trend": self._calc_trend(psych_scores),
            "physical_trend": self._calc_trend(physical_scores)
        }
    
    def _calc_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values."""
        if len(values) < 2:
            return "stable"
        
        mid = len(values) // 2
        first_half = mean(values[:mid]) if mid > 0 else values[0]
        second_half = mean(values[mid:]) if values[mid:] else values[-1]
        
        diff = second_half - first_half
        
        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "declining"
        return "stable"
    
    def extract_risk_features(
        self,
        checkin_features: Dict[str, Any],
        ring_score_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract risk-related features.
        
        Args:
            checkin_features: Features from check-in data
            ring_score_features: Features from ring scores
            
        Returns:
            Dictionary of risk features
        """
        risk_factors = []
        risk_score = 0
        
        # Check stress levels
        if checkin_features.get("avg_stress", 0) >= 4:
            risk_factors.append("high_stress")
            risk_score += 3
        elif checkin_features.get("avg_stress", 0) >= 3.5:
            risk_factors.append("elevated_stress")
            risk_score += 2
        
        # Check mood
        if checkin_features.get("avg_mood", 5) <= 2:
            risk_factors.append("low_mood")
            risk_score += 3
        
        # Check sleep
        if checkin_features.get("avg_sleep", 8) < 5:
            risk_factors.append("sleep_deprivation")
            risk_score += 2
        
        # Check ring trends
        if ring_score_features.get("psychological_trend") == "declining":
            risk_factors.append("declining_psychological")
            risk_score += 2
        
        # Check for missed check-ins
        if checkin_features.get("days_since_last_checkin", 0) > 2:
            risk_factors.append("missed_checkins")
            risk_score += 1
        
        return {
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "risk_level": "high" if risk_score >= 6 else ("medium" if risk_score >= 4 else "low")
        }


# Global instance
feature_extractor = FeatureExtractor()
