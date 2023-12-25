import datetime
import uuid
import enum

from sqlalchemy import Boolean, ForeignKey, String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, uuid_pk


class UserRole(enum.Enum):
    base_user = "base_user"
    rentier = "rentier"
    moderator = "moderator"


class User(Base):
    __tablename__ = "auth_user"

    id: Mapped[uuid_pk]
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    role: Mapped[UserRole]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth_user.id", ondelete="cascade"))
    token: Mapped[str]
    expires_at: Mapped[datetime.datetime]
