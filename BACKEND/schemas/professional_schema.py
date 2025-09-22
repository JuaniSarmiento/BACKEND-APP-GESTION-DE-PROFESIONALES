from pydantic import BaseModel, constr
from typing import List, Optional
from enum import Enum

class VerificationStatus(str, Enum):
    NOT_SUBMITTED = "not_submitted"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class ProfessionalProfileBase(BaseModel):
    headline: constr(max_length=100)
    bio: constr(max_length=1000)
    categories: List[str] = []

class ProfessionalProfileCreate(ProfessionalProfileBase):
    pass

class ProfessionalProfileOut(ProfessionalProfileBase):
    user_id: str
    avg_rating: float = 0.0
    total_reviews: int = 0
    verification_status: VerificationStatus = VerificationStatus.NOT_SUBMITTED
    document_urls: Optional[List[str]] = []

    class Config:
        from_attributes = True