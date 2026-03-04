"""Physical Ring service for UniThrive.

Handles business logic for time management, sleep tracking,
fitness routines, and wearable device integration.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from statistics import mean

from app.schemas.physical_ring import (
    TimeManagementBehavior, TimeManagementCreate,
    DailyActivity, DailyActivityCreate,
    SleepRecord, SleepRecordCreate,
    FitnessRoutine, FitnessRoutineCreate,
    ExerciseSession, ExerciseSessionCreate,
    WearableData, DeviceIntegration,
    DeviceConnectRequest, WearableDataSubmit,
    PhysicalRingSummary
)
from app.storage.json_storage import JsonPhysicalRingStorage


class PhysicalRingService:
    """Service for managing Physical Ring data."""
    
    def __init__(self):
        self.time_storage = JsonPhysicalRingStorage(entity_type="time")
        self.activity_storage = JsonPhysicalRingStorage(entity_type="activity")
        self.sleep_storage = JsonPhysicalRingStorage(entity_type="sleep")
        self.routine_storage = JsonPhysicalRingStorage(entity_type="routines")
        self.exercise_storage = JsonPhysicalRingStorage(entity_type="exercise")
        self.wearable_data_storage = JsonPhysicalRingStorage(entity_type="wearable_data")
        self.device_storage = JsonPhysicalRingStorage(entity_type="devices")
    
    # Time Management
    async def create_time_management(self, data: TimeManagementCreate) -> Dict[str, Any]:
        """Log daily time management behavior."""
        record = TimeManagementBehavior(
            id="",
            user_id=data.user_id,
            date=data.date,
            schedule_adherence=data.schedule_adherence,
            procrastination_instances=data.procrastination_instances,
            productive_hours=data.productive_hours,
            distraction_score=0.0,  # calculated
            tasks_completed=data.tasks_completed,
            tasks_planned=data.tasks_planned,
            focus_sessions_count=0,
            avg_focus_duration_minutes=None,
            notes=None
        )
        return await self.time_storage.create(record)
    
    async def get_user_time_management(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get time management records for a user."""
        records = await self.time_storage.get_by_user_id(user_id)
        cutoff = date.today() - timedelta(days=days)
        return [r for r in records if r['date'] >= cutoff.isoformat()]
    
    # Daily Activity
    async def create_daily_activity(self, data: DailyActivityCreate) -> Dict[str, Any]:
        """Record daily physical activity."""
        record = DailyActivity(
            id="",
            user_id=data.user_id,
            date=data.date,
            steps=data.steps,
            active_minutes=data.active_minutes,
            sedentary_hours=data.sedentary_hours,
            movement_breaks_taken=data.movement_breaks_taken,
            distance_km=None,
            calories_burned=None,
            floors_climbed=None
        )
        return await self.activity_storage.create(record)
    
    async def get_user_activity(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get activity records for a user."""
        records = await self.activity_storage.get_by_user_id(user_id)
        cutoff = date.today() - timedelta(days=days)
        return [r for r in records if r['date'] >= cutoff.isoformat()]
    
    # Sleep
    async def create_sleep_record(self, data: SleepRecordCreate) -> Dict[str, Any]:
        """Log sleep data."""
        from datetime import datetime
        
        # Calculate total hours
        bed_time = datetime.combine(data.date, data.bed_time)
        wake_time = datetime.combine(data.date, data.wake_time)
        if wake_time < bed_time:
            wake_time += timedelta(days=1)
        total_hours = (wake_time - bed_time).total_seconds() / 3600
        
        record = SleepRecord(
            id="",
            user_id=data.user_id,
            date=data.date,
            bed_time=data.bed_time,
            wake_time=data.wake_time,
            total_hours=total_hours,
            sleep_quality=data.sleep_quality,
            rem_minutes=data.rem_minutes,
            deep_minutes=data.deep_minutes,
            light_minutes=None,
            awake_minutes=None,
            position_changes=None,
            sleep_stages=None,
            notes=None
        )
        return await self.sleep_storage.create(record)
    
    async def get_user_sleep(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get sleep records for a user."""
        records = await self.sleep_storage.get_by_user_id(user_id)
        cutoff = date.today() - timedelta(days=days)
        return [r for r in records if r['date'] >= cutoff.isoformat()]
    
    # Fitness
    async def create_fitness_routine(self, data: FitnessRoutineCreate) -> Dict[str, Any]:
        """Create a fitness routine."""
        routine = FitnessRoutine(
            id="",
            user_id=data.user_id,
            name=data.name,
            type=data.type,
            description=None,
            scheduled_days=data.scheduled_days,
            target_duration_minutes=data.target_duration_minutes,
            target_intensity=data.target_intensity,
            exercises=[],
            created_at=datetime.now(),
            is_active=True,
            streak_count=0,
            total_sessions_completed=0
        )
        return await self.routine_storage.create(routine)
    
    async def get_user_fitness_routines(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all fitness routines for a user."""
        return await self.routine_storage.get_by_user_id(user_id)
    
    async def create_exercise_session(self, data: ExerciseSessionCreate) -> Dict[str, Any]:
        """Log an exercise session."""
        from datetime import datetime, time
        
        end_time = (datetime.combine(date.today(), data.start_time) + 
                   timedelta(minutes=data.duration_minutes)).time()
        
        session = ExerciseSession(
            id="",
            user_id=data.user_id,
            routine_id=data.routine_id,
            date=data.date,
            start_time=data.start_time,
            end_time=end_time,
            duration_minutes=data.duration_minutes,
            intensity=data.intensity,
            calories_burned=None,
            heart_rate_avg=None,
            heart_rate_max=None,
            exercises_completed=data.exercises_completed,
            satisfaction_rating=None,
            notes=None
        )
        return await self.exercise_storage.create(session)
    
    async def get_user_exercise_sessions(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get exercise sessions for a user."""
        records = await self.exercise_storage.get_by_user_id(user_id)
        cutoff = date.today() - timedelta(days=days)
        return [r for r in records if r['date'] >= cutoff.isoformat()]
    
    # Wearable Devices
    async def connect_device(self, request: DeviceConnectRequest) -> Dict[str, Any]:
        """Connect a wearable device."""
        device = DeviceIntegration(
            id="",
            user_id=request.user_id,
            device_id=f"{request.device_type}_{request.user_id}_{int(datetime.now().timestamp())}",
            device_name=request.device_name,
            device_type=request.device_type,
            manufacturer=request.manufacturer,
            connection_status="connected",
            last_sync=datetime.now(),
            data_points_count=0,
            api_token=None,
            created_at=datetime.now()
        )
        return await self.device_storage.create(device)
    
    async def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all connected devices for a user."""
        return await self.device_storage.get_by_user_id(user_id)
    
    async def submit_wearable_data(self, data: WearableDataSubmit) -> Dict[str, Any]:
        """Submit data from a wearable device."""
        record = WearableData(
            id="",
            user_id=data.user_id,
            device_id=data.device_id,
            timestamp=data.timestamp,
            heart_rate=data.heart_rate,
            steps=data.steps,
            sleep_stage=data.sleep_stage,
            vo2_max_estimate=None,
            breathing_rate=None,
            stress_level=data.stress_level,
            blood_oxygen=None
        )
        return await self.wearable_data_storage.create(record)
    
    async def get_user_wearable_data(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get wearable data for a user."""
        records = await self.wearable_data_storage.get_by_user_id(user_id)
        cutoff = datetime.now() - timedelta(days=days)
        return [r for r in records if datetime.fromisoformat(r['timestamp']) >= cutoff]
    
    # Summary
    async def get_physical_ring_summary(
        self, 
        user_id: str,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None
    ) -> PhysicalRingSummary:
        """Generate a summary of the Physical Ring."""
        if not period_start:
            period_start = date.today() - timedelta(days=30)
        if not period_end:
            period_end = date.today()
        
        # Get all data
        time_records = await self.get_user_time_management(user_id, 30)
        activity_records = await self.get_user_activity(user_id, 30)
        sleep_records = await self.get_user_sleep(user_id, 30)
        exercise_records = await self.get_user_exercise_sessions(user_id, 30)
        devices = await self.get_user_devices(user_id)
        
        # Calculate metrics
        time_management_score = 0.5
        if time_records:
            adherence = mean(r['schedule_adherence'] for r in time_records)
            time_management_score = adherence
        
        activity_score = 0.5
        avg_steps = 5000
        if activity_records:
            avg_steps = mean(r['steps'] for r in activity_records)
            activity_score = min(avg_steps / 10000, 1.0)
        
        sleep_score = 0.5
        avg_sleep_hours = 7.0
        if sleep_records:
            avg_sleep_hours = mean(r['total_hours'] for r in sleep_records)
            sleep_score = max(0, 1 - abs(avg_sleep_hours - 8) / 4)
        
        fitness_score = 0.3
        weekly_workouts = len(exercise_records)
        if exercise_records:
            fitness_score = min(weekly_workouts / 12, 1.0)  # 3 per week over 4 weeks
        
        # Overall score
        overall_score = (
            time_management_score * 0.25 +
            activity_score * 0.25 +
            sleep_score * 0.25 +
            fitness_score * 0.25
        )
        
        # Generate recommendations
        recommendations = []
        if time_management_score < 0.5:
            recommendations.append("Try using time-blocking to improve schedule adherence")
        if activity_score < 0.5:
            recommendations.append("Aim for 10,000 steps daily - start with small walks")
        if sleep_score < 0.6:
            recommendations.append("Work on improving sleep quality - aim for 7-9 hours")
        if fitness_score < 0.4:
            recommendations.append("Try to exercise 3 times per week for at least 30 minutes")
        
        return PhysicalRingSummary(
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            time_management_score=round(time_management_score, 2),
            activity_score=round(activity_score, 2),
            sleep_score=round(sleep_score, 2),
            fitness_score=round(fitness_score, 2),
            overall_score=round(overall_score, 2),
            avg_daily_steps=int(avg_steps),
            avg_sleep_hours=round(avg_sleep_hours, 1),
            weekly_workouts=weekly_workouts,
            schedule_adherence_rate=round(time_management_score, 2),
            connected_devices=len(devices),
            recommendations=recommendations
        )


# Global service instance
physical_ring_service = PhysicalRingService()
