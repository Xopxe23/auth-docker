import datetime
from uuid import UUID

from fastapi import Depends, Response
from jose import jwt

from app.auth.models import RefreshToken, User
from app.auth.repositories import UserRepository, get_user_repository
from app.auth.utils import CookieTransport, Hasher
from app.config import settings


class UserService:
    hasher = Hasher
    cookie_transport = CookieTransport
    token_lifetime = datetime.timedelta(minutes=1)

    def __init__(self, user_db: UserRepository):
        self.user_db = user_db

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.user_db.get_by_id(user_id)

    async def get_by_email(self, user_email: str) -> User | None:
        return await self.user_db.get_by_email(user_email)

    def verify(self, user: User, password: str) -> bool:
        return self.hasher.verify_password(password, user.hashed_password)

    def parse_token(self, token: str) -> dict | None:
        return self.hasher.parse_token(token)

    async def create(self, user_data: dict) -> User:
        password = user_data.pop("password")
        user_data["email"] = user_data["email"].lower()
        user_data["hashed_password"] = self.hasher.get_password_hash(password)
        created_user = await self.user_db.create(user_data)
        return created_user

    def create_access_token(self, user_email: str) -> str | None:
        data = {"sub": user_email}
        to_encode = data.copy()
        expire = datetime.datetime.now(datetime.UTC) + self.token_lifetime
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def set_login_cookie(self, response: Response, access_token, refresh_token: str) -> None:
        response.set_cookie(
            "ACCESS_TOKEN", access_token,
            httponly=True,
            expires=datetime.datetime.now(datetime.UTC) + self.token_lifetime,  # + datetime.timedelta(hours=3)
        )
        response.set_cookie(
            "REFRESH_TOKEN", refresh_token,
            httponly=True,
            expires=datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
        )

    @staticmethod
    def set_logout_cookie(response: Response) -> None:
        response.set_cookie("ACCESS_TOKEN", "")
        response.set_cookie("REFRESH_TOKEN", "")

    async def get_refresh_token(self, refresh_token: str) -> RefreshToken | None:
        return await self.user_db.get_refresh_token(refresh_token)

    async def generate_tokens(self, user: User) -> dict[str, str]:
        access_token = self.create_access_token(user.email)
        refresh_token = self.hasher.generate_unique_string()
        await self.user_db.add_refresh_token(user.id, refresh_token)
        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        return tokens

    async def get_all_users(self) -> list[User]:
        return await self.user_db.get_all()


async def get_user_service(user_db: UserRepository = Depends(get_user_repository)):
    yield UserService(user_db)
