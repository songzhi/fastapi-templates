from datetime import datetime, timedelta
from typing import Union, Dict, Any

from bson import ObjectId
from fastapi import HTTPException
from pydantic.typing import DictStrAny
from starlette import status

from .base import BaseDao
from ..config import TZ
from ..models import user as models
from ..utils import unwrap_or_404, encryption, jwt


def create_user_token(user: Union[models.User, Dict[str, Any]], expires: timedelta) -> str:
    if isinstance(user, models.User):
        user = user.dict()
    payload = {
        'id': str(user['id']),
        'scopes': user['scopes'],
        'avatar': user.get('avatar', None),
        'username': user['username'],
    }
    return jwt.create_token(payload, expires)


class UserDao(BaseDao):

    async def insert(self, user_create: models.UserCreate) -> models.User:
        user = models.User(**user_create.dict(), created_at=datetime.now(TZ))
        result = await self.collection.insert_one(user.dict_no_id)
        user.id = result.inserted_id
        return user

    async def find_one(self, user_id: ObjectId, projection: DictStrAny = None) -> models.User:
        projection = projection or {
            'password': 0
        }
        user = models.User(**unwrap_or_404(await self.collection.find_one({'_id': user_id}, projection)))
        return user

    async def update(self, user_id: ObjectId, user_update: models.UserUpdate, auth_user: models.AuthenticatedUser):
        if user_id != auth_user.id and not auth_user.is_admin:
            raise HTTPException(status.HTTP_403_FORBIDDEN)
        if user_update.password is not None:
            user_update.password = encryption.hash_password(user_update.password)
        await self.collection.update_one({'_id': user_id}, {'$set': user_update.dict(exclude_unset=True)})

    async def login_with_email(self, login_input: models.LoginInput) -> models.User:
        password = encryption.hash_password(login_input.password.strip())
        projection = {
            'password': 0,
        }
        user = models.User(
            **unwrap_or_404(
                await self.collection.find_one({'email': login_input.email, 'password': password}, projection)))
        return user

    async def login(self, login_input: models.LoginInput, expire_hours: int = 1200) -> models.LoginResponse:
        if login_input.type == models.LoginType.Email:
            user = await self.login_with_email(login_input)
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)
        token = create_user_token(user, expires=timedelta(hours=expire_hours))
        return models.LoginResponse(user=user, token=token)
