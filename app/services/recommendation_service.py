"""Recommendation Service for UniThrive.

Generates personalized recommendations using the decision engine.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any

from app.schemas.recommendations import Recommendation, Opportunity, RiskAlert
from app.decision_engine.features import feature_extractor
from app.decision_engine.ranker import recommendation_engine
from app.storage.json_storage import (
    JsonOpportunityStorage, JsonRecommendationStorage,
    JsonCheckInStorage, JsonActivityStorage, JsonRingScoreStorage
)


class RecommendationService:
    """Service for generating and managing recommendations."""
    
    def __init__(self):
        self.opportunity_storage = JsonOpportunityStorage()
        self.recommendation_storage = JsonRecommendationStorage()
        self.checkin_storage = JsonCheckInStorage()
        self.activity_storage = JsonActivityStorage()
        self.ring_score_storage = JsonRingScoreStorage()
    
    async def get_available_opportunities(
        self,
        campus: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Opportunity]:
        """Get available opportunities with optional filtering.
        
        Args:
            campus: Optional campus filter
            tags: Optional tags filter
            
        Returns:
            List of opportunities
        """
        if campus:
            return await self.opportunity_storage.get_by_campus(campus)
        elif tags:
            return await self.opportunity_storage.get_by_tags(tags)
        else:
            return await self.opportunity_storage.get_all(limit=100)
    
    async def generate_recommendations(
        self,
        user_id: str,
        top_k: int = 5
    ) -> List[Recommendation]:
        """Generate personalized recommendations for a user.
        
        Args:
            user_id: The user ID
            top_k: Number of recommendations to generate
            
        Returns:
            List of recommendations
        """
        # Get user data
        end_date = date.today()
        start_date = end_date - timedelta(days=14)
        
        checkins = await self.checkin_storage.get_by_user_id(
            user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        activities = await self.activity_storage.get_by_user_id(
            user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        ring_scores = await self.ring_score_storage.get_by_user_id(
            user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Extract features
        checkin_features = feature_extractor.extract_checkin_features(checkins)
        activity_features = feature_extractor.extract_activity_features(activities)
        ring_score_features = feature_extractor.extract_ring_score_features(ring_scores)
        
        # Combine features
        features = {
            **checkin_features,
            **activity_features,
            **ring_score_features
        }
        
        # Get opportunities
        opportunities = await self.get_available_opportunities()
        
        # Generate recommendations
        recommendations = await recommendation_engine.generate_recommendations(
            user_id=user_id,
            features=features,
            opportunities=opportunities,
            top_k=top_k
        )
        
        # Store recommendations
        for rec in recommendations:
            await self.recommendation_storage.create(rec)
        
        return recommendations
    
    async def get_user_recommendations(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 10
    ) -> List[Recommendation]:
        """Get recommendations for a user.
        
        Args:
            user_id: The user ID
            unread_only: If True, only return unviewed recommendations
            limit: Maximum number to return
            
        Returns:
            List of recommendations
        """
        recommendations = await self.recommendation_storage.get_by_user_id(
            user_id,
            unread_only=unread_only
        )
        return recommendations[:limit]
    
    async def mark_recommendation_viewed(self, recommendation_id: str) -> bool:
        """Mark a recommendation as viewed.
        
        Args:
            recommendation_id: The recommendation ID
            
        Returns:
            True if successful
        """
        rec = await self.recommendation_storage.get_by_id(recommendation_id)
        if not rec:
            return False
        
        rec.is_viewed = True
        await self.recommendation_storage.update(recommendation_id, rec)
        return True
    
    async def accept_recommendation(
        self,
        recommendation_id: str,
        accepted: bool = True
    ) -> bool:
        """Mark whether user accepts a recommendation.
        
        Args:
            recommendation_id: The recommendation ID
            accepted: Whether user accepts (True) or declines (False)
            
        Returns:
            True if successful
        """
        rec = await self.recommendation_storage.get_by_id(recommendation_id)
        if not rec:
            return False
        
        rec.is_accepted = accepted
        await self.recommendation_storage.update(recommendation_id, rec)
        return True
    
    async def generate_spotlight_opportunity(
        self,
        user_id: str,
        features: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a spotlight opportunity recommendation.
        
        Args:
            user_id: The user ID
            features: Optional pre-computed features
            
        Returns:
            Spotlight opportunity description
        """
        if not features:
            # Compute features
            end_date = date.today()
            start_date = end_date - timedelta(days=14)
            
            checkins = await self.checkin_storage.get_by_user_id(user_id, start_date, end_date)
            ring_scores = await self.ring_score_storage.get_by_user_id(user_id, start_date, end_date)
            
            features = {
                **feature_extractor.extract_checkin_features(checkins),
                **feature_extractor.extract_ring_score_features(ring_scores)
            }
        
        weakest_ring = features.get("weakest_ring")
        
        # Get opportunities targeting weakest ring
        opportunities = await self.get_available_opportunities()
        ring_opportunities = [
            opp for opp in opportunities
            if self._matches_ring(opp, weakest_ring)
        ]
        
        if ring_opportunities:
            # Get highest scoring one
            from app.decision_engine.perspectives import perspective_scorer
            
            best_opp = None
            best_score = 0
            
            for opp in ring_opportunities[:5]:
                perspectives = perspective_scorer.score_all_perspectives(features, opp)
                score = sum(perspectives.values()) / len(perspectives)
                if score > best_score:
                    best_score = score
                    best_opp = opp
            
            if best_opp:
                return f"Based on your {weakest_ring} ring being your focus area, we recommend: {best_opp.title}"
        
        # Default message
        if weakest_ring == "psychological":
            return "Consider exploring mindfulness resources to support your psychological wellbeing this week."
        elif weakest_ring == "physical":
            return "Try adding a 20-minute walk to your daily routine to boost your physical health."
        elif weakest_ring == "mental":
            return "Look for a workshop or skill-building activity to strengthen your mental ring."
        
        return "Explore the opportunities section for personalized recommendations!"
    
    def _matches_ring(self, opportunity: Opportunity, ring: Optional[str]) -> bool:
        """Check if an opportunity matches a target ring."""
        if not ring:
            return True
        
        tags = [t.lower() for t in opportunity.tags]
        
        if ring == "psychological":
            return any(t in tags for t in ["stress", "mindfulness", "wellbeing", "social", "mood"])
        elif ring == "physical":
            return any(t in tags for t in ["exercise", "fitness", "sleep", "activity", "health"])
        elif ring == "mental":
            return any(t in tags for t in ["study", "course", "skill", "learning", "workshop"])
        
        return True


# Global instance
recommendation_service = RecommendationService()
