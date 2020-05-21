import json
from typing import TypeVar, Generic, List, Optional, Any, Tuple, Dict, Type

import orjson
import pymongo
from fastapi import Query
from pydantic import Field
from pydantic.generics import GenericModel

from ..models.base import BaseModel
from ..models.base import ObjectId


class Paging(BaseModel):
    sort: str = '_id'
    skip: int = 0
    after: Optional[Any] = None
    limit: int = 15
    total: Optional[int] = None

    @property
    def sort_arg(self) -> List[Tuple[str, int]]:
        fields = self.sort.split()
        args = []
        for field in fields:
            if field.startswith('-'):
                args.append((field[1:], pymongo.DESCENDING))
            else:
                args.append((field.lstrip('+'), pymongo.ASCENDING))
        return args

    @property
    def filter_arg(self) -> Dict[str, Any]:
        args = {}
        ops_map = {
            pymongo.ASCENDING: '$gt',
            pymongo.DESCENDING: '$lt'
        }
        if self.after is not None:
            sort_field, direction = self.sort_arg[0]
            args[sort_field] = {ops_map[direction]: self.after}
        return args

    @property
    def other_args(self) -> Dict[str, Any]:
        return {
            'sort': self.sort_arg,
            'skip': self.skip,
            'limit': self.limit
        }


def get_paging_args(sort: str = Query('_id', description='按哪个字段排序,前加减号为逆序,加号或不加为正序'),
                    skip: int = Query(0, description='跳过n项;如果和after一起使用,意为在after值之后跳过n项'),
                    after: str = Query(None, description='上一页最后一项中排序字段的值,用于加速查询,以json格式序列化'),
                    total: Optional[int] = Query(None, description='查询总数;如果值为None或-1则从数据库中获取,值为其他则直接返回该值'),
                    limit: int = Query(15, description='值为0代表不限长')) -> Paging:
    if after is not None:
        try:
            after = orjson.loads(after)
        except json.decoder.JSONDecodeError:
            pass
        if sort.endswith('_id'):
            after = ObjectId(after)
    if total == -1:
        total = None
    return Paging(sort=sort, skip=skip, after=after, limit=limit, total=total)


ResultsT = TypeVar('ResultsT')


class PagingResponse(GenericModel, Generic[ResultsT]):
    items: List[ResultsT] = Field(..., description='返回的数据')
    total: int = Field(..., description='筛选过后的集合总数,不是`items`的长度')
    has_more: bool = Field(..., description='是否有更多数据')

    @classmethod
    def __concrete_name__(cls: Type[Any], params: Tuple[Type[Any], ...]) -> str:
        return f'{params[0].__name__.title()}PagingResponse'

    class Config:
        use_enum_values = True
        json_encoders = {
            ObjectId: lambda v: str(v)
        }
        allow_population_by_field_name = True
        schema_extra = {
            'description': '分页响应'
        }
