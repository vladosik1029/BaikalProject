from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta
from typing import Optional

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: str | None = None
    role: str | None = None

class User(UserBase):
    id: int
    is_active: bool
    role: str

    class Config:
        from_attributes = True
        
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str