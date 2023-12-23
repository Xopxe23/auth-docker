import datetime
import secrets

from fastapi import Response, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


class Hasher:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_password, hashed_password: str):
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def generate_unique_string(cls, byte: int = 64) -> str:
        return secrets.token_urlsafe(byte)

    @classmethod
    def parse_token(cls, token: str) -> dict | None:
        try:
            payload = jwt.decode(token, settings.SECRET, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            expired: datetime.datetime = payload.get("exp")
            if email is None:
                return None
        except JWTError:
            return None
        return {
            "email": email,
            "exp": expired
        }


class CookieTransport:

    @classmethod
    def get_login_response(cls, token: str) -> Response:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        return cls._set_login_cookie(response, token)

    @classmethod
    def get_logout_response(cls) -> Response:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        return cls._set_logout_cookie(response)

    @classmethod
    def _set_login_cookie(cls, response: Response, token: str) -> Response:
        response.set_cookie("ACCESS_TOKEN", token)
        return response

    @classmethod
    def _set_logout_cookie(cls, response: Response) -> Response:
        response.set_cookie(
            key="ACCESS_TOKEN",
            value="",
        )
        return response
