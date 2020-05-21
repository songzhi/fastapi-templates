from typing import Dict, Any, TYPE_CHECKING

import orjson
from bson import ObjectId
from pydantic import BaseModel as PydanticBaseModel, Field

ObjectId.__get_validators__ = lambda: [lambda v: ObjectId(v)]

if TYPE_CHECKING:
    from pydantic.typing import DictStrAny


def json_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    if isinstance(v, ObjectId):
        v = str(v)
    return orjson.dumps(v, default=default).decode()


class BaseModel(PydanticBaseModel):
    @classmethod
    def schema(cls, by_alias: bool = True) -> 'DictStrAny':
        from ..utils.openapi import replace_field_type
        for field in cls.__fields__.values():
            replace_field_type(field)
        return super().schema(by_alias)

    class Config:
        use_enum_values = True
        json_loads = orjson.loads
        json_dumps = json_dumps
        json_encoders = {
            ObjectId: lambda v: str(v)
        }
        allow_population_by_field_name = True


class ModelInDb(BaseModel):
    id: ObjectId = Field(None, alias='_id')

    @property
    def dict_no_id(self) -> Dict[str, Any]:
        """
        用这个来创建Doc
        :return:
        """
        return self.dict(exclude={'id'}, by_alias=True)
