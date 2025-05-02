from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import get_setting, Setting


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, setting: Setting):
        self.engine = create_async_engine(
            url=setting.DB_POSTGRES_URL, echo=True, pool_size=5, max_overflow=10
        )
        self.session = async_sessionmaker(self.engine)
    
    def get_session(self):
        async def _session():
            async with self.session() as session:
                yield session
        return _session


setting = get_setting()
db = Database(setting)
get_session = db.get_session()