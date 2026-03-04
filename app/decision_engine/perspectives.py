"""Multi-perspective scoring module for UniThrive decision engine.

Provides different perspectives for scoring opportunities and recommendations.
"""

from typing import Dict, Any, List

from app.schemas.recommendations import Opportunity


class PerspectiveScorer:
    """Scores opportunities from multiple perspectives."""
    
    def efficiency_perspective(
        self,
        features: Dict[str, Any],
        opportunity: Opportunity
    ) -> float:
        """Score from an efficiency/time management perspective.
        
        Considers:
        - How the opportunity helps with academic/work efficiency
        - Time investment vs expected benefit
        - Alignment with current workload
        
        Args:
            features: User features from feature extractor
            opportunity: The opportunity to score
            
        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.5  # baseline
        
        # Check opportunity type
        if opportunity.type == "workshop":
            if "time" in opportunity.tags or "productivity" in opportunity.tags:
                score += 0.3
            if features.get("weakest_ring") == "mental":
                score += 0.2
        
        elif opportunity.type == "course":
            if features.get("avg_mental", 0.5) < 0.6:
                score += 0.3
        
        elif opportunity.type == "event":
            # Events are neutral for efficiency unless skill-related
            if "skill" in opportunity.tags:
                score += 0.2
        
        # Consider activity level
        activity_freq = features.get("activity_frequency", 0)
        if activity_freq < 1 and opportunity.type in ["workshop", "course"]:
            # Low activity - might benefit from structured learning
            score += 0.1
        
        return min(1.0, score)
    
    def wellbeing_perspective(
        self,
        features: Dict[str, Any],
        opportunity: Opportunity
    ) -> float:
        """Score from a wellbeing/mental health perspective.
        
        Considers:
        - Impact on stress and mood
        - Social connection opportunities
        - Mindfulness and relaxation benefits
        
        Args:
            features: User features from feature extractor
            opportunity: The opportunity to score
            
        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.5  # baseline
        
        # Check for stress-related tags
        if "stress" in opportunity.tags or "mindfulness" in opportunity.tags:
            if features.get("avg_stress", 0) > 3.5:
                score += 0.4
            if features.get("stress_trend") == "declining":
                score += 0.1
        
        # Check for mood-related tags
        if "mood" in opportunity.tags or "wellbeing" in opportunity.tags:
            if features.get("avg_mood", 5) < 3:
                score += 0.3
        
        # Check for social tags
        if "social" in opportunity.tags or "community" in opportunity.tags:
            # High value if user has few social interactions
            if features.get("social_hours", 0) < 2:
                score += 0.3
        
        # Check ring weakness
        if features.get("weakest_ring") == "psychological":
            if opportunity.type in ["counselling", "community"]:
                score += 0.3
        
        return min(1.0, score)
    
    def physical_perspective(
        self,
        features: Dict[str, Any],
        opportunity: Opportunity
    ) -> float:
        """Score from a physical health perspective.
        
        Considers:
        - Exercise and activity benefits
        - Sleep improvement potential
        - Overall physical wellness
        
        Args:
            features: User features from feature extractor
            opportunity: The opportunity to score
            
        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.5  # baseline
        
        # Check for exercise/activity tags
        if "exercise" in opportunity.tags or "fitness" in opportunity.tags:
            if features.get("avg_exercise", 0) < 30:  # less than 30 min daily
                score += 0.4
            if features.get("weakest_ring") == "physical":
                score += 0.2
        
        # Check for sleep tags
        if "sleep" in opportunity.tags:
            if features.get("avg_sleep", 8) < 6:
                score += 0.4
        
        # Check opportunity type
        if opportunity.type == "activity":
            score += 0.2
        
        return min(1.0, score)
    
    def learning_perspective(
        self,
        features: Dict[str, Any],
        opportunity: Opportunity
    ) -> float:
        """Score from a learning/development perspective.
        
        Considers:
        - Skill development potential
        - Career/academic relevance
        - Intellectual growth
        
        Args:
            features: User features from feature extractor
            opportunity: The opportunity to score
            
        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.5  # baseline
        
        # Check for skill-related tags
        if "skill" in opportunity.tags or "learning" in opportunity.tags:
            if features.get("study_hours", 0) < 10:  # Low study time
                score += 0.3
            if features.get("weakest_ring") == "mental":
                score += 0.2
        
        # Check opportunity type
        if opportunity.type == "workshop":
            score += 0.2
        elif opportunity.type == "course":
            score += 0.3
        
        return min(1.0, score)
    
    def score_all_perspectives(
        self,
        features: Dict[str, Any],
        opportunity: Opportunity
    ) -> Dict[str, float]:
        """Score an opportunity from all perspectives.
        
        Args:
            features: User features
            opportunity: The opportunity
            
        Returns:
            Dictionary mapping perspective names to scores
        """
        return {
            "efficiency": self.efficiency_perspective(features, opportunity),
            "wellbeing": self.wellbeing_perspective(features, opportunity),
            "physical": self.physical_perspective(features, opportunity),
            "learning": self.learning_perspective(features, opportunity)
        }


# Global instance
perspective_scorer = PerspectiveScorer()
