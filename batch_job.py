"""Batch Job for UniThrive.

Processes data periodically to:
1. Calculate daily ring scores
2. Generate weekly summaries
3. Award achievement badges
4. Create recommendations
5. Detect risks and create alerts

Usage:
    python batch_job.py
    python batch_job.py --user-id <user_id>
"""

import asyncio
import argparse
from datetime import datetime, date, timedelta
from statistics import mean

from app.storage.json_storage import (
    JsonUserStorage, JsonCheckInStorage, JsonActivityStorage,
    JsonRingScoreStorage, JsonWeeklySummaryStorage, JsonAlertStorage,
    JsonRecommendationStorage, JsonOpportunityStorage
)
from app.services.ring_scoring_service import ring_scoring_service
from app.services.risk_detection_service import risk_detection_service
from app.services.recommendation_service import recommendation_service
from app.schemas.rings import DailyRingScore, WeeklySummary, AchievementBadge, RingScores
from app.schemas.recommendations import Opportunity


async def calculate_daily_scores(user_id: str) -> None:
    """Calculate and store daily ring scores for a user."""
    checkin_storage = JsonCheckInStorage()
    activity_storage = JsonActivityStorage()
    ring_score_storage = JsonRingScoreStorage()
    
    today = date.today()
    
    # Get today's data
    checkins = await checkin_storage.get_by_user_and_date(user_id, today)
    activities = await activity_storage.get_by_user_id(
        user_id,
        start_date=today,
        end_date=today
    )
    
    # Check if already calculated today
    existing = await ring_score_storage.get_latest_for_user(user_id)
    if existing and existing.date == today:
        print(f"  Ring scores already calculated for today for user {user_id}")
        return
    
    # Calculate scores
    scores = ring_scoring_service.calculate_all_scores(
        checkins=checkins,
        activities=activities
    )
    
    # Create and store
    daily_score = DailyRingScore(
        id="",
        user_id=user_id,
        date=today,
        mental_score=scores.mental,
        psychological_score=scores.psychological,
        physical_score=scores.physical,
        calculated_at=datetime.now()
    )
    
    await ring_score_storage.create(daily_score)
    print(f"  Calculated ring scores for user {user_id}: M={scores.mental:.2f}, P={scores.psychological:.2f}, Ph={scores.physical:.2f}")


async def generate_weekly_summary(user_id: str) -> None:
    """Generate weekly summary for a user."""
    summary_storage = JsonWeeklySummaryStorage()
    ring_score_storage = JsonRingScoreStorage()
    checkin_storage = JsonCheckInStorage()
    activity_storage = JsonActivityStorage()
    
    # Define week
    week_end = date.today()
    week_start = week_end - timedelta(days=6)
    
    # Check if already generated for this week
    existing = await summary_storage.get_latest_for_user(user_id)
    if existing and existing.week_start == week_start:
        print(f"  Weekly summary already generated for this week for user {user_id}")
        return
    
    # Get data
    ring_scores = await ring_score_storage.get_by_user_id(
        user_id,
        start_date=week_start,
        end_date=week_end
    )
    
    checkins = await checkin_storage.get_by_user_id(
        user_id,
        start_date=week_start,
        end_date=week_end
    )
    
    activities = await activity_storage.get_by_user_id(
        user_id,
        start_date=week_start,
        end_date=week_end
    )
    
    # Calculate averages
    avg_mental = mean([r.mental_score for r in ring_scores]) if ring_scores else 0.5
    avg_psych = mean([r.psychological_score for r in ring_scores]) if ring_scores else 0.5
    avg_physical = mean([r.physical_score for r in ring_scores]) if ring_scores else 0.5
    
    # Generate summaries
    mental_summary = f"You averaged a {avg_mental:.0%} mental ring score this week. "
    if activities:
        study_hours = sum(a.duration_minutes for a in activities if a.type in ["course", "skill"]) / 60
        mental_summary += f"You logged {study_hours:.1f} hours of study time."
    
    psych_summary = f"Your psychological wellbeing averaged {avg_psych:.0%}. "
    if checkins:
        avg_mood = mean([c.mood_score for c in checkins])
        avg_stress = mean([c.stress_score for c in checkins])
        psych_summary += f"Average mood: {avg_mood:.1f}/5, stress: {avg_stress:.1f}/5."
    
    physical_summary = f"Your physical health ring averaged {avg_physical:.0%}. "
    if checkins:
        avg_sleep = mean([c.sleep_hours for c in checkins])
        total_exercise = sum([c.exercise_minutes for c in checkins])
        physical_summary += f"Average sleep: {avg_sleep:.1f}h, total exercise: {total_exercise}min."
    
    # Generate spotlight opportunity
    from app.decision_engine.features import feature_extractor
    features = feature_extractor.extract_checkin_features(checkins)
    features.update(feature_extractor.extract_ring_score_features(ring_scores))
    
    spotlight = await recommendation_service.generate_spotlight_opportunity(user_id, features)
    
    # Determine achievement badge
    ring_scores_obj = RingScores(
        mental=avg_mental,
        psychological=avg_psych,
        physical=avg_physical,
        calculated_at=datetime.now()
    )
    badge = ring_scoring_service.determine_achievement_badge(ring_scores_obj, ring_scores)
    
    # Create summary
    summary = WeeklySummary(
        id="",
        user_id=user_id,
        week_start=week_start,
        week_end=week_end,
        mental_summary=mental_summary,
        psych_summary=psych_summary,
        physical_summary=physical_summary,
        spotlight_opportunity=spotlight,
        achievement_badge=badge.value if badge else None,
        ring_scores=ring_scores_obj,
        created_at=datetime.now()
    )
    
    await summary_storage.create(summary)
    print(f"  Generated weekly summary for user {user_id}")
    if badge:
        print(f"  Awarded badge: {badge.value}")


async def detect_risks(user_id: str) -> None:
    """Detect risks and create alerts for a user."""
    alert = await risk_detection_service.detect_and_create_alerts(user_id)
    if alert:
        print(f"  Created {alert.risk_level} risk alert for user {user_id}: {alert.reason}")
    else:
        print(f"  No new risks detected for user {user_id}")


async def generate_recommendations(user_id: str) -> None:
    """Generate recommendations for a user."""
    recommendations = await recommendation_service.generate_recommendations(
        user_id=user_id,
        top_k=5
    )
    print(f"  Generated {len(recommendations)} recommendations for user {user_id}")


async def ensure_opportunities() -> None:
    """Ensure sample opportunities exist."""
    storage = JsonOpportunityStorage()
    existing = await storage.get_all(limit=1)
    
    if existing:
        return  # Already have opportunities
    
    # Create sample opportunities
    opportunities = [
        Opportunity(
            id="",
            title="Exam Week Mindfulness Group",
            type="workshop",
            description="Join us for guided meditation and stress relief during exam week",
            tags=["stress", "exam", "mindfulness", "psychological"],
            campus="Main Campus",
            start_time=datetime.now() + timedelta(days=3),
            end_time=datetime.now() + timedelta(days=3, hours=1),
            location="Wellness Center, Room 101",
            is_active=True
        ),
        Opportunity(
            id="",
            title="Campus Yoga Session",
            type="activity",
            description="Free yoga class for all students",
            tags=["exercise", "stress", "sleep", "physical"],
            campus="Main Campus",
            start_time=datetime.now() + timedelta(days=2),
            end_time=datetime.now() + timedelta(days=2, hours=1),
            location="Recreation Center",
            is_active=True
        ),
        Opportunity(
            id="",
            title="Career CV Clinic",
            type="workshop",
            description="Get your resume reviewed by career counselors",
            tags=["career", "skill", "confidence", "mental"],
            campus="Main Campus",
            start_time=datetime.now() + timedelta(days=5),
            end_time=datetime.now() + timedelta(days=5, hours=2),
            location="Career Services Center",
            is_active=True
        ),
        Opportunity(
            id="",
            title="Peer Support Circle",
            type="community",
            description="Connect with fellow students in a supportive environment",
            tags=["loneliness", "social", "wellbeing", "psychological"],
            campus="Main Campus",
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=1.5),
            location="Student Center, Room 205",
            is_active=True
        ),
        Opportunity(
            id="",
            title="Introduction to Python Programming",
            type="course",
            description="Learn Python basics in this 4-week workshop series",
            tags=["coding", "skill", "learning", "mental"],
            campus="Main Campus",
            start_time=datetime.now() + timedelta(days=7),
            end_time=datetime.now() + timedelta(days=7, weeks=4),
            location="Computer Lab B",
            is_active=True
        )
    ]
    
    for opp in opportunities:
        await storage.create(opp)
    
    print(f"  Created {len(opportunities)} sample opportunities")


async def process_user(user_id: str) -> None:
    """Run all batch processing steps for a user."""
    print(f"\nProcessing user: {user_id}")
    print("-" * 50)
    
    await calculate_daily_scores(user_id)
    await generate_weekly_summary(user_id)
    await detect_risks(user_id)
    await generate_recommendations(user_id)


async def process_all_users() -> None:
    """Process all users."""
    user_storage = JsonUserStorage()
    users = await user_storage.get_all(limit=1000)
    
    print(f"\nBatch processing {len(users)} users...")
    print("=" * 50)
    
    for user in users:
        await process_user(user.id)
    
    print("\n" + "=" * 50)
    print("Batch processing complete!")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="UniThrive Batch Processing")
    parser.add_argument(
        "--user-id",
        type=str,
        help="Process specific user ID only"
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("UniThrive Batch Processing Job")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 50)
    
    # Ensure opportunities exist
    await ensure_opportunities()
    
    if args.user_id:
        await process_user(args.user_id)
    else:
        await process_all_users()
    
    print("\n" + "=" * 50)
    print(f"Completed at: {datetime.now().isoformat()}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
