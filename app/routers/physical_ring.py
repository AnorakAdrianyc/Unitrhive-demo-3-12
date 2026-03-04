"""Physical Ring router for UniThrive.

Handles time management, sleep, fitness, and wearable integration endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.physical_ring import (
    TimeManagementCreate, DailyActivityCreate, SleepRecordCreate,
    FitnessRoutineCreate, ExerciseSessionCreate,
    DeviceConnectRequest, WearableDataSubmit
)
from app.services.physical_ring_service import physical_ring_service

router = APIRouter()


@router.post("/time-management", status_code=status.HTTP_201_CREATED)
async def log_time_management(data: TimeManagementCreate):
    """Log daily time management behavior."""
    try:
        result = await physical_ring_service.create_time_management(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/time-management/{user_id}")
async def get_time_management(user_id: str, days: int = 30):
    """Get time management records."""
    records = await physical_ring_service.get_user_time_management(user_id, days)
    return {"user_id": user_id, "records": records, "count": len(records)}


@router.post("/activity", status_code=status.HTTP_201_CREATED)
async def record_daily_activity(data: DailyActivityCreate):
    """Record daily physical activity."""
    try:
        result = await physical_ring_service.create_daily_activity(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/activity/{user_id}")
async def get_daily_activity(user_id: str, days: int = 30):
    """Get activity records."""
    records = await physical_ring_service.get_user_activity(user_id, days)
    return {"user_id": user_id, "records": records, "count": len(records)}


@router.post("/sleep", status_code=status.HTTP_201_CREATED)
async def log_sleep(data: SleepRecordCreate):
    """Log sleep data."""
    try:
        result = await physical_ring_service.create_sleep_record(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sleep/{user_id}")
async def get_sleep_records(user_id: str, days: int = 30):
    """Get sleep records."""
    records = await physical_ring_service.get_user_sleep(user_id, days)
    return {"user_id": user_id, "records": records, "count": len(records)}


@router.post("/fitness", status_code=status.HTTP_201_CREATED)
async def create_fitness_routine(data: FitnessRoutineCreate):
    """Create a fitness routine."""
    try:
        result = await physical_ring_service.create_fitness_routine(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/fitness/{user_id}")
async def get_fitness_routines(user_id: str):
    """Get fitness routines."""
    routines = await physical_ring_service.get_user_fitness_routines(user_id)
    return {"user_id": user_id, "routines": routines, "count": len(routines)}


@router.post("/exercise", status_code=status.HTTP_201_CREATED)
async def log_exercise_session(data: ExerciseSessionCreate):
    """Log an exercise session."""
    try:
        result = await physical_ring_service.create_exercise_session(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/exercise/{user_id}")
async def get_exercise_sessions(user_id: str, days: int = 30):
    """Get exercise sessions."""
    sessions = await physical_ring_service.get_user_exercise_sessions(user_id, days)
    return {"user_id": user_id, "sessions": sessions, "count": len(sessions)}


@router.post("/wearables", status_code=status.HTTP_201_CREATED)
async def connect_wearable(request: DeviceConnectRequest):
    """Connect a wearable device."""
    try:
        result = await physical_ring_service.connect_device(request)
        return {"status": "success", "data": result, "message": f"Device {request.device_name} connected successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/wearables/{user_id}")
async def get_connected_devices(user_id: str):
    """Get connected wearable devices."""
    devices = await physical_ring_service.get_user_devices(user_id)
    return {"user_id": user_id, "devices": devices, "count": len(devices)}


@router.post("/wearable-data", status_code=status.HTTP_201_CREATED)
async def submit_wearable_data(data: WearableDataSubmit):
    """Submit data from a wearable device."""
    try:
        result = await physical_ring_service.submit_wearable_data(data)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/wearable-data/{user_id}")
async def get_wearable_data(user_id: str, days: int = 7):
    """Get wearable data."""
    data = await physical_ring_service.get_user_wearable_data(user_id, days)
    return {"user_id": user_id, "data_points": data, "count": len(data)}


@router.get("/summary/{user_id}")
async def get_physical_ring_summary(user_id: str):
    """Get Physical Ring summary for a user."""
    summary = await physical_ring_service.get_physical_ring_summary(user_id)
    return summary
