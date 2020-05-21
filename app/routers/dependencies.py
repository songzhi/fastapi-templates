from typing import Union, Sequence

from fastapi import HTTPException, Header, Query
from starlette import status
from starlette.authentication import UnauthenticatedUser
from starlette.requests import Request

from ..middlewares.auth import get_user_from_header
from ..models.user import AuthenticatedUser
from ..utils import Context
from ..utils.paging import get_paging_args, Paging, PagingResponse


def get_context(request: Request) -> Context:
    return Context({
        'user': request.user,
        'request': request
    })


AuthUser = Union[AuthenticatedUser, UnauthenticatedUser]


class GetAuthUser:
    def __init__(self, is_strict=False, scopes: Sequence[str] = None):
        self.scopes = [] if scopes is None else list(scopes)
        self.is_strict = is_strict

    async def __call__(self, authorization: str = Header(None),
                       auth_token: str = Query(None)) -> AuthUser:
        if authorization is not None:
            auth = get_user_from_header(authorization)
        elif auth_token is not None:
            auth = get_user_from_header(f'bearer {auth_token}')
        else:
            auth = None
        if auth is None:
            if self.is_strict:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='未登录')
            else:
                return UnauthenticatedUser()
        credentials, user = auth
        if not set(self.scopes).issubset(set(credentials.scopes)):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='权限不足')
        return user


__all__ = ['get_paging_args', 'GetAuthUser', 'get_context', 'AuthenticatedUser', 'UnauthenticatedUser', 'Paging',
           'PagingResponse', 'AuthUser']
