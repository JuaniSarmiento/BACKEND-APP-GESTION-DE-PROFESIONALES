# schemas/review_schema.py
from pydantic import BaseModel, constr, conint, Field
from datetime import datetime
from typing import Optional

class ReviewBase(BaseModel):
    rating: conint(ge=1, le=5)
    comment: constr(max_length=1000)

class ReviewIn(ReviewBase):
    professional_id: str

class ReviewUpdate(BaseModel):
    rating: Optional[conint(ge=1, le=5)] = None
    comment: Optional[constr(max_length=1000)] = None

class ReviewOut(ReviewBase):
    id: str = Field(..., alias="_id")
    client_id: str
    professional_id: str
    created_at: datetime

    class Config:
        from_attributes = True
