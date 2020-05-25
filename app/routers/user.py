from bson import ObjectId
from fastapi import APIRouter, Query, Depends

from .dependencies import GetAuthUser, AuthUser
from ..dao.user import USER_DAO
from ..models import user as models

router = APIRouter()


@router.post('/', response_model=models.User)
async def create_user(user_create: models.UserCreate):
    return await USER_DAO.insert(user_create)


@router.post('/token/', response_model=models.LoginResponse)
async def login(login_input: models.LoginInput, expires_hours: int = Query(1200, description='token多少小时后过期')):
    return await USER_DAO.login(login_input, expires_hours)


@router.get('/{pk}/', response_model=models.User)
async def get_user(pk: ObjectId):
    return await USER_DAO.find_one(pk)


@router.put('/{pk}/')
async def update_user(pk: ObjectId, user_update: models.UserUpdate,
                      auth_user: AuthUser = Depends(GetAuthUser(is_strict=True))):
    await USER_DAO.update(pk, user_update, auth_user)

