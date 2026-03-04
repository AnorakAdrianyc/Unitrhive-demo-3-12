"""Risk Detection Service for UniThrive.

Proactive monitoring and detection of mental health risks.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from statistics import mean

from app.config import settings
from app.schemas.recommendations import RiskAlert
from app.storage.json_storage import JsonAlertStorage, JsonCheckInStorage


class RiskDetectionService:
    """Service for detecting and managing mental health risks."""
    
    def __init__(self):
        self.alert_storage = JsonAlertStorage()
        self.checkin_storage = JsonCheckInStorage()
        self.high_risk_keywords = settings.high_risk_keywords
        self.medium_risk_keywords = settings.medium_risk_keywords
    
    async def analyze_user_risk(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Analyze a user's data for risk indicators.
        
        Args:
            user_id: The user ID
            days: Number of days to analyze
            
        Returns:
            Risk analysis results
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        checkins = await self.checkin_storage.get_by_user_id(
            user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        risk_indicators = []
        risk_score = 0
        
        if not checkins:
            risk_indicators.append({
                "type": "no_checkins",
                "severity": "low",
                "description": f"No check-ins in the past {days} days"
            })
            risk_score += 1
        else:
            # Analyze stress patterns
            stress_scores = [c.stress_score for c in checkins]
            avg_stress = mean(stress_scores)
            
            if all(s >= 4 for s in stress_scores[-3:]):
                risk_indicators.append({
                    "type": "sustained_high_stress",
                    "severity": "high",
                    "description": "High stress for 3+ consecutive days"
                })
                risk_score += 3
            elif avg_stress >= 3.5:
                risk_indicators.append({
                    "type": "elevated_stress",
                    "severity": "medium",
                    "description": f"Average stress level is {avg_stress:.1f}/5"
                })
                risk_score += 2
            
            # Analyze mood trends
            mood_scores = [c.mood_score for c in checkins]
            
            if len(mood_scores) >= 3:
                # Check for declining trend
                first_half = mean(mood_scores[:len(mood_scores)//2])
                second_half = mean(mood_scores[len(mood_scores)//2:])
                
                if first_half - second_half > 0.5:
                    risk_indicators.append({
                        "type": "declining_mood",
                        "severity": "medium",
                        "description": "Mood has been declining recently"
                    })
                    risk_score += 2
            
            if all(m <= 2 for m in mood_scores[-3:]):
                risk_indicators.append({
                    "type": "sustained_low_mood",
                    "severity": "high",
                    "description": "Low mood for 3+ consecutive days"
                })
                risk_score += 3
            
            # Analyze sleep patterns
            sleep_hours = [c.sleep_hours for c in checkins]
            
            if all(s < 5 for s in sleep_hours[-3:]):
                risk_indicators.append({
                    "type": "sleep_deprivation",
                    "severity": "medium",
                    "description": "Less than 5 hours sleep for 3+ days"
                })
                risk_score += 2
            
            # Analyze social interactions
            social_counts = [c.social_interactions for c in checkins]
            
            if all(s == 0 for s in social_counts[-5:]):
                risk_indicators.append({
                    "type": "social_withdrawal",
                    "severity": "medium",
                    "description": "No social interactions for 5+ days"
                })
                risk_score += 2
        
        # Determine overall risk level
        if risk_score >= 6:
            risk_level = "high"
        elif risk_score >= 4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "user_id": user_id,
            "analysis_period_days": days,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "indicators": risk_indicators,
            "checkin_count": len(checkins),
            "analyzed_at": datetime.now().isoformat()
        }
    
    async def detect_and_create_alerts(self, user_id: str) -> Optional[RiskAlert]:
        """Analyze user and create alert if risk detected.
        
        Args:
            user_id: The user ID
            
        Returns:
            Created alert or None if no risk
        """
        analysis = await self.analyze_user_risk(user_id)
        
        if analysis["risk_level"] in ["high", "medium"]:
            # Check if similar alert already exists
            existing_alerts = await self.alert_storage.get_by_user_id(
                user_id,
                active_only=True,
                risk_level=analysis["risk_level"]
            )
            
            if existing_alerts:
                # Don't create duplicate
                return None
            
            # Create new alert
            alert = RiskAlert(
                id="",
                user_id=user_id,
                risk_level=analysis["risk_level"],
                reason=self._format_risk_reason(analysis),
                triggered_at=datetime.now(),
                escalated_to_counselor=(analysis["risk_level"] == "high"),
                suggested_actions=self._generate_suggested_actions(analysis),
                is_acknowledged=False,
                acknowledged_at=None,
                resolved_at=None
            )
            
            return await self.alert_storage.create(alert)
        
        return None
    
    def _format_risk_reason(self, analysis: Dict[str, Any]) -> str:
        """Format risk analysis into a human-readable reason."""
        indicators = analysis["indicators"]
        
        if not indicators:
            return "Risk analysis detected concerns"
        
        # Get primary indicator
        high_severity = [i for i in indicators if i["severity"] == "high"]
        if high_severity:
            return f"{high_severity[0]['description']}"
        
        medium_severity = [i for i in indicators if i["severity"] == "medium"]
        if medium_severity:
            return f"{medium_severity[0]['description']}"
        
        return f"Multiple indicators: {', '.join(i['type'] for i in indicators)}"
    
    def _generate_suggested_actions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate suggested actions based on risk analysis."""
        actions = []
        
        for indicator in analysis["indicators"]:
            if indicator["type"] == "sustained_high_stress":
                actions.extend([
                    "Practice 5-minute breathing exercises",
                    "Consider scheduling a counseling session",
                    "Take a 30-minute break for a walk"
                ])
            elif indicator["type"] == "sustained_low_mood":
                actions.extend([
                    "Reach out to a friend or family member",
                    "Engage in an activity you usually enjoy",
                    "Consider speaking with a counselor"
                ])
            elif indicator["type"] == "sleep_deprivation":
                actions.extend([
                    "Establish a consistent sleep schedule",
                    "Avoid screens 1 hour before bed",
                    "Try a relaxing bedtime routine"
                ])
            elif indicator["type"] == "social_withdrawal":
                actions.extend([
                    "Send a message to someone you care about",
                    "Join a club or group activity",
                    "Attend a campus event"
                ])
        
        # Default actions if none specific
        if not actions:
            actions = [
                "Complete your daily check-in to track patterns",
                "Explore wellness resources in your recommendations",
                "Consider talking to someone about how you're feeling"
            ]
        
        return list(set(actions))[:5]  # Remove duplicates, limit to 5
    
    async def scan_text_for_risk(self, text: str) -> Dict[str, Any]:
        """Scan text (e.g., chat message, journal entry) for risk keywords.
        
        Args:
            text: Text to scan
            
        Returns:
            Risk scan results
        """
        text_lower = text.lower()
        
        found_high_risk = []
        found_medium_risk = []
        
        for keyword in self.high_risk_keywords:
            if keyword.lower() in text_lower:
                found_high_risk.append(keyword)
        
        for keyword in self.medium_risk_keywords:
            if keyword.lower() in text_lower:
                found_medium_risk.append(keyword)
        
        risk_level = "none"
        if found_high_risk:
            risk_level = "high"
        elif found_medium_risk:
            risk_level = "medium"
        
        return {
            "risk_level": risk_level,
            "high_risk_keywords_found": found_high_risk,
            "medium_risk_keywords_found": found_medium_risk,
            "requires_immediate_attention": len(found_high_risk) > 0
        }


# Global instance
risk_detection_service = RiskDetectionService()
