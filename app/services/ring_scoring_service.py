"""3-Ring scoring service for UniThrive.

Calculates Mental, Psychological, and Physical ring scores based on user data.
"""

from datetime import date, datetime, timedelta
from statistics import mean
from typing import List, Optional, Dict, Any

from app.schemas.rings import (
    DailyRingScore, RingScores, RingTrends, TrendDirection,
    WeeklySummary, AchievementBadge
)
from app.schemas.checkin import CheckIn, ActivityRecord
from app.config import settings


class RingScoringService:
    """Service for calculating 3-ring wellbeing scores."""
    
    def __init__(self):
        self.mental_weights = settings.mental_ring_weights
        self.psych_weights = settings.psych_ring_weights
        self.physical_weights = settings.physical_ring_weights
    
    def calculate_mental_score(
        self,
        checkins: List[CheckIn],
        activities: List[ActivityRecord],
        mental_records: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate Mental Ring score.
        
        Based on:
        - Course engagement (40%)
        - Skill development (30%)
        - Workshop attendance (15%)
        - Project participation (15%)
        
        Args:
            checkins: User's check-ins
            activities: User's activities
            mental_records: Optional mental ring records from submodule
            
        Returns:
            Score between 0.0 and 1.0
        """
        # Course engagement from activities
        course_activities = [a for a in activities if a.type == "course"]
        study_hours = sum(a.duration_minutes for a in course_activities) / 60
        target_study = 30  # hours per week
        course_score = min(study_hours / target_study, 1.0)
        
        # Skill development
        skill_activities = [a for a in activities if a.type == "skill"]
        skill_hours = sum(a.duration_minutes for a in skill_activities) / 60
        skill_score = min(skill_hours / 10, 1.0)
        
        # Workshop attendance
        workshop_activities = [a for a in activities if a.type == "event"]
        workshop_score = min(len(workshop_activities) / 1, 1.0)
        
        # Project participation (estimate from mental records or activities)
        project_score = 0.5  # default baseline
        if mental_records:
            active_projects = mental_records.get('active_projects', 0)
            project_score = min(active_projects / 3, 1.0)
        
        # Weighted combination
        score = (
            course_score * self.mental_weights.get('course_engagement', 0.40) +
            skill_score * self.mental_weights.get('skill_development', 0.30) +
            workshop_score * self.mental_weights.get('workshops', 0.15) +
            project_score * self.mental_weights.get('projects', 0.15)
        )
        
        return round(score, 2)
    
    def calculate_psychological_score(
        self,
        checkins: List[CheckIn],
        psych_records: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate Psychological Ring score.
        
        Based on:
        - Emotional stability (30%) - inverse of stress
        - Self-awareness (30%) - based on assessments completed
        - Cognitive health (20%) - neurocognitive test performance
        - Risk mitigation (20%) - inverse of risk level
        
        Args:
            checkins: User's check-ins with mood and stress data
            psych_records: Optional psychological ring records
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not checkins:
            return 0.5  # baseline
        
        # Emotional stability (inverse of stress)
        avg_stress = mean(c.stress_score for c in checkins)
        stress_score = 1.0 - ((avg_stress - 1) / 4)  # Normalize 1-5 to 0-1
        stress_score = max(0.0, min(1.0, stress_score))
        
        # Mood positivity
        avg_mood = mean(c.mood_score for c in checkins)
        mood_score = (avg_mood - 1) / 4
        
        # Self-awareness (default baseline, enhanced by psych records)
        awareness_score = 0.3
        if psych_records:
            tests_completed = psych_records.get('tests_completed', 0)
            awareness_score = min(tests_completed / 5, 1.0)
        
        # Cognitive health
        cognitive_score = 0.5
        if psych_records:
            avg_percentile = psych_records.get('avg_neuro_percentile')
            if avg_percentile:
                cognitive_score = avg_percentile / 100
        
        # Risk mitigation (inverse of risk)
        risk_score = 0.7
        if psych_records:
            risk_level = psych_records.get('risk_level', 0)
            risk_score = 1.0 - (risk_level / 10)
        
        # Weighted combination
        score = (
            stress_score * self.psych_weights.get('emotional_stability', 0.30) +
            awareness_score * self.psych_weights.get('self_awareness', 0.30) +
            cognitive_score * self.psych_weights.get('cognitive_health', 0.20) +
            risk_score * self.psych_weights.get('risk_mitigation', 0.20)
        )
        
        return round(score, 2)
    
    def calculate_physical_score(
        self,
        checkins: List[CheckIn],
        physical_records: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate Physical Ring score.
        
        Based on:
        - Time management (25%)
        - Daily activity (25%)
        - Sleep quality (25%)
        - Fitness (25%)
        
        Args:
            checkins: User's check-ins with sleep and exercise data
            physical_records: Optional physical ring records
            
        Returns:
            Score between 0.0 and 1.0
        """
        # Time management (default baseline)
        time_score = 0.5
        if physical_records:
            adherence = physical_records.get('avg_schedule_adherence', 0.5)
            time_score = adherence
        
        # Activity level from check-ins
        avg_steps = 5000  # baseline
        if physical_records:
            avg_steps = physical_records.get('avg_daily_steps', 5000)
        activity_score = min(avg_steps / 10000, 1.0)
        
        # Sleep quality
        sleep_score = 0.5
        if checkins:
            avg_sleep = mean(c.sleep_hours for c in checkins)
            # Optimal is 7-9 hours, peak at 8
            sleep_score = 1.0 - abs(avg_sleep - 8) / 4
            sleep_score = max(0.0, min(1.0, sleep_score))
        
        # Fitness
        fitness_score = 0.3
        if physical_records:
            weekly_workouts = physical_records.get('weekly_workouts', 0)
            fitness_score = min(weekly_workouts / 3, 1.0)
        
        # Exercise from check-ins as backup
        if checkins and fitness_score < 0.3:
            total_exercise = sum(c.exercise_minutes for c in checkins)
            fitness_score = max(fitness_score, min(total_exercise / 150, 1.0))
        
        # Weighted combination
        score = (
            time_score * self.physical_weights.get('time_management', 0.25) +
            activity_score * self.physical_weights.get('activity', 0.25) +
            sleep_score * self.physical_weights.get('sleep', 0.25) +
            fitness_score * self.physical_weights.get('fitness', 0.25)
        )
        
        return round(score, 2)
    
    def calculate_all_scores(
        self,
        checkins: List[CheckIn],
        activities: List[ActivityRecord],
        mental_records: Optional[Dict[str, Any]] = None,
        psych_records: Optional[Dict[str, Any]] = None,
        physical_records: Optional[Dict[str, Any]] = None
    ) -> RingScores:
        """Calculate all three ring scores.
        
        Args:
            checkins: User's check-ins
            activities: User's activities
            mental_records: Optional mental ring data
            psych_records: Optional psychological ring data
            physical_records: Optional physical ring data
            
        Returns:
            RingScores with all three scores
        """
        return RingScores(
            mental=self.calculate_mental_score(checkins, activities, mental_records),
            psychological=self.calculate_psychological_score(checkins, psych_records),
            physical=self.calculate_physical_score(checkins, physical_records),
            calculated_at=datetime.now()
        )
    
    def calculate_trends(
        self,
        ring_history: List[DailyRingScore],
        period_days: int = 7
    ) -> RingTrends:
        """Calculate trends for each ring based on recent history.
        
        Args:
            ring_history: List of daily ring scores
            period_days: Number of days to analyze
            
        Returns:
            RingTrends with trend direction for each ring
        """
        if len(ring_history) < 2:
            return RingTrends(
                mental=TrendDirection.STABLE,
                psychological=TrendDirection.STABLE,
                physical=TrendDirection.STABLE,
                period_days=period_days
            )
        
        # Sort by date
        sorted_history = sorted(ring_history, key=lambda x: x.date)
        
        # Get recent period
        cutoff_date = date.today() - timedelta(days=period_days)
        recent = [r for r in sorted_history if r.date >= cutoff_date]
        
        if len(recent) < 2:
            recent = sorted_history[-2:]  # Use last 2 available
        
        # Calculate trends
        def get_trend(scores: List[float]) -> TrendDirection:
            if len(scores) < 2:
                return TrendDirection.STABLE
            
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            
            first_avg = mean(first_half) if first_half else 0
            second_avg = mean(second_half) if second_half else 0
            
            diff = second_avg - first_avg
            
            if diff > 0.1:
                return TrendDirection.IMPROVING
            elif diff < -0.1:
                return TrendDirection.DECLINING
            return TrendDirection.STABLE
        
        mental_scores = [r.mental_score for r in recent]
        psych_scores = [r.psychological_score for r in recent]
        physical_scores = [r.physical_score for r in recent]
        
        return RingTrends(
            mental=get_trend(mental_scores),
            psychological=get_trend(psych_scores),
            physical=get_trend(physical_scores),
            period_days=period_days
        )
    
    def determine_achievement_badge(
        self,
        ring_scores: RingScores,
        ring_history: List[DailyRingScore]
    ) -> Optional[AchievementBadge]:
        """Determine which achievement badge to award.
        
        Args:
            ring_scores: Current ring scores
            ring_history: Historical ring scores
            
        Returns:
            Achievement badge if criteria met
        """
        # Balance Seeker: All rings above 0.6
        if all(s > 0.6 for s in [ring_scores.mental, ring_scores.psychological, ring_scores.physical]):
            return AchievementBadge.BALANCE_SEEKER
        
        # Scholar: Mental ring above 0.8
        if ring_scores.mental > 0.8:
            return AchievementBadge.SCHOLAR
        
        # Mindful Master: Psychological ring above 0.8
        if ring_scores.psychological > 0.8:
            return AchievementBadge.MINDFUL_MASTER
        
        # Fitness Champion: Physical ring above 0.8
        if ring_scores.physical > 0.8:
            return AchievementBadge.FITNESS_CHAMPION
        
        # Stress Fighter: Psychological ring improved from below 0.4 to above 0.6
        if len(ring_history) >= 7:
            week_ago = date.today() - timedelta(days=7)
            old_scores = [r for r in ring_history if r.date <= week_ago]
            if old_scores:
                old_psych = mean(r.psychological_score for r in old_scores[-3:])
                if old_psych < 0.4 and ring_scores.psychological > 0.6:
                    return AchievementBadge.STRESS_FIGHTER
        
        # Comeback Kid: Overall improvement from low baseline
        if len(ring_history) >= 7:
            week_ago = date.today() - timedelta(days=7)
            old_scores = [r for r in ring_history if r.date <= week_ago]
            if old_scores:
                old_avg = mean([
                    mean([r.mental_score, r.psychological_score, r.physical_score])
                    for r in old_scores[-3:]
                ])
                current_avg = mean([ring_scores.mental, ring_scores.psychological, ring_scores.physical])
                if old_avg < 0.4 and current_avg > 0.6:
                    return AchievementBadge.COMEBACK_KID
        
        return None


# Global service instance
ring_scoring_service = RingScoringService()
