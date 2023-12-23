from uuid import UUID

from pydantic import BaseModel, EmailStr


class StatusResponse(BaseModel):
    status: str = "success"


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class ConfigDict:
        from_attributes = True
