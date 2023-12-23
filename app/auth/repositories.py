import datetime
from uuid import UUID

from fastapi import Depends
from sqlalchemy import Select, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken, User
from app.database import get_async_session


class UserRepository:
    user_table = User
    refresh_token_table = RefreshToken

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> User | None:
        statement = select(self.user_table).where(self.user_table.id == id)
        return await self._get_user(statement)

    async def get_all(self) -> list[User]:
        statement = select(self.user_table)
        result = await self.session.execute(statement)
        return result.scalars()

    async def get_by_email(self, email: str) -> User | None:
        statement = select(self.user_table).where(
            func.lower(self.user_table.email) == func.lower(email)
        )
        return await self._get_user(statement)

    async def create(self, create_dict: dict) -> User:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def add_refresh_token(self, user_id: int, token: str) -> None:
        refresh_token = self.refresh_token_table()
        refresh_token.token = token
        refresh_token.user_id = user_id
        refresh_token.expires_at = datetime.datetime.now() + datetime.timedelta(days=7)
        self.session.add(refresh_token)
        await self.session.commit()

    async def get_refresh_token(self, refresh_token: str) -> RefreshToken | None:
        statement = select(self.refresh_token_table).where(
            self.refresh_token_table.token == refresh_token
        )
        result = await self.session.execute(statement)
        statement = delete(self.refresh_token_table).where(self.refresh_token_table.token == refresh_token)
        await self.session.execute(statement)
        return result.unique().scalar_one_or_none()

    async def _get_user(self, statement: Select) -> User | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()


async def get_user_repository(session: AsyncSession = Depends(get_async_session)):
    yield UserRepository(session)
