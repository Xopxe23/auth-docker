import datetime
import secrets

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
            role: str = payload.get("role")
            expired: datetime.datetime = payload.get("exp")
            if email is None:
                return None
        except JWTError:
            return None
        return {
            "sub": email,
            "exp": expired,
            "role": role
        }
