from bson.errors import InvalidId
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute
from pydantic import ValidationError
from starlette.middleware.authentication import AuthenticationMiddleware

from .middlewares.auth import AuthBackend
from .utils.openapi import custom_openapi

FastAPI.openapi = custom_openapi

app = FastAPI(
    title='MadForms',
    version='0.1.0',
    default_response_class=ORJSONResponse
)


@app.get("/")
def root():
    pass


def on_auth_error(_, exc: Exception):
    return ORJSONResponse({"error": str(exc)}, status_code=401)


app.add_middleware(AuthenticationMiddleware, backend=AuthBackend(), on_error=on_auth_error)


def set_by_alias_as_false(router: APIRouter) -> APIRouter:
    for route in router.routes:
        if isinstance(route, APIRoute):
            route.response_model_by_alias = False
    return router


@app.exception_handler(InvalidId)
def handle_invalid_object_id(_, _exc):
    return ORJSONResponse(status_code=400, content='错误的ObjectId')


@app.exception_handler(ValidationError)
def handle_pydantic_validation_error(_, exc: ValidationError):
    return ORJSONResponse(status_code=422, content=exc.json())


@app.exception_handler(HTTPException)
def handle_http_exception(_, exc: HTTPException):
    return ORJSONResponse(status_code=exc.status_code, content=exc.detail)
