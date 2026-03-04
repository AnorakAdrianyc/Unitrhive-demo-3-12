"""Psychological Ring service for UniThrive.

Handles business logic for self-discovery, risk analysis,
MBTI assessments, and neurocognitive tracking.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from statistics import mean

from app.schemas.psychological_ring import (
    PersonalityAssessment, PersonalityAssessmentCreate,
    SelfDiscoveryTest, SelfDiscoveryTestCreate,
    BehavioralRiskProfile, LearningPattern,
    NeurocognitiveTest, NeurocognitiveTestCreate,
    LongTermMetric, LongTermMetricCreate,
    PsychologicalAlert, PsychologicalRingSummary,
    RiskSeverity
)
from app.storage.json_storage import JsonPsychologicalRingStorage, JsonAlertStorage
from app.config import settings


class PsychologicalRingService:
    """Service for managing Psychological Ring data."""
    
    def __init__(self):
        self.personality_storage = JsonPsychologicalRingStorage(entity_type="personality")
        self.self_discovery_storage = JsonPsychologicalRingStorage(entity_type="discovery")
        self.risk_storage = JsonPsychologicalRingStorage(entity_type="risk")
        self.pattern_storage = JsonPsychologicalRingStorage(entity_type="patterns")
        self.neuro_storage = JsonPsychologicalRingStorage(entity_type="neuro")
        self.metric_storage = JsonPsychologicalRingStorage(entity_type="metrics")
        self.alert_storage = JsonPsychologicalRingStorage(entity_type="alerts")
        self.main_alert_storage = JsonAlertStorage()
    
    # Personality Assessment
    async def create_personality_assessment(self, data: PersonalityAssessmentCreate) -> Dict[str, Any]:
        """Submit a personality assessment."""
        assessment = PersonalityAssessment(
            id="",
            user_id=data.user_id,
            assessment_type=data.assessment_type,
            results=data.results,
            mbti_type=data.mbti_type,
            traits=data.results.get('traits', []),
            strengths=data.results.get('strengths', []),
            study_preferences=data.results.get('study_preferences', []),
            completed_at=datetime.now()
        )
        return await self.personality_storage.create(assessment)
    
    async def get_user_personality(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest personality assessment for a user."""
        results = await self.personality_storage.get_by_user_id(user_id)
        if results:
            # Return most recent
            return max(results, key=lambda x: x['completed_at'])
        return None
    
    # Self Discovery
    async def create_self_discovery_test(self, data: SelfDiscoveryTestCreate) -> Dict[str, Any]:
        """Complete a self-discovery test."""
        test = SelfDiscoveryTest(
            id="",
            user_id=data.user_id,
            test_id=data.test_id,
            test_name=data.test_name,
            responses=data.responses,
            insights_generated=data.responses.get('insights', []),
            reflection_notes=data.reflection_notes,
            completed_at=datetime.now()
        )
        return await self.self_discovery_storage.create(test)
    
    async def get_user_discovery_tests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all self-discovery tests for a user."""
        return await self.self_discovery_storage.get_by_user_id(user_id)
    
    # Risk Analysis
    async def analyze_risk(self, user_id: str, checkins: List[Any]) -> Dict[str, Any]:
        """Analyze behavioral risk based on check-in patterns."""
        risk_factors = []
        risk_score = 0.0
        
        if checkins:
            # Stress analysis
            avg_stress = mean(c.stress_score for c in checkins)
            if avg_stress >= 4:
                risk_factors.append({
                    'type': 'stress',
                    'severity': 'high',
                    'value': avg_stress,
                    'description': 'High stress levels detected'
                })
                risk_score += 3
            elif avg_stress >= 3.5:
                risk_factors.append({
                    'type': 'stress',
                    'severity': 'medium',
                    'value': avg_stress,
                    'description': 'Elevated stress levels'
                })
                risk_score += 2
            
            # Mood analysis
            avg_mood = mean(c.mood_score for c in checkins)
            if avg_mood <= 2:
                risk_factors.append({
                    'type': 'mood',
                    'severity': 'high',
                    'value': avg_mood,
                    'description': 'Low mood levels detected'
                })
                risk_score += 3
            
            # Sleep analysis
            avg_sleep = mean(c.sleep_hours for c in checkins)
            if avg_sleep < 5:
                risk_factors.append({
                    'type': 'sleep',
                    'severity': 'medium',
                    'value': avg_sleep,
                    'description': 'Insufficient sleep'
                })
                risk_score += 2
            
            # Social withdrawal
            social_interactions = [c.social_interactions for c in checkins]
            if all(s == 0 for s in social_interactions[-5:]):
                risk_factors.append({
                    'type': 'social',
                    'severity': 'medium',
                    'value': 0,
                    'description': 'Social withdrawal detected'
                })
                risk_score += 2
        
        # Determine risk level
        if risk_score >= 6:
            risk_level = RiskSeverity.HIGH
        elif risk_score >= 4:
            risk_level = RiskSeverity.MEDIUM
        elif risk_score >= 2:
            risk_level = RiskSeverity.LOW
        else:
            risk_level = RiskSeverity.LOW
        
        profile = BehavioralRiskProfile(
            id="",
            user_id=user_id,
            risk_factors=risk_factors,
            overall_risk_score=risk_score,
            risk_level=risk_level,
            analysis_date=date.today(),
            recommendations=self._generate_risk_recommendations(risk_factors),
            contributing_factors=[f['type'] for f in risk_factors],
            protective_factors=self._identify_protective_factors(checkins)
        )
        
        stored = await self.risk_storage.create(profile)
        
        # Create alert for high risk
        if risk_level in [RiskSeverity.HIGH, RiskSeverity.CRITICAL]:
            from app.schemas.recommendations import RiskAlert
            alert = RiskAlert(
                id="",
                user_id=user_id,
                risk_level=risk_level.value,
                reason=f"Risk analysis detected elevated concerns: {', '.join(f['type'] for f in risk_factors)}",
                triggered_at=datetime.now(),
                escalated_to_counselor=False,
                suggested_actions=profile.recommendations
            )
            await self.main_alert_storage.create(alert)
        
        return stored
    
    def _generate_risk_recommendations(self, risk_factors: List[Dict]) -> List[str]:
        """Generate recommendations based on risk factors."""
        recommendations = []
        
        for factor in risk_factors:
            if factor['type'] == 'stress':
                recommendations.append("Practice daily stress-reduction techniques (breathing, meditation)")
                recommendations.append("Consider speaking with a counselor about stress management")
            elif factor['type'] == 'mood':
                recommendations.append("Reach out to a friend or family member for support")
                recommendations.append("Consider scheduling a counseling session")
            elif factor['type'] == 'sleep':
                recommendations.append("Establish a consistent sleep schedule (7-9 hours)")
                recommendations.append("Create a relaxing bedtime routine")
            elif factor['type'] == 'social':
                recommendations.append("Try to connect with at least one person today")
                recommendations.append("Consider joining a club or study group")
        
        if not recommendations:
            recommendations.append("Continue your current wellness practices")
            recommendations.append("Check in daily to maintain awareness of your wellbeing")
        
        return recommendations
    
    def _identify_protective_factors(self, checkins: List[Any]) -> List[str]:
        """Identify protective factors from check-in data."""
        factors = []
        
        if checkins:
            avg_exercise = mean(c.exercise_minutes for c in checkins)
            if avg_exercise > 30:
                factors.append("Regular physical activity")
            
            avg_sleep = mean(c.sleep_hours for c in checkins)
            if avg_sleep >= 7:
                factors.append("Adequate sleep")
            
            if any(c.social_interactions > 0 for c in checkins[-3:]):
                factors.append("Social connections")
        
        return factors
    
    # Neurocognitive Tests
    async def create_neurocognitive_test(self, data: NeurocognitiveTestCreate) -> Dict[str, Any]:
        """Submit neurocognitive test results."""
        test = NeurocognitiveTest(
            id="",
            user_id=data.user_id,
            test_type=data.test_type,
            score=data.score,
            percentile=data.percentile,
            baseline_comparison=None,
            test_date=date.today(),
            duration_seconds=data.duration_seconds,
            notes=None
        )
        return await self.neuro_storage.create(test)
    
    async def get_user_neuro_tests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all neurocognitive tests for a user."""
        return await self.neuro_storage.get_by_user_id(user_id)
    
    # Long-term Metrics
    async def create_long_term_metric(self, data: LongTermMetricCreate) -> Dict[str, Any]:
        """Record a long-term health metric."""
        metric = LongTermMetric(
            id="",
            user_id=data.user_id,
            metric_type=data.metric_type,
            value=data.value,
            unit=data.unit,
            recorded_at=datetime.now(),
            trend_direction=None
        )
        return await self.metric_storage.create(metric)
    
    async def get_user_metrics(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all long-term metrics for a user."""
        return await self.metric_storage.get_by_user_id(user_id)
    
    # Summary
    async def get_psychological_ring_summary(self, user_id: str) -> PsychologicalRingSummary:
        """Generate a summary of the Psychological Ring."""
        # Get all data
        personality = await self.get_user_personality(user_id)
        discovery_tests = await self.get_user_discovery_tests(user_id)
        neuro_tests = await self.get_user_neuro_tests(user_id)
        risk_profiles = await self.risk_storage.get_by_user_id(user_id)
        
        # Get latest risk profile
        latest_risk = None
        if risk_profiles:
            latest_risk = max(risk_profiles, key=lambda x: x['analysis_date'])
        
        # Calculate metrics
        emotional_stability = 0.7  # baseline
        if latest_risk:
            risk_score = latest_risk.get('overall_risk_score', 0)
            emotional_stability = max(0, 1 - (risk_score / 10))
        
        self_awareness = min(len(discovery_tests) / 5, 1.0)
        
        cognitive_health = 0.5
        avg_neuro_percentile = None
        if neuro_tests:
            percentiles = [t['percentile'] for t in neuro_tests if t.get('percentile')]
            if percentiles:
                avg_neuro_percentile = mean(percentiles)
                cognitive_health = avg_neuro_percentile / 100
        
        risk_mitigation = 0.7
        if latest_risk:
            risk_level = latest_risk.get('risk_level', 'low')
            risk_mitigation = 0.9 if risk_level == 'low' else (0.6 if risk_level == 'medium' else 0.3)
        
        # Overall score
        overall_score = (
            emotional_stability * 0.3 +
            self_awareness * 0.3 +
            cognitive_health * 0.2 +
            risk_mitigation * 0.2
        )
        
        # Count active alerts
        alerts = await self.alert_storage.get_by_user_id(user_id)
        active_alerts = len([a for a in alerts if a.get('status') == 'active'])
        
        # Generate recommendations
        recommendations = []
        if len(discovery_tests) < 2:
            recommendations.append("Complete a self-discovery assessment to better understand yourself")
        if not neuro_tests:
            recommendations.append("Try a neurocognitive test to establish your cognitive baseline")
        if emotional_stability < 0.5:
            recommendations.append("Consider mindfulness practices to improve emotional stability")
        
        return PsychologicalRingSummary(
            user_id=user_id,
            period_start=date.today() - timedelta(days=30),
            period_end=date.today(),
            emotional_stability_score=round(emotional_stability, 2),
            self_awareness_score=round(self_awareness, 2),
            cognitive_health_score=round(cognitive_health, 2),
            risk_mitigation_score=round(risk_mitigation, 2),
            overall_score=round(overall_score, 2),
            mbti_type=personality.get('mbti_type') if personality else None,
            tests_completed=len(discovery_tests),
            active_alerts=active_alerts,
            avg_neuro_percentile=avg_neuro_percentile,
            risk_level=latest_risk.get('overall_risk_score') if latest_risk else None,
            recommendations=recommendations
        )


# Global service instance
psychological_ring_service = PsychologicalRingService()
