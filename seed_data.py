"""Seed Data Generator for UniThrive.

Creates sample data for 3 student personas with realistic patterns:
- Maya: Business + Psych, exam week stress pattern
- Shadow: Physics + Green Energy, high mental but low physical
- Adrian: CS/Fintech, high social but mood fluctuations
"""

import asyncio
import uuid
from datetime import datetime, date, timedelta, time
from random import randint, choice, uniform

from app.schemas.user import User, Profile
from app.schemas.checkin import CheckInCreate, ActivityRecordCreate, ActivityType, RingTag
from app.schemas.mental_ring import (
    CourseEngagementCreate, WorkshopAttendanceCreate,
    SkillDevelopmentCreate, AcademicProjectCreate, LearningGoalCreate,
    SkillCategory, ProjectStatus
)
from app.schemas.psychological_ring import (
    PersonalityAssessmentCreate, NeurocognitiveTestCreate,
    AssessmentType, MBTIType, NeuroTestType
)
from app.schemas.physical_ring import (
    TimeManagementCreate, DailyActivityCreate, SleepRecordCreate,
    FitnessRoutineCreate, ExerciseSessionCreate,
    FitnessType, ExerciseIntensity, DayOfWeek
)
from app.storage.json_storage import JsonUserStorage, JsonCheckInStorage, JsonActivityStorage
from app.storage.json_storage import JsonMentalRingStorage, JsonPsychologicalRingStorage, JsonPhysicalRingStorage


async def create_users():
    """Create the 3 student personas."""
    user_storage = JsonUserStorage()
    
    # Maya - Business + Psych, exam week stress
    maya = User(
        id=str(uuid.uuid4()),
        email="maya@university.edu",
        display_name="Maya",
        is_anonymous=False,
        created_at=datetime.now() - timedelta(days=30)
    )
    maya = await user_storage.create(maya)
    
    # Shadow - Physics + Green Energy, high mental low physical
    shadow = User(
        id=str(uuid.uuid4()),
        email="shadow@university.edu",
        display_name="Shadow",
        is_anonymous=False,
        created_at=datetime.now() - timedelta(days=30)
    )
    shadow = await user_storage.create(shadow)
    
    # Adrian - CS/Fintech, high social mood fluctuations
    adrian = User(
        id=str(uuid.uuid4()),
        email="adrian@university.edu",
        display_name="Adrian",
        is_anonymous=False,
        created_at=datetime.now() - timedelta(days=30)
    )
    adrian = await user_storage.create(adrian)
    
    print(f"Created users: Maya ({maya.id}), Shadow ({shadow.id}), Adrian ({adrian.id})")
    
    return [maya, shadow, adrian]


async def create_checkins_maya(user):
    """Create check-ins for Maya - exam week stress pattern."""
    checkin_storage = JsonCheckInStorage()
    
    # Generate 7 days of data
    base_date = date.today() - timedelta(days=7)
    
    for day in range(7):
        current_date = base_date + timedelta(days=day)
        
        # Exam week pattern: higher stress on weekdays, recovery on weekend
        if day < 5:  # Weekdays
            stress = randint(3, 5)  # High stress
            mood = randint(2, 4)    # Lower mood
            sleep = uniform(5.0, 6.5)  # Less sleep
            exercise = randint(0, 15)  # Little exercise
        else:  # Weekend - recovery
            stress = randint(2, 3)  # Lower stress
            mood = randint(3, 5)    # Better mood
            sleep = uniform(7.0, 9.0)  # More sleep
            exercise = randint(20, 45)  # Some exercise
        
        checkin = CheckInCreate(
            user_id=user.id,
            mood_score=mood,
            stress_score=stress,
            sleep_hours=round(sleep, 1),
            exercise_minutes=exercise,
            social_interactions=randint(1, 3),
            notes_text="Exam prep day" if day < 5 else "Weekend recovery"
        )
        
        await checkin_storage.create(checkin.__class__(
            id=str(uuid.uuid4()),
            user_id=checkin.user_id,
            timestamp=datetime.combine(current_date, datetime.min.time()) + timedelta(hours=20),
            mood_score=checkin.mood_score,
            stress_score=checkin.stress_score,
            sleep_hours=checkin.sleep_hours,
            exercise_minutes=checkin.exercise_minutes,
            social_interactions=checkin.social_interactions,
            notes_text=checkin.notes_text
        ))
    
    print(f"  Created 7 check-ins for Maya")


async def create_checkins_shadow(user):
    """Create check-ins for Shadow - high mental, low physical."""
    checkin_storage = JsonCheckInStorage()
    
    base_date = date.today() - timedelta(days=7)
    
    for day in range(7):
        current_date = base_date + timedelta(days=day)
        
        # Consistent pattern: good sleep, low stress, minimal exercise
        stress = randint(1, 3)   # Low stress (focused on studies)
        mood = randint(3, 5)     # Good mood
        sleep = uniform(7.5, 9.0)  # Good sleep
        exercise = randint(0, 10)  # Very little exercise (sedentary)
        
        checkin = CheckInCreate(
            user_id=user.id,
            mood_score=mood,
            stress_score=stress,
            sleep_hours=round(sleep, 1),
            exercise_minutes=exercise,
            social_interactions=randint(0, 2),
            notes_text="Lab work and research"
        )
        
        await checkin_storage.create(checkin.__class__(
            id=str(uuid.uuid4()),
            user_id=checkin.user_id,
            timestamp=datetime.combine(current_date, datetime.min.time()) + timedelta(hours=21),
            mood_score=checkin.mood_score,
            stress_score=checkin.stress_score,
            sleep_hours=checkin.sleep_hours,
            exercise_minutes=checkin.exercise_minutes,
            social_interactions=checkin.social_interactions,
            notes_text=checkin.notes_text
        ))
    
    print(f"  Created 7 check-ins for Shadow")


async def create_checkins_adrian(user):
    """Create check-ins for Adrian - high social, mood fluctuations."""
    checkin_storage = JsonCheckInStorage()
    
    base_date = date.today() - timedelta(days=7)
    
    for day in range(7):
        current_date = base_date + timedelta(days=day)
        
        # Variable pattern: some high days, some low
        if day in [0, 2, 5]:  # Good days
            stress = randint(2, 3)
            mood = randint(4, 5)
            exercise = randint(30, 60)
        elif day in [1, 6]:  # Average days
            stress = randint(3, 4)
            mood = randint(3, 4)
            exercise = randint(15, 30)
        else:  # Challenging days
            stress = randint(4, 5)
            mood = randint(2, 3)
            exercise = randint(0, 20)
        
        sleep = uniform(6.0, 7.5)
        
        checkin = CheckInCreate(
            user_id=user.id,
            mood_score=mood,
            stress_score=stress,
            sleep_hours=round(sleep, 1),
            exercise_minutes=exercise,
            social_interactions=randint(3, 8),  # High social
            notes_text="Hackathon prep" if day == 5 else "Regular day"
        )
        
        await checkin_storage.create(checkin.__class__(
            id=str(uuid.uuid4()),
            user_id=checkin.user_id,
            timestamp=datetime.combine(current_date, datetime.min.time()) + timedelta(hours=23),
            mood_score=checkin.mood_score,
            stress_score=checkin.stress_score,
            sleep_hours=checkin.sleep_hours,
            exercise_minutes=checkin.exercise_minutes,
            social_interactions=checkin.social_interactions,
            notes_text=checkin.notes_text
        ))
    
    print(f"  Created 7 check-ins for Adrian")


async def create_activities(user):
    """Create sample activities for a user."""
    activity_storage = JsonActivityStorage()
    
    # Create a few activities
    activities = [
        ("Statistics 101", "course", 90, "mental"),
        ("Yoga Class", "exercise", 45, "physical"),
        ("Python Workshop", "skill", 120, "mental"),
    ]
    
    for title, act_type, duration, ring in activities:
        act = ActivityRecordCreate(
            user_id=user.id,
            date=date.today() - timedelta(days=randint(1, 7)),
            type=ActivityType(act_type),
            duration_minutes=duration,
            tag_ring=RingTag(ring),
            title=title
        )
        
        await activity_storage.create(act.__class__(
            id=str(uuid.uuid4()),
            user_id=act.user_id,
            date=act.date,
            type=act.type,
            duration_minutes=act.duration_minutes,
            tag_ring=act.tag_ring,
            title=act.title,
            created_at=datetime.now()
        ))


async def create_mental_ring_data(user):
    """Create Mental Ring data for a user."""
    course_storage = JsonMentalRingStorage("data", "courses")
    skill_storage = JsonMentalRingStorage("data", "skills")
    
    # Add a course
    course = CourseEngagementCreate(
        user_id=user.id,
        course_id=f"COURSE_{uuid.uuid4().hex[:8]}",
        course_name=choice(["Introduction to Psychology", "Business Strategy", "Data Analysis"]),
        attendance_rate=uniform(0.7, 0.95),
        assignment_completion=uniform(0.6, 0.9),
        participation_score=uniform(0.5, 0.8)
    )
    
    await course_storage.create(course.__class__(
        id=str(uuid.uuid4()),
        user_id=course.user_id,
        course_id=course.course_id,
        course_name=course.course_name,
        attendance_rate=course.attendance_rate,
        assignment_completion=course.assignment_completion,
        participation_score=course.participation_score,
        last_updated=datetime.now()
    ))
    
    # Add a skill
    skill = SkillDevelopmentCreate(
        user_id=user.id,
        skill_name=choice(["Python Programming", "Public Speaking", "Data Visualization"]),
        category=choice([SkillCategory.CODING, SkillCategory.COMMUNICATION, SkillCategory.ANALYTICS]),
        proficiency_level=randint(4, 8),
        hours_invested=randint(20, 80)
    )
    
    await skill_storage.create(skill.__class__(
        id=str(uuid.uuid4()),
        user_id=skill.user_id,
        skill_name=skill.skill_name,
        category=skill.category,
        proficiency_level=skill.proficiency_level,
        hours_invested=skill.hours_invested,
        started_date=date.today() - timedelta(days=randint(30, 90))
    ))


async def create_psychological_ring_data(user):
    """Create Psychological Ring data for a user."""
    personality_storage = JsonPsychologicalRingStorage("data", "personality")
    neuro_storage = JsonPsychologicalRingStorage("data", "neuro")
    
    # Add personality assessment
    mbti_types = [MBTIType.ENFJ, MBTIType.INTP, MBTIType.ENTP, MBTIType.INFJ]
    assessment = PersonalityAssessmentCreate(
        user_id=user.id,
        assessment_type=AssessmentType.MBTI,
        results={
            "traits": ["Intuitive", "Feeling", "Judging"],
            "strengths": ["Empathy", "Organization"],
            "study_preferences": ["Group study", "Visual learning"]
        },
        mbti_type=choice(mbti_types)
    )
    
    await personality_storage.create(assessment.__class__(
        id=str(uuid.uuid4()),
        user_id=assessment.user_id,
        assessment_type=assessment.assessment_type,
        results=assessment.results,
        mbti_type=assessment.mbti_type,
        traits=assessment.results.get('traits', []),
        completed_at=datetime.now()
    ))
    
    # Add neurocognitive test
    test_type = choice([NeuroTestType.MEMORY, NeuroTestType.ATTENTION, NeuroTestType.COGNITIVE_SPEED])
    neuro_test = NeurocognitiveTestCreate(
        user_id=user.id,
        test_type=test_type,
        score=uniform(70, 95),
        percentile=randint(40, 85)
    )
    
    await neuro_storage.create(neuro_test.__class__(
        id=str(uuid.uuid4()),
        user_id=neuro_test.user_id,
        test_type=neuro_test.test_type,
        score=neuro_test.score,
        percentile=neuro_test.percentile,
        test_date=date.today() - timedelta(days=randint(1, 14))
    ))


async def create_physical_ring_data(user):
    """Create Physical Ring data for a user."""
    sleep_storage = JsonPhysicalRingStorage("data", "sleep")
    activity_storage = JsonPhysicalRingStorage("data", "activity")
    
    # Add sleep record
    sleep = SleepRecordCreate(
        user_id=user.id,
        date=date.today() - timedelta(days=1),
        bed_time=time(23, 30),
        wake_time=time(7, 0),
        sleep_quality=randint(3, 5),
        rem_minutes=randint(60, 100),
        deep_minutes=randint(40, 80)
    )
    
    # Calculate total hours
    total_hours = 7.5  # 11:30 PM to 7:00 AM
    
    await sleep_storage.create(sleep.__class__(
        id=str(uuid.uuid4()),
        user_id=sleep.user_id,
        date=sleep.date,
        bed_time=sleep.bed_time,
        wake_time=sleep.wake_time,
        total_hours=total_hours,
        sleep_quality=sleep.sleep_quality,
        rem_minutes=sleep.rem_minutes,
        deep_minutes=sleep.deep_minutes
    ))
    
    # Add daily activity
    activity = DailyActivityCreate(
        user_id=user.id,
        date=date.today() - timedelta(days=1),
        steps=randint(3000, 12000),
        active_minutes=randint(15, 90),
        sedentary_hours=uniform(6.0, 10.0),
        movement_breaks_taken=randint(2, 8)
    )
    
    await activity_storage.create(activity.__class__(
        id=str(uuid.uuid4()),
        user_id=activity.user_id,
        date=activity.date,
        steps=activity.steps,
        active_minutes=activity.active_minutes,
        sedentary_hours=activity.sedentary_hours,
        movement_breaks_taken=activity.movement_breaks_taken
    ))


async def seed_all_data():
    """Seed all data for the prototype."""
    print("=" * 60)
    print("UniThrive Seed Data Generator")
    print("=" * 60)
    
    # Create users
    users = await create_users()
    
    # Create check-ins for each user
    await create_checkins_maya(users[0])
    await create_checkins_shadow(users[1])
    await create_checkins_adrian(users[2])
    
    # Create other data for each user
    for user in users:
        await create_activities(user)
        await create_mental_ring_data(user)
        await create_psychological_ring_data(user)
        await create_physical_ring_data(user)
    
    print("\n" + "=" * 60)
    print("Seed data created successfully!")
    print("=" * 60)
    print("\nYou can now run: python batch_job.py")
    print("to process the data and generate summaries.")


if __name__ == "__main__":
    asyncio.run(seed_all_data())
