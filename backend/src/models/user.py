from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: Optional[str] = None


class UserProfile(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
