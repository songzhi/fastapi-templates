import ast
import collections
import functools
from typing import Callable, Optional, Any, Iterable, Sized, Union, TypeVar

import more_itertools
from attrdict import AttrDict
from fastapi import HTTPException
from starlette.authentication import UnauthenticatedUser
from starlette.requests import Request
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from ..models.user import AuthenticatedUser


class Context(AttrDict):
    user: Union[AuthenticatedUser, UnauthenticatedUser]
    request: Request


def call_only_once(func: Callable) -> Callable:
    def new_func(*args, **kwargs):
        if not getattr(new_func, '__called', False):
            try:
                return func(*args, **kwargs)
            finally:
                new_func.__called = True

    return new_func


def to_str(x) -> str:
    """
    return str(x) if x else ''
    :param x: any
    :return: str(x) if x else ''
    """
    return str(x) if x else ''


def str_to_bool(s: str) -> bool:
    if s is None:
        return False
    try:
        return bool(ast.literal_eval(s.title()))
    except ValueError:
        return False


def parse_int(pk: str) -> int:
    try:
        return int(pk)
    except ValueError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST)


def int_or_default(x: Optional[Any], default: int = 0) -> int:
    return int(x) if x is not None else default


class memoized:
    """Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.abc.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, obj_type):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


def ilen(x: Iterable[Any]) -> int:
    if isinstance(x, Sized):
        return len(x)
    return more_itertools.ilen(x)


T = TypeVar('T')


def unwrap_or_404(obj: Optional[T], detail='Not Found') -> T:
    if obj is None:
        raise HTTPException(HTTP_404_NOT_FOUND, detail=detail)
    else:
        return obj
