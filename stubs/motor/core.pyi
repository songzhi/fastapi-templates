from typing import List, Union, Dict, Any, Tuple, Optional, Callable, FrozenSet, Coroutine

from bson import SON
from bson.codec_options import CodecOptions
from pymongo import ReturnDocument, ReadPreference
from pymongo.client_session import TransactionOptions, SessionOptions
from pymongo.collation import Collation
from pymongo.operations import *
from pymongo.read_concern import ReadConcern
from pymongo.results import *
from pymongo.write_concern import WriteConcern

RequestsT = List[Union[UpdateMany, UpdateOne, InsertOne, DeleteMany, DeleteOne, ReplaceOne, IndexModel]]
FilterT = Dict[str, Any]
DocT = Dict[str, Any]
SortT = List[Tuple[str, Any]]
PipelineT = List[Dict[str, Dict[str, Any]]]


class AgnosticBase:
    delegate: Any

    def __eq__(self, other): ...

    def __init__(self, delegate): ...

    def __repr__(self): ...


class AgnosticBaseProperties(AgnosticBase):
    codec_options: CodecOptions
    read_preference: ReadPreference
    read_concern: ReadConcern
    write_concern: WriteConcern


class AgnosticClient(AgnosticBaseProperties):
    # TODO:
    address: Tuple[str, int]
    arbiters: List[Tuple[str, int]]
    event_listeners: Any
    HOST: str
    is_mongos: bool
    is_primary: bool
    local_threshold_ms: int
    max_bson_size: int
    max_idle_time_ms: int
    max_message_size: int
    max_pool_size: int
    max_write_batch_size: int
    min_pool_size: int
    nodes: FrozenSet[Tuple[str, int]]
    PORT: int
    primary: Tuple[str, int]
    read_concern: ReadConcern
    retry_reads: bool
    retry_writes: bool
    secondaries: List[Tuple[str, int]]
    server_selection_timeout: int

    def __init__(self, *args, **kwargs): ...

    def __getattr__(self, name: str) -> AgnosticDatabase: ...

    def __getitem__(self, name: str) -> AgnosticDatabase: ...

    def close(self): ...

    async def drop_database(self, name_or_database: Union[str, AgnosticDatabase],
                            session: AgnosticClientSession = None): ...

    async def fsync(self, **kwargs): ...

    def get_database(self, name: str = None, codec_options: CodecOptions = None, read_preference: ReadPreference = None,
                     write_concern: WriteConcern = None, read_concern: ReadConcern = None) -> AgnosticDatabase: ...

    def get_default_database(self, default=None, codec_options: CodecOptions = None,
                             read_preference: ReadPreference = None, write_concern: WriteConcern = None,
                             read_concern: ReadConcern = None) -> AgnosticDatabase: ...

    async def list_databases(self, session: AgnosticClientSession = None) -> List[AgnosticDatabase]: ...

    async def list_database_names(self, session: AgnosticClientSession = None) -> List[str]: ...

    async def server_info(self, session: AgnosticClientSession) -> Dict[str, Any]: ...

    async def start_session(self, causal_consistency=True,
                            default_transaction_options: TransactionOptions = None) -> AgnosticClientSession: ...

    async def unlock(self, session: AgnosticClientSession) -> None: ...

    def watch(self, pipeline: List[Dict[str, Any]] = None, full_document=None, resume_after=None,
              max_await_time_ms=None, batch_size=None,
              collation=None, start_at_operation_time=None, session=None, start_after=None): ...


class AgnosticClientSession(AgnosticBase):
    cluster_time: int
    has_ended: bool
    in_transaction: bool
    options: SessionOptions
    operation_time: int
    session_id: str
    client: AgnosticClient

    def __init__(self, delegate, motor_client): ...

    async def commit_transaction(self) -> None: ...

    async def abort_transaction(self) -> None: ...

    async def end_session(self) -> None: ...

    def advance_cluster_time(self, cluster_time) -> int: ...

    def advance_operation_time(self, operation_time) -> int: ...

    def get_io_loop(self) -> Any: ...

    async def with_transaction(self, coro: Coroutine, read_concern: ReadConcern = None,
                               write_concern: WriteConcern = None, read_preference: ReadPreference = None,
                               max_commit_time_ms: int = None) -> Any: ...

    def start_transaction(self, read_concern: ReadConcern = None, write_concern: WriteConcern = None,
                          read_preference: ReadPreference = None, max_commit_time_ms: int = None): ...

    async def __aenter__(self) -> AgnosticClientSession: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb): ...


class AgnosticDatabase(AgnosticBaseProperties):
    name: str
    client: AgnosticClient

    def __init__(self, client: AgnosticClient, name: str, **kwargs): ...

    async def command(self, command, value=1, check=True, allowable_errors=None, read_preference=None,
                      codec_options: CodecOptions = None, session: AgnosticClientSession = None, **kwargs) -> Any: ...

    async def create_collection(self, name: str, codec_options: CodecOptions = None,
                                read_preference: ReadPreference = None,
                                write_concern: WriteConcern = None, read_concern: ReadConcern = None,
                                session: AgnosticClientSession = None, **kwargs) -> AgnosticCollection: ...

    async def dereference(self, dbref, session=None, **kwargs) -> Optional[DocT]: ...

    async def drop_collection(self, name_or_collection: Union[str, AgnosticCollection],
                              session: AgnosticClientSession = None) -> None: ...

    async def get_collection(self, name: str, codec_options: CodecOptions = None,
                             read_preference: ReadPreference = None, write_concern: WriteConcern = None,
                             read_concern: ReadConcern = None) -> AgnosticCollection: ...

    async def list_collection_names(self, session=None, filter=None, **kwargs) -> List[str]: ...

    async def list_collections(self, session=None, filter=None, **kwargs) -> List[AgnosticCollection]: ...

    async def profiling_info(self, session: AgnosticClientSession = None) -> List[Any]: ...

    async def profiling_level(self, session: AgnosticClientSession = None) -> int: ...

    async def set_profiling_level(self, level: int, slow_ms: int = None, session: AgnosticClientSession = None): ...

    async def validate_collection(self, name_or_collection: Union[str, AgnosticCollection], scandata=False, full=False,
                                  session: AgnosticClientSession = None) -> Dict[str, Any]: ...

    def with_options(self, codec_options: CodecOptions = None, read_preference: ReadPreference = None,
                     write_concern: WriteConcern = None, read_concern=None) -> AgnosticDatabase: ...

    def aggregate(self, pipeline: PipelineT, **kwargs) -> AgnosticCommandCursor: ...

    def watch(self, pipeline: PipelineT = None, full_document=None, resume_after=None,
              max_await_time_ms=None, batch_size=None, collation=None,
              start_at_operation_time=None, session=None, start_after=None) -> AgnosticChangeStream: ...

    def __getattr__(self, name: str) -> AgnosticCollection: ...

    def __getitem__(self, name: str) -> AgnosticCollection: ...


class AgnosticBaseCursor(AgnosticBase):
    address: str
    cursor_id: str
    alive: bool
    session: AgnosticClientSession

    def __init__(self, cursor, collection: AgnosticCollection):
        super().__init__(cursor)
        ...

    async def to_list(self, length: int) -> List[DocT]: ...

    def each(self, callback: Callable) -> None: ...

    def next_object(self) -> Optional[DocT]: ...

    @property
    async def fetch_next(self) -> Optional[DocT]: ...

    async def close(self) -> None: ...

    def batch_size(self, batch_size) -> AgnosticBaseCursor: ...

    def __aiter__(self) -> AgnosticBaseCursor: ...

    async def __anext__(self) -> Optional[DocT]: ...


class AgnosticCursor(AgnosticBaseCursor):
    async def distinct(self, key: str) -> List[Any]: ...

    async def explain(self) -> Any: ...

    def collation(self, collation) -> AgnosticCursor: ...

    def add_option(self, mask: int) -> AgnosticCursor: ...

    def remove_option(self, mask: int) -> AgnosticCursor: ...

    def limit(self, limit: int) -> AgnosticCursor: ...

    def skip(self, skip: int) -> AgnosticCursor: ...

    def max_scan(self, max_scan: int) -> AgnosticCursor: ...

    def sort(self, key_or_list: Union[str, SortT], direction=None) -> AgnosticCursor: ...

    def hint(self, index) -> AgnosticCursor: ...

    def where(self, code: str) -> AgnosticCursor: ...

    def max_await_time_ms(self, max_await_time_ms: int) -> AgnosticCursor: ...

    def max_time_ms(self, max_time_ms) -> AgnosticCursor: ...

    def min(self, spec: List[Tuple[str, Any]]) -> AgnosticCursor: ...

    def max(self, spec: List[Tuple[str, Any]]) -> AgnosticCursor: ...

    def comment(self, comment: str) -> AgnosticCursor: ...

    def rewind(self) -> AgnosticCursor: ...

    def clone(self) -> AgnosticCursor: ...

    def __copy__(self): ...

    def __deepcopy__(self, memo): ...


class AgnosticRawBatchCursor(AgnosticCursor):
    ...


class AgnosticCommandCursor(AgnosticBaseCursor):
    ...


class AgnosticRawBatchCommandCursor(AgnosticCommandCursor):
    ...


class AgnosticLatentCommandCursor(AgnosticCommandCursor):
    ...


class AgnosticChangeStream(AgnosticBase):
    def __init__(self, target, pipeline, full_document, resume_after,
                 max_await_time_ms, batch_size, collation,
                 start_at_operation_time, session, start_after): ...

    def __aiter__(self) -> AgnosticChangeStream: ...

    async def next(self): ...

    async def try_next(self): ...

    async def close(self): ...

    async def __anext__(self): ...

    async def __aenter__(self): ...

    async def __aexit__(self, exc_type, exc_val, exc_tb): ...


class AgnosticCollection(AgnosticBaseProperties):
    """A Mongo collection.
    """

    def __init__(self, database: AgnosticDatabase, name: str, codec_options: CodecOptions = None,
                 read_preference: ReadPreference = None, write_concern: WriteConcern = None,
                 read_concern: ReadConcern = None, _delegate=None): ...

    def __getattr__(self, name: str) -> AgnosticCollection: ...

    def __getitem__(self, name: str) -> AgnosticCollection: ...

    def __repr__(self): ...

    def __eq__(self, other): ...

    def __ne__(self, other): ...

    @property
    def full_name(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def database(self) -> AgnosticDatabase: ...

    def with_options(self, codec_options: CodecOptions = None, read_preference: ReadPreference = None,
                     write_concern: WriteConcern = None, read_concern: ReadConcern = None):
        ...

    def initialize_unordered_bulk_op(self, bypass_document_validation=False):
        ...

    def initialize_ordered_bulk_op(self, bypass_document_validation=False):
        ...

    async def bulk_write(self, requests: RequestsT, ordered=True, bypass_document_validation=False,
                         session: AgnosticClientSession = None) -> BulkWriteResult:
        ...

    async def insert_one(self, document: DocT, bypass_document_validation=False,
                         session: AgnosticClientSession = None) -> InsertOneResult:
        ...

    async def insert_many(self, documents: List[DocT], ordered=True,
                          bypass_document_validation=False, session: AgnosticClientSession = None) -> InsertManyResult:
        ...

    async def replace_one(self, filter: FilterT, replacement: DocT, upsert=False,
                          bypass_document_validation=False, collation: Collation = None,
                          session: AgnosticClientSession = None) -> UpdateResult:
        ...

    async def update_one(self, filter: FilterT, update: DocT, upsert=False,
                         bypass_document_validation=False,
                         collation: Collation = None, array_filters: List[FilterT] = None,
                         session: AgnosticClientSession = None) -> UpdateResult:
        ...

    async def update_many(self, filter: FilterT, update: DocT, upsert=False, array_filters=None,
                          bypass_document_validation=False, collation: Collation = None,
                          session: AgnosticClientSession = None) -> UpdateResult:
        ...

    async def drop(self, session: AgnosticClientSession = None): ...

    async def delete_one(self, filter: FilterT, collation: Collation = None,
                         session: AgnosticClientSession = None) -> DeleteResult:
        ...

    async def delete_many(self, filter: FilterT, collation: Collation = None,
                          session: AgnosticClientSession = None) -> DeleteResult:
        ...

    async def find_one(self, filter: FilterT = None, *args, **kwargs) -> Optional[DocT]:
        ...

    def find(self, *args, **kwargs) -> AgnosticCursor:
        ...

    def find_raw_batches(self, *args, **kwargs) -> AgnosticRawBatchCursor:
        ...

    async def estimated_document_count(self, **kwargs) -> int:
        ...

    async def count_documents(self, filter: FilterT, session: AgnosticClientSession = None,
                              **kwargs) -> int:
        ...

    def create_indexes(self, indexes: List[IndexModel], session: AgnosticClientSession = None, **kwargs) -> List[str]:
        ...

    async def create_index(self, keys: Union[str, SortT], session: AgnosticClientSession = None,
                           **kwargs) -> None:
        ...

    async def drop_indexes(self, session: AgnosticClientSession = None, **kwargs): ...

    async def drop_index(self, index_or_name: Union[IndexModel, str], session: AgnosticClientSession = None,
                         **kwargs) -> None:
        ...

    async def reindex(self, session: AgnosticClientSession = None, **kwargs):
        ...

    def list_indexes(self, session=None) -> AgnosticLatentCommandCursor:
        ...

    async def index_information(self, session: AgnosticClientSession = None) -> Dict[str, Dict[str, Any]]:
        ...

    async def options(self, session: AgnosticClientSession = None) -> Dict[str, Any]:
        ...

    def aggregate(self, pipeline: PipelineT, **kwargs) -> AgnosticCommandCursor:
        ...

    def aggregate_raw_batches(self, pipeline: PipelineT, **kwargs) -> AgnosticRawBatchCommandCursor:
        ...

    def watch(self, pipeline: List[Dict[str, Any]] = None, full_document=None, resume_after=None,
              max_await_time_ms=None, batch_size=None, collation=None,
              start_at_operation_time=None, session=None, start_after=None):
        ...

    async def rename(self, new_name: str, session: AgnosticClientSession = None, **kwargs):
        ...

    async def distinct(self, key: str, filter: FilterT = None, session: AgnosticClientSession = None, **kwargs) -> List[
        Any]:
        ...

    async def map_reduce(self, map: str, reduce: str, out: Union[str, SON], full_response=False,
                         session: AgnosticClientSession = None, **kwargs) -> Union[AgnosticCollection, Any]:
        ...

    async def inline_map_reduce(self, map: str, reduce: str, full_response=False, session: AgnosticClientSession = None,
                                **kwargs) -> Union[List[DocT], Any]:
        ...

    async def find_one_and_delete(self, filter: FilterT, projection: FilterT = None, sort: SortT = None,
                                  session: AgnosticClientSession = None, **kwargs) -> Optional[DocT]:
        ...

    async def find_one_and_replace(self, filter: FilterT, replacement: DocT,
                                   projection: FilterT = None, sort: SortT = None, upsert=False,
                                   return_document=ReturnDocument.BEFORE,
                                   session: AgnosticClientSession = None, **kwargs) -> Optional[DocT]:
        ...

    async def find_one_and_update(self, filter: FilterT, update: DocT,
                                  projection: FilterT = None, sort: SortT = None, upsert=False,
                                  return_document=ReturnDocument.BEFORE,
                                  array_filters=None, session: AgnosticClientSession = None, **kwargs) -> Optional[
        DocT]:
        ...

    def __iter__(self):
        return self

    def __next__(self):
        raise TypeError("'Collection' object is not iterable")

    next = __next__

    def __call__(self, *args, **kwargs):
        ...
