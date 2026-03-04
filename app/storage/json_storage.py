"""JSON file storage implementation for UniThrive.

This module provides a concrete implementation of the storage interfaces
using JSON files for data persistence. Suitable for prototyping and small deployments.
"""

import json
import os
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Callable
from dateutil import parser as date_parser

from app.storage.base import (
    UserStorage, CheckInStorage, ActivityStorage, RingScoreStorage,
    WeeklySummaryStorage, AlertStorage, RecommendationStorage,
    OpportunityStorage, ChatSessionStorage
)

T = TypeVar("T")


def _serialize_datetime(obj: Any) -> Any:
    """Helper function to serialize datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _deserialize_dates(data: Any) -> Any:
    """Helper function to deserialize date strings back to datetime/date objects."""
    if isinstance(data, dict):
        return {k: _deserialize_dates(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_deserialize_dates(item) for item in data]
    elif isinstance(data, str):
        # Try to parse as datetime or date
        try:
            if 'T' in data or ' ' in data:
                return date_parser.parse(data)
            elif len(data) == 10 and data.count('-') == 2:
                return date.fromisoformat(data)
        except (ValueError, TypeError):
            pass
        return data
    return data


class JsonStorage:
    """Base JSON storage class with common CRUD operations."""
    
    def __init__(self, data_dir: str, filename: str, model_class: Type[T]):
        """Initialize JSON storage.
        
        Args:
            data_dir: Directory to store JSON files
            filename: Name of the JSON file
            model_class: Pydantic model class for type conversion
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = self.data_dir / filename
        self.model_class = model_class
        self._data_cache: Dict[str, Any] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """Load data from JSON file into memory cache."""
        if self.filepath.exists():
            with open(self.filepath, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                self._data_cache = _deserialize_dates(raw_data)
        else:
            self._data_cache = {}
    
    def _save_data(self) -> None:
        """Save data from memory cache to JSON file."""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self._data_cache, f, default=_serialize_datetime, indent=2, ensure_ascii=False)
    
    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4())
    
    async def create(self, item: T) -> T:
        """Create a new item."""
        # Convert to dict if it's a Pydantic model
        if hasattr(item, 'model_dump'):
            item_dict = item.model_dump()
        elif hasattr(item, 'dict'):
            item_dict = item.dict()
        else:
            item_dict = dict(item)
        
        # Generate ID if not present
        if 'id' not in item_dict or not item_dict['id']:
            item_dict['id'] = self._generate_id()
        
        # Store in cache
        self._data_cache[item_dict['id']] = item_dict
        self._save_data()
        
        # Return the item with ID
        return self.model_class(**item_dict)
    
    async def get_by_id(self, item_id: str) -> Optional[T]:
        """Get item by ID."""
        data = self._data_cache.get(item_id)
        if data:
            return self.model_class(**data)
        return None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all items with pagination."""
        items = list(self._data_cache.values())
        items = items[offset:offset + limit]
        return [self.model_class(**item) for item in items]
    
    async def update(self, item_id: str, item: T) -> Optional[T]:
        """Update an existing item."""
        if item_id not in self._data_cache:
            return None
        
        # Convert to dict
        if hasattr(item, 'model_dump'):
            item_dict = item.model_dump()
        elif hasattr(item, 'dict'):
            item_dict = item.dict()
        else:
            item_dict = dict(item)
        
        item_dict['id'] = item_id
        self._data_cache[item_id] = item_dict
        self._save_data()
        
        return self.model_class(**item_dict)
    
    async def delete(self, item_id: str) -> bool:
        """Delete an item."""
        if item_id in self._data_cache:
            del self._data_cache[item_id]
            self._save_data()
            return True
        return False
    
    async def query(self, filters: Dict[str, Any]) -> List[T]:
        """Query items by filters."""
        results = []
        for item in self._data_cache.values():
            match = True
            for key, value in filters.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                results.append(self.model_class(**item))
        return results


class JsonUserStorage(JsonStorage, UserStorage):
    """JSON storage implementation for Users."""
    
    def __init__(self, data_dir: str = "data"):
        from app.schemas.user import User
        super().__init__(data_dir, "users.json", User)
    
    async def get_by_email(self, email: str) -> Optional[Any]:
        """Get user by email."""
        for item in self._data_cache.values():
            if item.get('email') == email:
                return self.model_class(**item)
        return None


class JsonCheckInStorage(JsonStorage, CheckInStorage):
    """JSON storage implementation for Check-ins."""
    
    def __init__(self, data_dir: str = "data"):
        from app.schemas.checkin import CheckIn
        super().__init__(data_dir, "checkins.json", CheckIn)
    
    async def get_by_user_id(
        self, 
        user_id: str, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[Any]:
        """Get check-ins for a user with optional date range."""
        results = []
        for item in self._data_cache.values():
            if item.get('user_id') != user_id:
                continue
            
            item_date = item.get('timestamp')
            if isinstance(item_date, str):
                item_date = date_parser.parse(item_date)
            if isinstance(item_date, datetime):
                item_date = item_date.date()
            
            if start_date and item_date and item_date < start_date:
                continue
            if end_date and item_date and item_date > end_date:
                continue
            
            results.append(self.model_class(**item))
        
        # Sort by timestamp descending
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:limit]
    
    async def get_by_user_and_date(self, user_id: str, date: date) -> List[Any]:
        """Get check-ins for a user on a specific date."""
        results = []
        for item in self._data_cache.values():
            if item.get('user_id') != user_id:
                continue
            
            item_date = item.get('timestamp')
            if isinstance(item_date, str):
                item_date = date_parser.parse(item_date)
            if isinstance(item_date, datetime):
                item_date = item_date.date()
            
            if item_date == date:
                results.append(self.model_class(**item))
        
        return results


class JsonActivityStorage(JsonStorage, ActivityStorage):
    """JSON storage implementation for Activities."""
    
    def __init__(self, data_dir: str = "data"):
        from app.schemas.checkin import ActivityRecord
        super().__init__(data_dir, "activities.json", ActivityRecord)
    
    async def get_by_user_id(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        activity_type: Optional[str] = None
    ) -> List[Any]:
        """Get activities for a user with optional filters."""
        results = []
        for item in self._data_cache.values():
            if item.get('user_id') != user_id:
                continue
            
            if activity_type and item.get('type') != activity_type:
                continue
            
            item_date = item.get('date')
            if isinstance(item_date, str):
                item_date = date.fromisoformat(item_date)
            
            if start_date and item_date and item_date < start_date:
                continue
            if end_date and item_date and item_date > end_date:
                continue
            
            results.append(self.model_class(**item))
        
        return results


class JsonRingScoreStorage(JsonStorage, RingScoreStorage):
    """JSON storage implementation for Ring Scores."""
    
    def __init__(self, data_dir: str = "data"):
        from app.schemas.rings import DailyRingScore
        super().__init__(data_dir, "daily_ring_scores.json", DailyRingScore)
    
    async def get_by_user_id(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Any]:
        """Get ring scores for a user with optional date range."""
        results = []
        for item in self._data_cache.values():
            if item.get('user_id') != user_id:
                continue
            
            item_date = item.get('date')
            if isinstance(item_date, str):
                item_date = date.fromisoformat(item_date)
            
            if start_date and item_date and item_date < start_date:
                continue
            if end_date and item_date and item_date > end_date:
                continue
            
            results.append(self.model_class(**item))
        
        # Sort by date descending
        results.sort(key=lambda x: x.date, reverse=True)
        return results
    
    async def get_latest_for_user(self, user_id: str) -> Optional[Any]:
        """Get the most recent ring scores for a user."""
        results = await self.get_by_user_id(user_id)
        return results[0] if results else None


class JsonWeeklySummaryStorage(JsonStorage, WeeklySummaryStorage):
    """JSON storage implementation for Weekly Summaries."""
    
    def __init__(self, data_dir: str = "data"):
        from app.schemas.rings import WeeklySummary
        super().__init__(data_dir, "weekly_summaries.json", WeeklySummary)
    
    async def get_by_user_id(
        self,
        user_id: str,
        week_start: Optional[date] = None
    ) -> List[Any]:
        """Get weekly summaries for a user."""
        results = []
        for item in self._data_cache.values():
            if item.get('user_id') != user_id:
                continue
            
            if week_start:
                item_week = item.get('week_start')
                if isinstance(item_week, str):
                    item_week = date.fromisoformat(item_week)
                if item_week != week_start:
                    continue
            
            results.append(self.model_class(**item))
        
        # Sort by week_start descending
        results.sort(key=lambda x: x.week_start, reverse=True)
        return results
    
    async def get_latest_for_user(self, user_id: str) -> Optional[Any]:
        """Get the most recent weekly summary for a user."""
        results = await self.get_by_user_id(user_id)
        return results[0] if results else None


class JsonAlertStorage(JsonStorage, AlertStorage):
    """JSON storage implementation for Alerts."""
    
    def __init__(self, data_dir: str = "data"):
        from app.schemas.recommendations import RiskAlert
        super().__init__(data_dir, "alerts.json", RiskAlert)
    
    async def get_by_user_id(
        self,
        user_id: str,
        active_only: bool = True,
        risk_level: Optional[str] = None
    ) -> List[Any]:
        """Get alerts for a user."""
        results = []
        for item in self._data_cache.values():
            if item.get('user_id') != user_id:
                continue
            
            if active_only and item.get('is_acknowledged', False):
                continue
            
            if risk_level and item.get('risk_level') != risk_level:
                continue
            
            results.append(self.model_class(**item))
        
        # Sort by triggered_at descending
        results.sort(key=lambda x: x.triggered_at, reverse=True)
        return results
    
    async def acknowledge(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged."""
        if alert_id not in self._data_cache:
            return False
        
        from datetime import datetime
        self._data_cache[alert_id]['is_acknowledged'] = True
        self._data_cache[alert_id]['acknowledged_at'] = datetime.now()
        self._save_data()
        return True


class JsonRecommendationStorage(JsonStorage, RecommendationStorage):
    """JSON storage implementation for Recommendations."""
    
    def __init__(self, data_dir: str = "data"):
        from app.schemas.recommendations import Recommendation
        super().__init__(data_dir, "recommendations.json", Recommendation)
    
    async def get_by_user_id(
        self,
        user_id: str,
        unread_only: bool = False,
        ring_target: Optional[str] = None
    ) -> List[Any]:
        """Get recommendations for a user."""
        results = []
        for item in self._data_cache.values():
            if item.get('user_id') != user_id:
                continue
            
            if unread_only and item.get('is_viewed', False):
                continue
            
            if ring_target and item.get('ring_target') != ring_target:
                continue
            
            results.append(self.model_class(**item))
        
        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        return results


class JsonOpportunityStorage(JsonStorage, OpportunityStorage):
    """JSON storage implementation for Opportunities."""
    
    def __init__(self, data_dir: str = "data"):
        from app.schemas.recommendations import Opportunity
        super().__init__(data_dir, "opportunities.json", Opportunity)
    
    async def get_by_tags(self, tags: List[str]) -> List[Any]:
        """Get opportunities matching any of the given tags."""
        results = []
        for item in self._data_cache.values():
            item_tags = item.get('tags', [])
            if any(tag in item_tags for tag in tags):
                results.append(self.model_class(**item))
        return results
    
    async def get_by_campus(self, campus: str) -> List[Any]:
        """Get opportunities for a specific campus."""
        results = []
        for item in self._data_cache.values():
            if item.get('campus') == campus:
                results.append(self.model_class(**item))
        return results


class JsonChatSessionStorage(JsonStorage, ChatSessionStorage):
    """JSON storage implementation for Chat Sessions."""
    
    def __init__(self, data_dir: str = "data"):
        from app.schemas.ai_chat import ChatSession
        super().__init__(data_dir, "chat_sessions.json", ChatSession)
    
    async def get_by_user_id(self, user_id: str, limit: int = 10) -> List[Any]:
        """Get chat sessions for a user."""
        results = []
        for item in self._data_cache.values():
            if item.get('user_id') != user_id:
                continue
            results.append(self.model_class(**item))
        
        # Sort by updated_at descending
        results.sort(key=lambda x: x.updated_at, reverse=True)
        return results[:limit]
    
    async def add_message(self, session_id: str, message: Any) -> bool:
        """Add a message to an existing session."""
        if session_id not in self._data_cache:
            return False
        
        if 'messages' not in self._data_cache[session_id]:
            self._data_cache[session_id]['messages'] = []
        
        # Convert message to dict
        if hasattr(message, 'model_dump'):
            msg_dict = message.model_dump()
        elif hasattr(message, 'dict'):
            msg_dict = message.dict()
        else:
            msg_dict = dict(message)
        
        self._data_cache[session_id]['messages'].append(msg_dict)
        self._data_cache[session_id]['updated_at'] = datetime.now()
        self._save_data()
        return True


# Ring-specific storage classes
class JsonMentalRingStorage(JsonStorage):
    """JSON storage for Mental Ring data."""
    
    def __init__(self, data_dir: str = "data", entity_type: str = "courses"):
        self.entity_type = entity_type
        filename = f"mental_{entity_type}.json"
        super().__init__(data_dir, filename, dict)
    
    async def get_by_user_id(self, user_id: str) -> List[Dict]:
        """Get all records for a user."""
        return [item for item in self._data_cache.values() if item.get('user_id') == user_id]


class JsonPsychologicalRingStorage(JsonStorage):
    """JSON storage for Psychological Ring data."""
    
    def __init__(self, data_dir: str = "data", entity_type: str = "assessments"):
        self.entity_type = entity_type
        filename = f"psych_{entity_type}.json"
        super().__init__(data_dir, filename, dict)
    
    async def get_by_user_id(self, user_id: str) -> List[Dict]:
        """Get all records for a user."""
        return [item for item in self._data_cache.values() if item.get('user_id') == user_id]


class JsonPhysicalRingStorage(JsonStorage):
    """JSON storage for Physical Ring data."""
    
    def __init__(self, data_dir: str = "data", entity_type: str = "sleep"):
        self.entity_type = entity_type
        filename = f"physical_{entity_type}.json"
        super().__init__(data_dir, filename, dict)
    
    async def get_by_user_id(self, user_id: str) -> List[Dict]:
        """Get all records for a user."""
        return [item for item in self._data_cache.values() if item.get('user_id') == user_id]
