import re
from enum import Enum
from itertools import chain
from typing import Sequence, Dict, Set, Type, Any, Union

from bson import ObjectId
from fastapi import FastAPI, routing
from fastapi.openapi.constants import REF_PREFIX
from fastapi.openapi.utils import get_openapi_path, get_flat_models_from_routes
from fastapi.routing import APIRoute
from pydantic import BaseModel
from pydantic.fields import ModelField
from pydantic.schema import get_model_name_map, model_process_schema
from starlette.routing import BaseRoute


def generate_operation_id_for_path(*, name: str, path: str) -> str:
    operation_id = name + path
    operation_id = re.sub("[^0-9a-zA-Z_]", "_", operation_id)
    # operation_id = operation_id + "_" + method.lower()
    return operation_id


def replace_field_type(field: ModelField):
    if isinstance(field.type_, type) and issubclass(field.type_, ObjectId):
        if field.name == 'id':
            field.required = True
        field.type_ = str
    elif isinstance(field.type_, type) and issubclass(field.type_, Enum):
        field.field_info.extra['x-enum-varnames'] = field.type_._member_names_
    elif getattr(field.type_, '__origin__', None) and ObjectId in field.type_.__args__:
        field.type_.__args__ = tuple(map(lambda v: str if v is ObjectId else v, field.type_.__args__))
    if field.sub_fields:
        for f in field.sub_fields:
            replace_field_type(f)


def get_model_definitions(
        *,
        flat_models: Set[Union[Type[BaseModel], Type[Enum]]],
        model_name_map: Dict[Union[Type[BaseModel], Type[Enum]], str],
) -> Dict[str, Any]:
    definitions: Dict[str, Dict] = {}
    for model in filter(lambda m: issubclass(m, BaseModel), flat_models):
        # 将类型为ObjectId的字段的类型改为str
        for field in model.__fields__.values():
            replace_field_type(field)
    for model in flat_models:
        # ignore mypy error until enum schemas are released
        m_schema, m_definitions, m_nested_models = model_process_schema(
            model, model_name_map=model_name_map, ref_prefix=REF_PREFIX  # type: ignore
        )
        definitions.update(m_definitions)
        model_name = model_name_map[model]
        definitions[model_name] = m_schema
    return definitions


def get_openapi(
        *,
        title: str,
        version: str,
        openapi_version: str = "3.0.2",
        description: str = None,
        routes: Sequence[BaseRoute],
        openapi_prefix: str = ""
) -> Dict:
    info = {"title": title, "version": version}
    if description:
        info["description"] = description
    output = {"openapi": openapi_version, "info": info}
    components: Dict[str, Dict] = {}
    paths: Dict[str, Dict] = {}
    flat_models = get_flat_models_from_routes(routes)
    model_name_map = get_model_name_map(flat_models)
    definitions = get_model_definitions(
        flat_models=flat_models, model_name_map=model_name_map
    )
    for route in routes:
        if isinstance(route, routing.APIRoute):
            # 将path和query中的ObjectId显示为str
            for field in chain(route.dependant.path_params, route.dependant.query_params):
                replace_field_type(field)
            result = get_openapi_path(route=route, model_name_map=model_name_map)
            if result:
                path, security_schemes, path_definitions = result
                if path:
                    # 在schema中删除auth_token,authorization头
                    for _, op in path.items():
                        if op.get('parameters'):
                            op['parameters'] = list(filter(lambda p: p['name'] not in ['auth_token', 'authorization'],
                                                           op['parameters']))
                    paths.setdefault(openapi_prefix + route.path_format, {}).update(
                        path
                    )
                if security_schemes:
                    components.setdefault("securitySchemes", {}).update(
                        security_schemes
                    )
                if path_definitions:
                    definitions.update(path_definitions)
    if definitions:
        components["schemas"] = {k: definitions[k] for k in sorted(definitions)}
    if components:
        output["components"] = components
    output["paths"] = paths
    # return jsonable_encoder(OpenAPI(**output), by_alias=True, include_none=False)
    return output


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    for r in app.routes:
        if isinstance(r, APIRoute):
            r.operation_id = r.name
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema
