from datetime import datetime
from enum import Enum
from typing import List, Optional

from bson import ObjectId
from pydantic import EmailStr
from starlette.authentication import BaseUser

from .base import BaseModel, ModelInDb


class UserBase(ModelInDb):
    username: str
    avatar: Optional[str] = None


class User(ModelInDb):
    username: str
    email: str
    password: str
    scopes: List[str] = []
    created_at: datetime


class AuthenticatedUser(BaseModel, BaseUser):
    id: ObjectId
    username: str
    scopes: List[str]
    avatar: Optional[str] = None

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def identity(self) -> str:
        return str(self.id)

    @property
    def display_name(self) -> str:
        return f'User({self.id})'

    @property
    def is_admin(self) -> bool:
        return 'admin' in self.scopes

    @property
    def as_user_base(self) -> UserBase:
        return UserBase(id=self.id, username=self.username, avatar=self.avatar)


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserUpdate(BaseModel):
    username: str = None
    password: str = None
    avatar: str = None


class LoginType(Enum):
    Email = 'email'


class LoginInput(BaseModel):
    type: LoginType = LoginType.Email
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    user: User
