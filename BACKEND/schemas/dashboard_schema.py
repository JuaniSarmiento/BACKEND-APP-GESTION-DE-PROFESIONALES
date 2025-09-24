# schemas/dashboard_schema.py
from pydantic import BaseModel, Field
from typing import List, Any

class AggregationResult(BaseModel):
    id: Any = Field(..., alias='_id')
    count: int

    class Config:
        populate_by_name = True

class DashboardStats(BaseModel):
    total_users: int
    total_professionals: int
    total_jobs: int
    jobs_by_state: List[AggregationResult]
    professionals_by_category: List[AggregationResult]