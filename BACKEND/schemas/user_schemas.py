# schemas/user_schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str = Field(..., alias='firstName')
    last_name: str = Field(..., alias='lastName')
    role: Literal['client', 'professional']

    class Config:
        populate_by_name = True

class UserIn(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    first_name: Optional[str] = Field(default=None, alias='firstName')
    last_name: Optional[str] = Field(default=None, alias='lastName')

class UserOut(UserBase):
    id: str = Field(..., alias="_id")
