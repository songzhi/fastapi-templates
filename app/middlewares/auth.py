from typing import Optional, Tuple

from jose import JWTError, ExpiredSignatureError
from pydantic import ValidationError
from starlette.authentication import AuthenticationBackend, AuthCredentials, AuthenticationError
from starlette.requests import Request

from ..models.user import AuthenticatedUser
from ..utils.jwt import decode_token


def get_user_from_header(auth_header: str) -> Optional[Tuple[AuthCredentials, AuthenticatedUser]]:
    try:
        scheme, token = auth_header.split()
        if scheme.lower() == 'bearer':
            payload = decode_token(token)
            return AuthCredentials(payload['scopes']), AuthenticatedUser(**payload)
        return
    except ExpiredSignatureError:
        raise AuthenticationError('Token expired')
    except JWTError:
        raise AuthenticationError("Auth failed")
    except (ValueError, UnicodeDecodeError, KeyError, ValidationError, AttributeError):
        return


class AuthBackend(AuthenticationBackend):
    async def authenticate(self, request: Request) -> Optional[Tuple[AuthCredentials, AuthenticatedUser]]:
        return get_user_from_header(request.headers.get('Authorization', None))
