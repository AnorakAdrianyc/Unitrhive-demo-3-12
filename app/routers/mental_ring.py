"""Mental Ring router for UniThrive.

Handles intellectual growth tracking endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.mental_ring import (
    CourseEngagementCreate, WorkshopAttendanceCreate,
    SkillDevelopmentCreate, AcademicProjectCreate, LearningGoalCreate
)
from app.services.mental_ring_service import mental_ring_service

router = APIRouter()


@router.post("/courses", status_code=status.HTTP_201_CREATED)
async def create_course_engagement(data: CourseEngagementCreate):
    """Log course engagement."""
    try:
        result = await mental_ring_service.create_course_engagement(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/courses/{user_id}")
async def get_user_courses(user_id: str):
    """Get course engagement for a user."""
    courses = await mental_ring_service.get_user_courses(user_id)
    return {"user_id": user_id, "courses": courses, "count": len(courses)}


@router.post("/workshops", status_code=status.HTTP_201_CREATED)
async def create_workshop_attendance(data: WorkshopAttendanceCreate):
    """Record workshop attendance."""
    try:
        result = await mental_ring_service.create_workshop_attendance(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/workshops/{user_id}")
async def get_user_workshops(user_id: str):
    """Get workshop attendance for a user."""
    workshops = await mental_ring_service.get_user_workshops(user_id)
    return {"user_id": user_id, "workshops": workshops, "count": len(workshops)}


@router.post("/skills", status_code=status.HTTP_201_CREATED)
async def create_skill_development(data: SkillDevelopmentCreate):
    """Add skill development record."""
    try:
        result = await mental_ring_service.create_skill_development(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/skills/{user_id}")
async def get_user_skills(user_id: str):
    """Get skills for a user."""
    skills = await mental_ring_service.get_user_skills(user_id)
    return {"user_id": user_id, "skills": skills, "count": len(skills)}


@router.post("/projects", status_code=status.HTTP_201_CREATED)
async def create_academic_project(data: AcademicProjectCreate):
    """Create academic project record."""
    try:
        result = await mental_ring_service.create_academic_project(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/projects/{user_id}")
async def get_user_projects(user_id: str):
    """Get projects for a user."""
    projects = await mental_ring_service.get_user_projects(user_id)
    return {"user_id": user_id, "projects": projects, "count": len(projects)}


@router.post("/goals", status_code=status.HTTP_201_CREATED)
async def create_learning_goal(data: LearningGoalCreate):
    """Set a learning goal."""
    try:
        result = await mental_ring_service.create_learning_goal(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/goals/{user_id}")
async def get_user_goals(user_id: str):
    """Get learning goals for a user."""
    goals = await mental_ring_service.get_user_goals(user_id)
    return {"user_id": user_id, "goals": goals, "count": len(goals)}


@router.get("/summary/{user_id}")
async def get_mental_ring_summary(user_id: str):
    """Get Mental Ring summary for a user."""
    summary = await mental_ring_service.get_mental_ring_summary(user_id)
    return summary
