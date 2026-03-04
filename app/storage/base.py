"""Abstract base storage interface for UniThrive.

This module defines the interface that all storage implementations must follow.
It allows easy swapping between JSON storage (for prototype) and database storage (for production).
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Optional, TypeVar, Generic, Dict, Any

T = TypeVar("T")


class BaseStorage(ABC, Generic[T]):
    """Abstract base class for all storage implementations.
    
    This interface allows the application to work with any storage backend
    (JSON files, SQLite, PostgreSQL, etc.) without changing business logic.
    """
    
    @abstractmethod
    async def create(self, item: T) -> T:
        """Create a new item in storage.
        
        Args:
            item: The item to create
            
        Returns:
            The created item with generated ID
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[T]:
        """Get an item by its ID.
        
        Args:
            item_id: The unique identifier of the item
            
        Returns:
            The item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all items with pagination.
        
        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip
            
        Returns:
            List of items
        """
        pass
    
    @abstractmethod
    async def update(self, item_id: str, item: T) -> Optional[T]:
        """Update an existing item.
        
        Args:
            item_id: The ID of the item to update
            item: The updated item data
            
        Returns:
            The updated item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """Delete an item by ID.
        
        Args:
            item_id: The ID of the item to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def query(self, filters: Dict[str, Any]) -> List[T]:
        """Query items by filters.
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            
        Returns:
            List of matching items
        """
        pass


class UserStorage(BaseStorage, ABC):
    """Storage interface for User data."""
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Any]:
        """Get user by email address.
        
        Args:
            email: The email to search for
            
        Returns:
            The user if found, None otherwise
        """
        pass


class CheckInStorage(BaseStorage, ABC):
    """Storage interface for Check-in data."""
    
    @abstractmethod
    async def get_by_user_id(
        self, 
        user_id: str, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[Any]:
        """Get check-ins for a specific user with optional date range.
        
        Args:
            user_id: The user ID to filter by
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of results
            
        Returns:
            List of check-ins
        """
        pass
    
    @abstractmethod
    async def get_by_user_and_date(self, user_id: str, date: date) -> List[Any]:
        """Get check-ins for a user on a specific date.
        
        Args:
            user_id: The user ID
            date: The date to query
            
        Returns:
            List of check-ins for that date
        """
        pass


class ActivityStorage(BaseStorage, ABC):
    """Storage interface for Activity data."""
    
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        activity_type: Optional[str] = None
    ) -> List[Any]:
        """Get activities for a specific user with optional filters.
        
        Args:
            user_id: The user ID to filter by
            start_date: Optional start date filter
            end_date: Optional end date filter
            activity_type: Optional activity type filter
            
        Returns:
            List of activities
        """
        pass


class RingScoreStorage(BaseStorage, ABC):
    """Storage interface for Ring Score data."""
    
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Any]:
        """Get ring scores for a user with optional date range.
        
        Args:
            user_id: The user ID
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of daily ring scores
        """
        pass
    
    @abstractmethod
    async def get_latest_for_user(self, user_id: str) -> Optional[Any]:
        """Get the most recent ring scores for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            The latest ring score entry
        """
        pass


class WeeklySummaryStorage(BaseStorage, ABC):
    """Storage interface for Weekly Summary data."""
    
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: str,
        week_start: Optional[date] = None
    ) -> List[Any]:
        """Get weekly summaries for a user.
        
        Args:
            user_id: The user ID
            week_start: Optional specific week to query
            
        Returns:
            List of weekly summaries
        """
        pass
    
    @abstractmethod
    async def get_latest_for_user(self, user_id: str) -> Optional[Any]:
        """Get the most recent weekly summary for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            The latest weekly summary
        """
        pass


class AlertStorage(BaseStorage, ABC):
    """Storage interface for Alert data."""
    
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: str,
        active_only: bool = True,
        risk_level: Optional[str] = None
    ) -> List[Any]:
        """Get alerts for a user.
        
        Args:
            user_id: The user ID
            active_only: If True, only return unacknowledged alerts
            risk_level: Optional filter by risk level
            
        Returns:
            List of alerts
        """
        pass
    
    @abstractmethod
    async def acknowledge(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged.
        
        Args:
            alert_id: The alert ID
            
        Returns:
            True if acknowledged, False if not found
        """
        pass


class RecommendationStorage(BaseStorage, ABC):
    """Storage interface for Recommendation data."""
    
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: str,
        unread_only: bool = False,
        ring_target: Optional[str] = None
    ) -> List[Any]:
        """Get recommendations for a user.
        
        Args:
            user_id: The user ID
            unread_only: If True, only return unviewed recommendations
            ring_target: Optional filter by target ring
            
        Returns:
            List of recommendations
        """
        pass


class OpportunityStorage(BaseStorage, ABC):
    """Storage interface for Opportunity data."""
    
    @abstractmethod
    async def get_by_tags(self, tags: List[str]) -> List[Any]:
        """Get opportunities matching any of the given tags.
        
        Args:
            tags: List of tags to match
            
        Returns:
            List of matching opportunities
        """
        pass
    
    @abstractmethod
    async def get_by_campus(self, campus: str) -> List[Any]:
        """Get opportunities for a specific campus.
        
        Args:
            campus: The campus name
            
        Returns:
            List of opportunities
        """
        pass


class ChatSessionStorage(BaseStorage, ABC):
    """Storage interface for Chat Session data."""
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 10) -> List[Any]:
        """Get chat sessions for a user.
        
        Args:
            user_id: The user ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of chat sessions
        """
        pass
    
    @abstractmethod
    async def add_message(self, session_id: str, message: Any) -> bool:
        """Add a message to an existing session.
        
        Args:
            session_id: The session ID
            message: The message to add
            
        Returns:
            True if added, False if session not found
        """
        pass
