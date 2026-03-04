"""AI Assistant router for UniThrive.

Handles AI Counselling and Time Management Assistant endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.ai_chat import (
    ChatRequest, ChatResponse, TimePlanRequest, TimePlanResponse,
    ScheduleOptimizationRequest, TimeManagementSuggestionsResponse
)
from app.services.ai_counselling_service import ai_counselling_service
from app.services.time_management_service import time_management_service

router = APIRouter()


@router.post("/counselling/chat", response_model=ChatResponse)
async def counselling_chat(request: ChatRequest):
    """Chat with the AI Counselling Assistant.
    
    The assistant provides empathetic guidance and monitors for
    high-risk language patterns that may require counselor intervention.
    
    Args:
        request: ChatRequest with user_id and message
        
    Returns:
        ChatResponse with AI response and risk assessment
    """
    try:
        response = await ai_counselling_service.process_chat(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat: {str(e)}"
        )


@router.get("/counselling/sessions/{user_id}")
async def get_chat_sessions(user_id: str, limit: int = 10):
    """Get chat session history for a user.
    
    Args:
        user_id: The user ID
        limit: Maximum number of sessions to return
        
    Returns:
        List of chat sessions
    """
    sessions = await ai_counselling_service.get_chat_history(user_id, limit=limit)
    return {
        "user_id": user_id,
        "sessions": sessions,
        "count": len(sessions)
    }


@router.get("/counselling/session/{session_id}")
async def get_chat_session(session_id: str):
    """Get a specific chat session.
    
    Args:
        session_id: The session ID
        
    Returns:
        Chat session with all messages
    """
    session = await ai_counselling_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    return session


@router.post("/timemanagement/plan", response_model=TimePlanResponse)
async def generate_time_plan(request: TimePlanRequest):
    """Generate a personalized study and exam schedule.
    
    Creates an optimized time management plan based on:
    - Upcoming exam dates
    - Preferred study hours
    - Historical productivity patterns
    - Stress and sleep data
    
    Args:
        request: TimePlanRequest with exam schedule and preferences
        
    Returns:
        TimePlanResponse with generated plan and recommendations
    """
    try:
        response = await time_management_service.generate_time_plan(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate time plan: {str(e)}"
        )


@router.post("/timemanagement/optimize")
async def optimize_schedule(request: ScheduleOptimizationRequest):
    """Optimize an existing schedule.
    
    Args:
        request: ScheduleOptimizationRequest with current plan and issues
        
    Returns:
        Optimized plan recommendations
    """
    # For demo purposes, return general optimization tips
    return {
        "user_id": request.user_id,
        "plan_id": request.current_plan_id,
        "optimizations": [
            "Consider moving heavy study sessions to morning hours when energy is highest",
            "Add buffer time between subjects to prevent cognitive fatigue",
            "Schedule review sessions using spaced repetition (1 day, 3 days, 7 days)",
            "Block out time for meals and exercise to maintain energy levels"
        ],
        "prioritized_issues": request.issues[:3] if request.issues else [],
        "goals": request.goals
    }


@router.get("/timemanagement/suggestions/{user_id}", response_model=TimeManagementSuggestionsResponse)
async def get_time_suggestions(user_id: str):
    """Get personalized time management suggestions.
    
    Analyzes user's check-in patterns and activity data to provide
    tailored recommendations for improving time management.
    
    Args:
        user_id: The user ID
        
    Returns:
        TimeManagementSuggestionsResponse with personalized suggestions
    """
    try:
        response = await time_management_service.get_suggestions(user_id)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )


@router.get("/timemanagement/tips/{user_id}")
async def get_time_management_tips(user_id: str):
    """Get general time management tips.
    
    Args:
        user_id: The user ID
        
    Returns:
        List of time management tips
    """
    tips = [
        {
            "title": "The 2-Minute Rule",
            "description": "If a task takes less than 2 minutes, do it immediately rather than adding it to your to-do list.",
            "category": "productivity"
        },
        {
            "title": "Eat the Frog",
            "description": "Tackle your most challenging or important task first thing in the morning when your energy is highest.",
            "category": "prioritization"
        },
        {
            "title": "Time Blocking",
            "description": "Schedule specific blocks of time for different activities. This reduces context switching and improves focus.",
            "category": "scheduling"
        },
        {
            "title": "The Pomodoro Technique",
            "description": "Work in focused 25-minute intervals followed by 5-minute breaks. After 4 cycles, take a longer 15-30 minute break.",
            "category": "focus"
        },
        {
            "title": "Review and Reflect",
            "description": "Spend 10 minutes at the end of each day reviewing what you accomplished and planning tomorrow's priorities.",
            "category": "reflection"
        }
    ]
    
    return {
        "user_id": user_id,
        "tips": tips,
        "total": len(tips)
    }
