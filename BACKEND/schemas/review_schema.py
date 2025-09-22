from pydantic import BaseModel, constr, conint
from datetime import datetime

class ReviewBase(BaseModel):
    rating: conint(ge=1, le=5) # El rating debe ser un entero entre 1 y 5
    comment: constr(max_length=1000)

class ReviewCreate(ReviewBase):
    pass

class ReviewOut(ReviewBase):
    id: str
    job_id: str
    client_id: str
    professional_id: str
    created_at: datetime

    class Config:
        from_attributes = True