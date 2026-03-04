"""AI Time Management Assistant service for UniThrive.

Provides smart scheduling, workload optimization, and procrastination detection.
"""

from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any
from statistics import mean

from app.schemas.ai_chat import (
    TimePlan, TimePlanRequest, TimePlanResponse,
    ScheduleOptimizationRequest, TimeManagementSuggestion,
    TimeManagementSuggestionsResponse,
    StudyBlock, ExamScheduleItem, BreakReminder
)
from app.services.checkin_service import checkin_service


class TimeManagementService:
    """AI Time Management Assistant."""
    
    def __init__(self):
        pass
    
    async def generate_time_plan(self, request: TimePlanRequest) -> TimePlanResponse:
        """Generate a personalized time management plan.
        
        Args:
            request: Time plan request with exam schedule and preferences
            
        Returns:
            TimePlanResponse with generated plan and recommendations
        """
        user_id = request.user_id
        
        # Analyze past check-ins to understand productive patterns
        checkins = await checkin_service.get_user_checkins(user_id, days=14)
        activities = await checkin_service.get_user_activities(user_id, days=14)
        
        # Calculate workload balance score
        total_study_hours = sum(
            a.duration_minutes for a in activities if a.type == "course"
        ) / 60
        avg_daily_hours = total_study_hours / 14 if checkins else 4
        
        workload_balance = min(avg_daily_hours / request.preferred_study_hours_per_day, 1.0)
        
        # Generate study blocks based on preferences
        study_blocks = []
        for exam in request.upcoming_exams:
            days_until_exam = (exam.exam_date - date.today()).days
            
            if days_until_exam > 0:
                # Create spaced repetition schedule
                study_sessions = self._create_spaced_sessions(exam, days_until_exam)
                study_blocks.extend(study_sessions)
        
        # Sort by date and time
        study_blocks.sort(key=lambda x: (x.start_time.hour, x.start_time.minute))
        
        # Generate break reminders
        break_reminders = [
            BreakReminder(after_minutes=45, break_duration_minutes=5, reminder_type="movement"),
            BreakReminder(after_minutes=90, break_duration_minutes=10, reminder_type="mindfulness"),
            BreakReminder(after_minutes=180, break_duration_minutes=30, reminder_type="eye_rest")
        ]
        
        # Create the plan
        plan = TimePlan(
            plan_id="",
            user_id=user_id,
            created_at=datetime.now(),
            exam_schedule=request.upcoming_exams,
            daily_study_blocks=study_blocks[:10],  # Limit to 10 blocks
            break_reminders=break_reminders,
            workload_balance_score=round(workload_balance, 2),
            estimated_productivity_score=round(self._estimate_productivity(checkins), 2)
        )
        
        # Generate recommendations
        recommendations = self._generate_plan_recommendations(request, checkins, workload_balance)
        
        # Generate warnings
        warnings = self._generate_plan_warnings(request, workload_balance)
        
        return TimePlanResponse(
            plan=plan,
            recommendations=recommendations,
            warnings=warnings
        )
    
    def _create_spaced_sessions(
        self, 
        exam: ExamScheduleItem, 
        days_until: int
    ) -> List[StudyBlock]:
        """Create spaced repetition study sessions for an exam.
        
        Args:
            exam: The exam to prepare for
            days_until: Days until the exam
            
        Returns:
            List of study blocks
        """
        blocks = []
        
        # Create sessions with decreasing intervals as exam approaches
        if days_until >= 7:
            # Far from exam: study every 2-3 days
            intervals = [days_until - i * 2 for i in range(min(3, days_until // 2))]
        else:
            # Close to exam: study daily
            intervals = list(range(days_until, 0, -1))[:days_until]
        
        for interval in intervals:
            if interval > 0:
                study_date = date.today() + timedelta(days=interval)
                
                # Morning session for best retention
                block = StudyBlock(
                    start_time=time(9, 0),
                    end_time=time(10, 30),
                    subject=exam.subject,
                    priority=exam.priority,
                    break_after=True
                )
                blocks.append(block)
        
        return blocks
    
    def _estimate_productivity(self, checkins: List[Any]) -> float:
        """Estimate productivity based on check-in patterns.
        
        Args:
            checkins: User's check-ins
            
        Returns:
            Productivity score (0-1)
        """
        if not checkins:
            return 0.5
        
        # Higher mood and lower stress = higher productivity
        avg_mood = mean(c.mood_score for c in checkins) if checkins else 3
        avg_stress = mean(c.stress_score for c in checkins) if checkins else 3
        
        # Calculate sleep quality impact
        avg_sleep = mean(c.sleep_hours for c in checkins) if checkins else 7
        sleep_score = 1.0 - abs(avg_sleep - 8) / 4
        sleep_score = max(0, min(1, sleep_score))
        
        # Productivity formula
        mood_component = (avg_mood - 1) / 4  # 1-5 to 0-1
        stress_component = 1 - ((avg_stress - 1) / 4)  # invert stress
        
        productivity = (mood_component * 0.4 + stress_component * 0.3 + sleep_score * 0.3)
        return max(0, min(1, productivity))
    
    def _generate_plan_recommendations(
        self,
        request: TimePlanRequest,
        checkins: List[Any],
        workload_balance: float
    ) -> List[str]:
        """Generate personalized recommendations.
        
        Args:
            request: The time plan request
            checkins: User's check-ins
            workload_balance: Current workload balance score
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if workload_balance < 0.5:
            recommendations.append(
                "You're currently under your target study hours. Consider adding 30-60 minutes "
                "of focused study time to build consistency."
            )
        elif workload_balance > 1.2:
            recommendations.append(
                "Your current study load is high. Make sure to prioritize breaks and sleep "
                "to avoid burnout."
            )
        
        if checkins:
            avg_stress = mean(c.stress_score for c in checkins)
            if avg_stress > 3.5:
                recommendations.append(
                    "Your stress levels have been elevated. Consider adding mindfulness "
                    "breaks to your schedule and reviewing your workload."
                )
        
        if len(request.upcoming_exams) > 3:
            recommendations.append(
                f"You have {len(request.upcoming_exams)} exams coming up. Prioritize the "
                "highest-weight exams and use spaced repetition for efficient studying."
            )
        
        if "morning" in request.preferred_productive_times:
            recommendations.append(
                "You prefer morning study sessions. Schedule your most challenging "
                "subjects between 9-11 AM for optimal retention."
            )
        
        recommendations.append(
            "Use the Pomodoro technique: 25 minutes of focused work followed by a 5-minute break."
        )
        
        return recommendations
    
    def _generate_plan_warnings(
        self,
        request: TimePlanRequest,
        workload_balance: float
    ) -> List[str]:
        """Generate warnings about potential issues.
        
        Args:
            request: The time plan request
            workload_balance: Current workload balance
            
        Returns:
            List of warning strings
        """
        warnings = []
        
        # Check for cramming
        for exam in request.upcoming_exams:
            days_until = (exam.exam_date - date.today()).days
            if days_until < 3 and exam.recommended_daily_study_hours > 6:
                warnings.append(
                    f"{exam.exam_name} is in {days_until} days but requires extensive preparation. "
                    "Focus on key concepts rather than trying to cover everything."
                )
        
        # Check for back-to-back exams
        if len(request.upcoming_exams) >= 2:
            sorted_exams = sorted(request.upcoming_exams, key=lambda x: x.exam_date)
            for i in range(len(sorted_exams) - 1):
                days_between = (sorted_exams[i + 1].exam_date - sorted_exams[i].exam_date).days
                if days_between == 1:
                    warnings.append(
                        f"You have back-to-back exams: {sorted_exams[i].exam_name} and "
                        f"{sorted_exams[i + 1].exam_name}. Plan your study time carefully."
                    )
        
        return warnings
    
    async def get_suggestions(self, user_id: str) -> TimeManagementSuggestionsResponse:
        """Get personalized time management suggestions.
        
        Args:
            user_id: The user ID
            
        Returns:
            TimeManagementSuggestionsResponse with suggestions
        """
        # Get user data
        checkins = await checkin_service.get_user_checkins(user_id, days=14)
        activities = await checkin_service.get_user_activities(user_id, days=14)
        
        suggestions = []
        
        # Analyze patterns
        if checkins:
            # Procrastination detection
            avg_stress = mean(c.stress_score for c in checkins)
            if avg_stress > 4:
                suggestions.append(TimeManagementSuggestion(
                    suggestion_type="stress_management",
                    title="High Stress Detected",
                    description=(
                        "Your stress levels have been consistently high. Consider breaking tasks "
                        "into smaller chunks and scheduling regular breaks."
                    ),
                    priority=5,
                    based_on_data=["stress_score_avg"]
                ))
            
            # Sleep analysis
            avg_sleep = mean(c.sleep_hours for c in checkins)
            if avg_sleep < 6:
                suggestions.append(TimeManagementSuggestion(
                    suggestion_type="sleep_optimization",
                    title="Improve Sleep Schedule",
                    description=(
                        "You're averaging less than 6 hours of sleep. Better sleep leads to "
                        "improved focus and retention. Try to get 7-8 hours."
                    ),
                    priority=4,
                    based_on_data=["sleep_hours_avg"]
                ))
        
        # Activity analysis
        course_activities = [a for a in activities if a.type == "course"]
        if not course_activities:
            suggestions.append(TimeManagementSuggestion(
                suggestion_type="study_consistency",
                title="Start Building Study Habits",
                description=(
                    "No study activities logged recently. Try the Pomodoro technique: "
                    "25 minutes of focused study followed by a 5-minute break."
                ),
                priority=3,
                based_on_data=["activity_count"]
            ))
        
        # General suggestions
        suggestions.append(TimeManagementSuggestion(
            suggestion_type="time_blocking",
            title="Use Time Blocking",
            description=(
                "Schedule specific blocks of time for different subjects. "
                "This reduces decision fatigue and improves focus."
            ),
            priority=2,
            based_on_data=[]
        ))
        
        suggestions.append(TimeManagementSuggestion(
            suggestion_type="break_optimization",
            title="Take Strategic Breaks",
            description=(
                "Your brain needs rest to consolidate learning. Take a 5-minute break "
                "every 25-30 minutes of focused work."
            ),
            priority=2,
            based_on_data=[]
        ))
        
        # Calculate overall efficiency
        efficiency = self._calculate_efficiency(checkins, activities)
        
        areas_for_improvement = []
        if checkins and mean(c.stress_score for c in checkins) > 3:
            areas_for_improvement.append("stress_management")
        if checkins and mean(c.sleep_hours for c in checkins) < 6:
            areas_for_improvement.append("sleep_quality")
        
        return TimeManagementSuggestionsResponse(
            user_id=user_id,
            suggestions=suggestions,
            overall_efficiency_score=round(efficiency, 2),
            areas_for_improvement=areas_for_improvement
        )
    
    def _calculate_efficiency(self, checkins: List[Any], activities: List[Any]) -> float:
        """Calculate overall time management efficiency.
        
        Args:
            checkins: User's check-ins
            activities: User's activities
            
        Returns:
            Efficiency score (0-1)
        """
        if not checkins:
            return 0.5
        
        # Components of efficiency
        stress_factor = 1 - (mean(c.stress_score for c in checkins) - 1) / 4
        sleep_factor = max(0, 1 - abs(mean(c.sleep_hours for c in checkins) - 8) / 4)
        activity_factor = min(len(activities) / 10, 1.0) if activities else 0.3
        
        efficiency = (stress_factor * 0.3 + sleep_factor * 0.3 + activity_factor * 0.4)
        return max(0, min(1, efficiency))


# Global service instance
time_management_service = TimeManagementService()
