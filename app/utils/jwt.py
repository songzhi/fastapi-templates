from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from ..config import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from ..config import TZ


def create_token(payload: dict,
                 expires_delta: Optional[timedelta] = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    to_encode = payload.copy()
    expire = datetime.now(TZ) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
