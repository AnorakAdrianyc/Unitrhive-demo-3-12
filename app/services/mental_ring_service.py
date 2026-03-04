"""Mental Ring service for UniThrive.

Handles business logic for intellectual growth tracking including
course engagement, workshops, skill development, and projects.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from statistics import mean

from app.schemas.mental_ring import (
    CourseEngagement, CourseEngagementCreate,
    WorkshopAttendance, WorkshopAttendanceCreate,
    SkillDevelopment, SkillDevelopmentCreate,
    AcademicProject, AcademicProjectCreate,
    LearningGoal, LearningGoalCreate,
    MentalRingSummary
)
from app.storage.json_storage import JsonMentalRingStorage


class MentalRingService:
    """Service for managing Mental Ring data."""
    
    def __init__(self):
        self.course_storage = JsonMentalRingStorage(entity_type="courses")
        self.workshop_storage = JsonMentalRingStorage(entity_type="workshops")
        self.skill_storage = JsonMentalRingStorage(entity_type="skills")
        self.project_storage = JsonMentalRingStorage(entity_type="projects")
        self.goal_storage = JsonMentalRingStorage(entity_type="goals")
    
    # Course Engagement
    async def create_course_engagement(self, data: CourseEngagementCreate) -> Dict[str, Any]:
        """Create a course engagement record."""
        course = CourseEngagement(
            id="",
            user_id=data.user_id,
            course_id=data.course_id,
            course_name=data.course_name,
            attendance_rate=data.attendance_rate,
            assignment_completion=data.assignment_completion,
            participation_score=data.participation_score,
            current_grade=data.current_grade if hasattr(data, 'current_grade') else None,
            last_updated=datetime.now()
        )
        return await self.course_storage.create(course)
    
    async def get_user_courses(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all course engagements for a user."""
        return await self.course_storage.get_by_user_id(user_id)
    
    # Workshop Attendance
    async def create_workshop_attendance(self, data: WorkshopAttendanceCreate) -> Dict[str, Any]:
        """Record workshop attendance."""
        workshop = WorkshopAttendance(
            id="",
            user_id=data.user_id,
            workshop_id=data.workshop_id,
            title=data.title,
            date=data.date,
            duration_minutes=data.duration_minutes,
            skills_gained=data.skills_gained,
            satisfaction_rating=data.satisfaction_rating if hasattr(data, 'satisfaction_rating') else None,
            notes=data.notes if hasattr(data, 'notes') else None
        )
        return await self.workshop_storage.create(workshop)
    
    async def get_user_workshops(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all workshop attendances for a user."""
        return await self.workshop_storage.get_by_user_id(user_id)
    
    # Skill Development
    async def create_skill_development(self, data: SkillDevelopmentCreate) -> Dict[str, Any]:
        """Add or update skill development."""
        skill = SkillDevelopment(
            id="",
            user_id=data.user_id,
            skill_name=data.skill_name,
            category=data.category,
            proficiency_level=data.proficiency_level,
            hours_invested=data.hours_invested,
            certifications=data.certifications if hasattr(data, 'certifications') else [],
            started_date=date.today(),
            last_practiced=None,
            goal_level=data.goal_level if hasattr(data, 'goal_level') else None
        )
        return await self.skill_storage.create(skill)
    
    async def get_user_skills(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all skills for a user."""
        return await self.skill_storage.get_by_user_id(user_id)
    
    # Academic Projects
    async def create_academic_project(self, data: AcademicProjectCreate) -> Dict[str, Any]:
        """Create an academic project record."""
        project = AcademicProject(
            id="",
            user_id=data.user_id,
            project_id=data.project_id,
            title=data.title,
            description=data.description if hasattr(data, 'description') else None,
            role=data.role,
            start_date=data.start_date,
            end_date=data.end_date if hasattr(data, 'end_date') else None,
            status=data.status,
            outcomes=data.outcomes if hasattr(data, 'outcomes') else [],
            collaborators=data.collaborators if hasattr(data, 'collaborators') else []
        )
        return await self.project_storage.create(project)
    
    async def get_user_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all projects for a user."""
        return await self.project_storage.get_by_user_id(user_id)
    
    # Learning Goals
    async def create_learning_goal(self, data: LearningGoalCreate) -> Dict[str, Any]:
        """Create a learning goal."""
        goal = LearningGoal(
            id="",
            user_id=data.user_id,
            title=data.title,
            description=data.description,
            target_date=data.target_date,
            progress_percent=0.0,
            related_ring=data.related_ring,
            milestones=data.milestones if hasattr(data, 'milestones') else [],
            created_at=datetime.now(),
            completed_at=None
        )
        return await self.goal_storage.create(goal)
    
    async def get_user_goals(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all learning goals for a user."""
        return await self.goal_storage.get_by_user_id(user_id)
    
    # Summary
    async def get_mental_ring_summary(
        self, 
        user_id: str,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None
    ) -> MentalRingSummary:
        """Generate a summary of the Mental Ring for a user."""
        if not period_start:
            period_start = date.today() - __import__('datetime').timedelta(days=30)
        if not period_end:
            period_end = date.today()
        
        # Get all data
        courses = await self.get_user_courses(user_id)
        workshops = await self.get_user_workshops(user_id)
        skills = await self.get_user_skills(user_id)
        projects = await self.get_user_projects(user_id)
        goals = await self.get_user_goals(user_id)
        
        # Calculate metrics
        course_engagement_avg = 0.0
        if courses:
            engagement_scores = [
                c['attendance_rate'] * 0.4 + 
                c['assignment_completion'] * 0.4 + 
                c['participation_score'] * 0.2
                for c in courses
            ]
            course_engagement_avg = mean(engagement_scores)
        
        avg_skill_proficiency = 0.0
        if skills:
            avg_skill_proficiency = mean(s['proficiency_level'] for s in skills)
        
        workshops_in_period = [
            w for w in workshops 
            if period_start <= w['date'] <= period_end
        ]
        
        active_projects = len([p for p in projects if p['status'] == 'in_progress'])
        completed_projects = len([p for p in projects if p['status'] == 'completed'])
        
        active_goals = len([g for g in goals if g['completed_at'] is None])
        completed_goals = len([g for g in goals if g['completed_at'] is not None])
        
        # Calculate overall score
        overall_score = (
            course_engagement_avg * 0.4 +
            (avg_skill_proficiency / 10) * 0.3 +
            min(len(workshops_in_period) / 4, 1.0) * 0.15 +
            min(active_projects / 3, 1.0) * 0.15
        )
        
        # Generate recommendations
        recommendations = []
        if course_engagement_avg < 0.6:
            recommendations.append("Consider increasing class attendance and participation")
        if len(workshops_in_period) < 1:
            recommendations.append("Attend a workshop to expand your skills")
        if avg_skill_proficiency < 5:
            recommendations.append("Focus on developing one key skill this month")
        
        return MentalRingSummary(
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            course_engagement_avg=round(course_engagement_avg, 2),
            skills_count=len(skills),
            avg_skill_proficiency=round(avg_skill_proficiency, 2),
            workshops_attended=len(workshops_in_period),
            active_projects=active_projects,
            completed_projects=completed_projects,
            learning_goals_active=active_goals,
            learning_goals_completed=completed_goals,
            overall_score=round(overall_score, 2),
            recommendations=recommendations
        )


# Global service instance
mental_ring_service = MentalRingService()
