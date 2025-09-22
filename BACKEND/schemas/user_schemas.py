from pydantic import BaseModel, EmailStr
from typing import Literal

class UserBase(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    role: Literal['client', 'professional']

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: str

    class Config:
        from_attributes = True # Reemplazo de orm_mode