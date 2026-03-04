"""Psychological Ring router for UniThrive.

Handles self-discovery, risk analysis, and neurocognitive tracking endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.psychological_ring import (
    PersonalityAssessmentCreate, SelfDiscoveryTestCreate,
    NeurocognitiveTestCreate, LongTermMetricCreate, RiskAnalysisRequest
)
from app.services.psychological_ring_service import psychological_ring_service
from app.services.checkin_service import checkin_service

router = APIRouter()


@router.post("/personality", status_code=status.HTTP_201_CREATED)
async def submit_personality_assessment(data: PersonalityAssessmentCreate):
    """Submit personality assessment (MBTI, Big Five, etc.)."""
    try:
        result = await psychological_ring_service.create_personality_assessment(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/personality/{user_id}")
async def get_user_personality(user_id: str):
    """Get personality assessment for a user."""
    personality = await psychological_ring_service.get_user_personality(user_id)
    if not personality:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No personality assessment found")
    return {"user_id": user_id, "personality": personality}


@router.post("/self-discovery", status_code=status.HTTP_201_CREATED)
async def complete_self_discovery_test(data: SelfDiscoveryTestCreate):
    """Complete a self-discovery test."""
    try:
        result = await psychological_ring_service.create_self_discovery_test(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/self-discovery/{user_id}")
async def get_user_discovery_tests(user_id: str):
    """Get self-discovery test history."""
    tests = await psychological_ring_service.get_user_discovery_tests(user_id)
    return {"user_id": user_id, "tests": tests, "count": len(tests)}


@router.post("/risk-analysis", status_code=status.HTTP_201_CREATED)
async def trigger_risk_analysis(request: RiskAnalysisRequest):
    """Trigger behavioral risk analysis for a user."""
    try:
        # Get check-in data for analysis
        checkins = await checkin_service.get_user_checkins(request.user_id, days=request.analysis_period_days)
        result = await psychological_ring_service.analyze_risk(request.user_id, checkins)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/risk-profile/{user_id}")
async def get_risk_profile(user_id: str):
    """Get behavioral risk profile for a user."""
    from app.storage.json_storage import JsonPsychologicalRingStorage
    storage = JsonPsychologicalRingStorage(entity_type="risk")
    profiles = await storage.get_by_user_id(user_id)
    if profiles:
        return {"user_id": user_id, "risk_profiles": profiles, "latest": max(profiles, key=lambda x: x['analysis_date'])}
    return {"user_id": user_id, "risk_profiles": [], "message": "No risk analysis available"}


@router.post("/neurocognitive", status_code=status.HTTP_201_CREATED)
async def submit_neurocognitive_test(data: NeurocognitiveTestCreate):
    """Submit neurocognitive test results."""
    try:
        result = await psychological_ring_service.create_neurocognitive_test(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/neurocognitive/{user_id}")
async def get_neurocognitive_results(user_id: str):
    """Get neurocognitive test results for a user."""
    results = await psychological_ring_service.get_user_neuro_tests(user_id)
    return {"user_id": user_id, "results": results, "count": len(results)}


@router.post("/metrics", status_code=status.HTTP_201_CREATED)
async def record_health_metric(data: LongTermMetricCreate):
    """Record a long-term health metric."""
    try:
        result = await psychological_ring_service.create_long_term_metric(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/metrics/{user_id}")
async def get_health_metrics(user_id: str):
    """Get long-term health metrics for a user."""
    metrics = await psychological_ring_service.get_user_metrics(user_id)
    return {"user_id": user_id, "metrics": metrics, "count": len(metrics)}


@router.get("/alerts/{user_id}")
async def get_psychological_alerts(user_id: str):
    """Get psychological alerts for a user."""
    from app.storage.json_storage import JsonPsychologicalRingStorage
    storage = JsonPsychologicalRingStorage(entity_type="alerts")
    alerts = await storage.get_by_user_id(user_id)
    return {"user_id": user_id, "alerts": alerts, "count": len(alerts)}


@router.get("/summary/{user_id}")
async def get_psychological_ring_summary(user_id: str):
    """Get Psychological Ring summary for a user."""
    summary = await psychological_ring_service.get_psychological_ring_summary(user_id)
    return summary
