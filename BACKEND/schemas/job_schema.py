from pydantic import BaseModel, constr
from datetime import datetime
from enum import Enum

# Usamos un Enum para tener estados predefinidos y evitar errores de tipeo.
class JobStatus(str, Enum):
    POSTED = "posted"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class JobBase(BaseModel):
    title: constr(min_length=5, max_length=100)
    description: constr(max_length=2000)
    category: str
    budget: float

class JobCreate(JobBase):
    pass

class JobOut(JobBase):
    id: str
    client_id: str
    status: JobStatus
    created_at: datetime

    class Config:
        from_attributes = True