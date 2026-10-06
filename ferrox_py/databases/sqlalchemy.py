from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ferrox_py.core.provider import injectable


@injectable()
class AsyncDatabaseService:
    def __init__(self) -> None:
        # In a real app, read from config
        self.database_url = "sqlite+aiosqlite:///:memory:"
        self.engine = create_async_engine(self.database_url, echo=True)
        self.async_session_maker = sessionmaker(  # type: ignore
            self.engine,  expire_on_commit=False
        )

    async def get_session(self) -> AsyncSession:  # type: ignore
        async with self.async_session_maker() as session:
            yield session
