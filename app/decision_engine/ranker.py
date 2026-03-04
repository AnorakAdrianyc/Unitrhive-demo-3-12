"""Core ranking module for UniThrive decision engine.

Combines multi-perspective scores into final rankings.
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime

from app.schemas.recommendations import Opportunity, Recommendation
from app.decision_engine.perspectives import perspective_scorer


class CoreRanker:
    """Core ranking algorithm combining multi-perspective scores."""
    
    def __init__(self):
        # Default weights for each perspective
        self.perspective_weights = {
            "efficiency": 0.25,
            "wellbeing": 0.30,
            "physical": 0.25,
            "learning": 0.20
        }
    
    def rank_opportunities(
        self,
        features: Dict[str, Any],
        opportunities: List[Opportunity],
        top_k: int = 5
    ) -> List[Tuple[Opportunity, float, str]]:
        """Rank opportunities based on user features.
        
        Args:
            features: User features from feature extractor
            opportunities: List of opportunities to rank
            top_k: Number of top results to return
            
        Returns:
            List of (opportunity, score, explanation) tuples
        """
        scored_opportunities = []
        
        for opp in opportunities:
            # Get perspective scores
            perspectives = perspective_scorer.score_all_perspectives(features, opp)
            
            # Calculate weighted final score
            final_score = sum(
                perspectives[p] * self.perspective_weights[p]
                for p in perspectives
            )
            
            # Determine target ring based on highest perspective
            target_ring = self._determine_target_ring(features, perspectives, opp)
            
            # Generate explanation
            explanation = self._generate_explanation(features, opp, perspectives, target_ring)
            
            scored_opportunities.append((opp, final_score, target_ring, explanation))
        
        # Sort by score descending
        scored_opportunities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k with explanation
        return [(opp, score, explanation) for opp, score, ring, explanation in scored_opportunities[:top_k]]
    
    def _determine_target_ring(
        self,
        features: Dict[str, Any],
        perspectives: Dict[str, float],
        opportunity: Opportunity
    ) -> str:
        """Determine which ring this opportunity primarily targets.
        
        Args:
            features: User features
            perspectives: Perspective scores
            opportunity: The opportunity
            
        Returns:
            Ring name: "mental", "psychological", or "physical"
        """
        # Check opportunity tags first
        tags = [t.lower() for t in opportunity.tags]
        
        if any(t in ["stress", "mindfulness", "mood", "wellbeing", "social"] for t in tags):
            return "psychological"
        
        if any(t in ["exercise", "fitness", "sleep", "activity", "health"] for t in tags):
            return "physical"
        
        if any(t in ["study", "course", "skill", "learning", "workshop"] for t in tags):
            return "mental"
        
        # Check opportunity type
        if opportunity.type in ["counselling", "community"]:
            return "psychological"
        
        if opportunity.type == "activity":
            return "physical"
        
        if opportunity.type in ["workshop", "course"]:
            return "mental"
        
        # Check weakest ring
        weakest = features.get("weakest_ring")
        if weakest:
            return weakest
        
        # Default to highest perspective score
        return max(perspectives, key=perspectives.get)
    
    def _generate_explanation(
        self,
        features: Dict[str, Any],
        opportunity: Opportunity,
        perspectives: Dict[str, float],
        target_ring: str
    ) -> str:
        """Generate human-readable explanation for a recommendation.
        
        Args:
            features: User features
            opportunity: The opportunity
            perspectives: Perspective scores
            target_ring: Target ring
            
        Returns:
            Explanation string
        """
        # Find highest scoring perspective
        top_perspective = max(perspectives, key=perspectives.get)
        
        # Generate explanation based on context
        if target_ring == "psychological":
            if features.get("avg_stress", 0) > 3.5:
                return f"Your stress levels have been elevated. {opportunity.title} can help you find balance and relief."
            if features.get("avg_mood", 5) < 3:
                return f"Supporting your emotional wellbeing is important. {opportunity.title} could help lift your mood."
            if features.get("social_hours", 0) < 2:
                return f"Connecting with others can boost your mood. {opportunity.title} is a great opportunity to meet people."
            return f"Taking care of your psychological health is key. {opportunity.title} supports your mental wellness."
        
        elif target_ring == "physical":
            if features.get("avg_exercise", 0) < 30:
                return f"Staying active is important for both body and mind. {opportunity.title} can help you get moving."
            if features.get("avg_sleep", 8) < 6:
                return f"Quality sleep is essential. {opportunity.title} may help improve your rest."
            return f"Physical health supports everything else you do. {opportunity.title} is a great fit for your physical goals."
        
        elif target_ring == "mental":
            if features.get("study_hours", 0) < 10:
                return f"Growing your skills opens new doors. {opportunity.title} can help advance your learning."
            return f"Intellectual growth is a lifelong journey. {opportunity.title} aligns with your mental development goals."
        
        return f"Based on your patterns, {opportunity.title} could be a valuable addition to your routine."
    
    def adjust_weights(
        self,
        weakest_ring: str
    ) -> None:
        """Adjust perspective weights based on user's weakest ring.
        
        Args:
            weakest_ring: The user's weakest ring
        """
        # Reset to defaults
        self.perspective_weights = {
            "efficiency": 0.25,
            "wellbeing": 0.30,
            "physical": 0.25,
            "learning": 0.20
        }
        
        # Adjust based on weakest ring
        if weakest_ring == "psychological":
            self.perspective_weights["wellbeing"] = 0.40
            self.perspective_weights["efficiency"] = 0.20
        elif weakest_ring == "physical":
            self.perspective_weights["physical"] = 0.40
            self.perspective_weights["wellbeing"] = 0.20
        elif weakest_ring == "mental":
            self.perspective_weights["learning"] = 0.35
            self.perspective_weights["efficiency"] = 0.30


class RecommendationEngine:
    """Engine for generating personalized recommendations."""
    
    def __init__(self):
        self.ranker = CoreRanker()
    
    async def generate_recommendations(
        self,
        user_id: str,
        features: Dict[str, Any],
        opportunities: List[Opportunity],
        top_k: int = 5
    ) -> List[Recommendation]:
        """Generate personalized recommendations for a user.
        
        Args:
            user_id: The user ID
            features: User features
            opportunities: Available opportunities
            top_k: Number of recommendations to generate
            
        Returns:
            List of Recommendation objects
        """
        # Adjust weights based on weakest ring
        weakest_ring = features.get("weakest_ring")
        if weakest_ring:
            self.ranker.adjust_weights(weakest_ring)
        
        # Rank opportunities
        ranked = self.ranker.rank_opportunities(features, opportunities, top_k=top_k)
        
        # Create recommendation objects
        recommendations = []
        for i, (opp, score, explanation) in enumerate(ranked):
            target_ring = self.ranker._determine_target_ring(
                features,
                perspective_scorer.score_all_perspectives(features, opp),
                opp
            )
            
            rec = Recommendation(
                id=f"rec_{user_id}_{int(datetime.now().timestamp())}_{i}",
                user_id=user_id,
                opportunity_id=opp.id,
                opportunity=opp,
                ring_target=target_ring,
                score=round(score, 3),
                explanation=explanation,
                created_at=datetime.now(),
                expires_at=None,
                is_viewed=False,
                is_accepted=None
            )
            recommendations.append(rec)
        
        return recommendations


# Global instances
core_ranker = CoreRanker()
recommendation_engine = RecommendationEngine()
