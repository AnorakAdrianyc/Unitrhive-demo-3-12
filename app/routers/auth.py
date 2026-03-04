"""Authentication router for UniThrive.

Provides mock login/logout functionality for demo purposes.
"""

from datetime import datetime
from typing import Optional
import uuid

from fastapi import APIRouter, HTTPException, status

from app.schemas.user import UserLoginRequest, UserLoginResponse, User, UserCreate
from app.storage.json_storage import JsonUserStorage

router = APIRouter()
user_storage = JsonUserStorage()


@router.post("/mock-login", response_model=UserLoginResponse)
async def mock_login(request: UserLoginRequest):
    """Mock login endpoint for demo purposes.
    
    Creates a new user if email not found, or returns existing user.
    Supports anonymous login (no email required).
    
    Args:
        request: Login request with optional email and display name
        
    Returns:
        UserLoginResponse with user_id and session info
    """
    # Check if user exists by email
    existing_user = None
    if request.email:
        existing_user = await user_storage.get_by_email(request.email)
    
    if existing_user:
        return UserLoginResponse(
            user_id=existing_user.id,
            display_name=existing_user.display_name,
            is_anonymous=existing_user.is_anonymous,
            message=f"Welcome back, {existing_user.display_name}!"
        )
    
    # Create new user
    display_name = request.display_name or request.email.split("@")[0] if request.email else f"User_{uuid.uuid4().hex[:8]}"
    
    new_user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        display_name=display_name,
        is_anonymous=request.anonymous or not bool(request.email),
        created_at=datetime.now()
    )
    
    created_user = await user_storage.create(new_user)
    
    return UserLoginResponse(
        user_id=created_user.id,
        display_name=created_user.display_name,
        is_anonymous=created_user.is_anonymous,
        message=f"Welcome, {created_user.display_name}! Your account has been created."
    )


@router.post("/logout")
async def mock_logout(user_id: str):
    """Mock logout endpoint.
    
    Args:
        user_id: The user ID to logout
        
    Returns:
        Success message
    """
    # In a real implementation, this would invalidate session tokens
    return {"message": "Successfully logged out", "user_id": user_id}


@router.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get user by ID.
    
    Args:
        user_id: The user ID to retrieve
        
    Returns:
        User object if found
    """
    user = await user_storage.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


@router.get("/users")
async def list_users(limit: int = 100, offset: int = 0):
    """List all users (for admin/demo purposes).
    
    Args:
        limit: Maximum number of users to return
        offset: Number of users to skip
        
    Returns:
        List of users
    """
    users = await user_storage.get_all(limit=limit, offset=offset)
    return {
        "users": users,
        "count": len(users),
        "limit": limit,
        "offset": offset
    }
