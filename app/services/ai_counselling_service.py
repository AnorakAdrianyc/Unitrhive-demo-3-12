"""AI Counselling Assistant service for UniThrive.

Provides empathetic guidance and monitors for high-risk language patterns.
"""

import re
from datetime import datetime
from typing import List, Optional, Tuple

from app.schemas.ai_chat import (
    ChatMessage, ChatSession, ChatRequest, ChatResponse,
    MessageRole, RiskLevel
)
from app.config import settings
from app.storage.json_storage import JsonChatSessionStorage, JsonAlertStorage
from app.schemas.recommendations import RiskAlert


class AICounsellingService:
    """AI Counselling Assistant with risk detection."""
    
    def __init__(self):
        self.session_storage = JsonChatSessionStorage()
        self.alert_storage = JsonAlertStorage()
        self.high_risk_keywords = settings.high_risk_keywords
        self.medium_risk_keywords = settings.medium_risk_keywords
    
    def analyze_risk(self, message: str) -> Tuple[RiskLevel, List[str]]:
        """Analyze a message for risk indicators.
        
        Args:
            message: The user's message text
            
        Returns:
            Tuple of (risk_level, list_of_detected_flags)
        """
        message_lower = message.lower()
        flags = []
        
        # Check for high-risk keywords
        for keyword in self.high_risk_keywords:
            if keyword.lower() in message_lower:
                flags.append(f"HIGH_RISK_KEYWORD: {keyword}")
        
        # Check for medium-risk keywords
        for keyword in self.medium_risk_keywords:
            if keyword.lower() in message_lower:
                flags.append(f"MEDIUM_RISK_KEYWORD: {keyword}")
        
        # Determine risk level
        if any("HIGH_RISK" in f for f in flags):
            return RiskLevel.HIGH, flags
        elif any("MEDIUM_RISK" in f for f in flags):
            return RiskLevel.MEDIUM, flags
        
        return RiskLevel.NONE, flags
    
    def generate_response(self, user_message: str, risk_level: RiskLevel, flags: List[str]) -> Tuple[str, List[str]]:
        """Generate an empathetic AI response.
        
        Args:
            user_message: The user's message
            risk_level: Detected risk level
            flags: Risk flags detected
            
        Returns:
            Tuple of (response_text, suggestions)
        """
        suggestions = []
        
        # High-risk response
        if risk_level == RiskLevel.HIGH:
            response = (
                "I'm really concerned about what you've shared. Your wellbeing is important, "
                "and I want to make sure you get the support you need.\n\n"
                "Please consider reaching out immediately:\n"
                "- Campus Counseling Center: (555) 123-4567\n"
                "- Crisis Text Line: Text HOME to 741741\n"
                "- National Suicide Prevention Lifeline: 988\n\n"
                "You don't have to face this alone. Would you like me to help you connect with "
                "a counselor right now?"
            )
            suggestions = [
                "Contact campus counseling immediately",
                "Reach out to a trusted friend or family member",
                "Practice grounding techniques: 5-4-3-2-1 method",
                "Remove any means of self-harm from your immediate area"
            ]
            return response, suggestions
        
        # Medium-risk response
        if risk_level == RiskLevel.MEDIUM:
            response = (
                "I can hear that you're going through a really difficult time. "
                "It's completely valid to feel overwhelmed sometimes.\n\n"
                "Let's work through this together. Can you tell me more about what's "
                "been the hardest part for you recently? Sometimes putting it into words "
                "can help us find a path forward."
            )
            suggestions = [
                "Consider scheduling a counseling session",
                "Try a 5-minute mindfulness breathing exercise",
                "Journal about your feelings for 10 minutes",
                "Reach out to a friend for a chat"
            ]
            return response, suggestions
        
        # Standard empathetic responses based on content
        if any(word in user_message.lower() for word in ["stress", "stressed", "overwhelmed"]):
            response = (
                "It sounds like you're carrying a lot right now. Academic stress is real, "
                "and it's okay to acknowledge when things feel like too much.\n\n"
                "What specific aspect feels most overwhelming? Sometimes breaking it down "
                "can help us find manageable steps forward."
            )
            suggestions = [
                "Try the 4-7-8 breathing technique",
                "Take a 15-minute walk to clear your mind",
                "Make a list of priorities - focus on one at a time",
                "Check out the Time Management Assistant for study planning"
            ]
            return response, suggestions
        
        if any(word in user_message.lower() for word in ["sleep", "tired", "exhausted", "insomnia"]):
            response = (
                "Sleep struggles can really affect everything else in our lives. "
                "Your body and mind need rest to function well.\n\n"
                "What's your sleep routine been like lately? Sometimes small adjustments "
                "to our evening habits can make a difference."
            )
            suggestions = [
                "Try to go to bed 30 minutes earlier tonight",
                "Avoid screens 1 hour before bed",
                "Create a relaxing bedtime routine",
                "Track your sleep patterns in the Physical Ring"
            ]
            return response, suggestions
        
        if any(word in user_message.lower() for word in ["lonely", "isolated", "alone", "no friends"]):
            response = (
                "Feeling disconnected can be really painful. It's a common experience, "
                "especially during busy academic periods, but that doesn't make it easier.\n\n"
                "What kinds of connections are you missing most? Understanding that "
                "might help us find ways to rebuild those connections."
            )
            suggestions = [
                "Join a campus club or study group",
                "Attend one of the social events in your recommendations",
                "Start a conversation with someone in your class",
                "Consider the Peer Support Circle"
            ]
            return response, suggestions
        
        # Default response
        response = (
            "Thank you for sharing that with me. I'm here to support you through "
            "whatever you're experiencing.\n\n"
            "How are you feeling overall today? I'm here to listen and help you "
            "find resources or strategies that might help."
        )
        suggestions = [
            "Check your 3-Ring dashboard for personalized insights",
            "Explore opportunities in your recommendations",
            "Complete your daily check-in to track your wellbeing",
            "Try one of the self-discovery assessments"
        ]
        return response, suggestions
    
    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message and generate a response.
        
        Args:
            request: Chat request with user_id and message
            
        Returns:
            ChatResponse with AI response and risk assessment
        """
        user_id = request.user_id
        message_text = request.message
        session_id = request.session_id
        
        # Analyze risk
        risk_level, flags = self.analyze_risk(message_text)
        
        # Generate AI response
        response_text, suggestions = self.generate_response(message_text, risk_level, flags)
        
        # Get or create session
        session = None
        if session_id:
            session = await self.session_storage.get_by_id(session_id)
        
        if not session:
            # Create new session
            now = datetime.now()
            session = ChatSession(
                session_id="",  # Will be generated
                user_id=user_id,
                messages=[],
                detected_risk_level=risk_level,
                created_at=now,
                updated_at=now
            )
            session = await self.session_storage.create(session)
        
        # Add user message to session
        user_message = ChatMessage(
            role=MessageRole.USER,
            content=message_text,
            timestamp=datetime.now(),
            risk_flags=flags,
            detected_risk_level=risk_level
        )
        await self.session_storage.add_message(session.id, user_message)
        
        # Add AI response to session
        ai_message = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=response_text,
            timestamp=datetime.now(),
            risk_flags=[],
            detected_risk_level=RiskLevel.NONE
        )
        await self.session_storage.add_message(session.id, ai_message)
        
        # Create alert for high-risk messages
        if risk_level == RiskLevel.HIGH:
            alert = RiskAlert(
                id="",
                user_id=user_id,
                risk_level="high",
                reason=f"High-risk language detected in chat: {', '.join(flags)}",
                triggered_at=datetime.now(),
                escalated_to_counselor=False,
                suggested_actions=[
                    "Immediate counselor follow-up recommended",
                    "Review chat session for context",
                    "Consider wellness check"
                ]
            )
            await self.alert_storage.create(alert)
        
        return ChatResponse(
            session_id=session.id,
            response=response_text,
            detected_risk_level=risk_level,
            risk_flags=flags,
            suggestions=suggestions,
            timestamp=datetime.now()
        )
    
    async def get_chat_history(self, user_id: str, limit: int = 10) -> List[ChatSession]:
        """Get chat history for a user.
        
        Args:
            user_id: The user ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of chat sessions
        """
        return await self.session_storage.get_by_user_id(user_id, limit=limit)
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a specific chat session.
        
        Args:
            session_id: The session ID
            
        Returns:
            The chat session or None
        """
        return await self.session_storage.get_by_id(session_id)


# Global service instance
ai_counselling_service = AICounsellingService()
