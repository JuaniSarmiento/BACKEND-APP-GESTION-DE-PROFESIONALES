# schemas/job_schema.py
from pydantic import BaseModel, constr, Field
from datetime import datetime
from enum import Enum
from typing import Optional

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

class JobIn(JobBase):
    professional_id: str

class JobUpdate(BaseModel):
    title: Optional[constr(min_length=5, max_length=100)] = None
    description: Optional[constr(max_length=2000)] = None
    category: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[JobStatus] = None

class JobOut(JobBase):
    id: str = Field(..., alias="_id")
    client_id: str
    professional_id: str
    status: JobStatus
    created_at: datetime

    class Config:
        from_attributes = True
