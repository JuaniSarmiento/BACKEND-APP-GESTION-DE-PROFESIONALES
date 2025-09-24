# schemas/professional_schema.py
from pydantic import BaseModel, constr, Field
from typing import List, Optional
from enum import Enum

class VerificationStatus(str, Enum):
    NOT_SUBMITTED = "not_submitted"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class ProfessionalBase(BaseModel):
    headline: constr(max_length=100)
    bio: constr(max_length=1000)
    categories: List[str] = Field(default_factory=list)

class ProfessionalIn(ProfessionalBase):
    pass

class ProfessionalUpdate(BaseModel):
    headline: Optional[constr(max_length=100)] = None
    bio: Optional[constr(max_length=1000)] = None
    categories: Optional[List[str]] = None

class ProfessionalOut(ProfessionalBase):
    id: str = Field(..., alias="_id")
    user_id: str
    avg_rating: float = 0.0
    total_reviews: int = 0
    verification_status: VerificationStatus = VerificationStatus.NOT_SUBMITTED
    document_urls: Optional[List[str]] = Field(default_factory=list)

    class Config:
        from_attributes = True
