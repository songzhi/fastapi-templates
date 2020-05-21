import asyncio

from bson import CodecOptions

from motor.core import AgnosticCollection, AgnosticClient
from motor.motor_asyncio import AsyncIOMotorClient
from .config import DATABASE_URL

options = CodecOptions(tz_aware=True)
client: AgnosticClient = AsyncIOMotorClient(DATABASE_URL)

db = client.get_database('madforms', codec_options=options)


def get_collection(collection: str, db=db) -> AgnosticCollection:
    return db[collection]


async def create_indexes(db_name='bubble'):
    db = client[db_name]

    tasks = [
    ]
    if tasks:
        await asyncio.gather(*tasks)
    print('Indexes created.')
