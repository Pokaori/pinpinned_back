import os

import databases
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy.ext.asyncio import create_async_engine

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_URL')}/pinpinned"
DATABASE_SYNC_URL = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_URL')}/pinpinned"
database = databases.Database(DATABASE_URL)
engine = create_async_engine(DATABASE_URL)
engine_sync = create_engine(DATABASE_SYNC_URL, execution_options={"asyncpg_execute_kw": {"timeout": 60000}})
metadata = sqlalchemy.MetaData(bind=engine)

async_session = sessionmaker(engine, class_=AsyncSession)
session = sessionmaker(engine_sync)

Base = declarative_base(metadata=metadata)


async def get_async_session():
    async with async_session() as db_session:
        # async with db_session.begin():
        try:
            yield db_session
        except Exception as e:
            await db_session.rollback()
            raise e

def get_session():
    with session() as db_session:
        with db_session.begin():
            return db_session
