import re

from pydantic import BaseModel, EmailStr, field_validator

from app.auth.models import UserRole


class PasswordMixin(BaseModel):
    password: str

    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain at least one digit')
        if any(char.isspace() for char in value):
            raise ValueError('Password must not contain spaces')
        return value


class UserCreateSchema(PasswordMixin):
    email: EmailStr
    phone_number: str
    role: UserRole

    @field_validator('phone_number')
    def validate_phone_number(cls, phone_number):
        pattern = r'^\d{10}$'  # Паттерн: состоит из 10 цифр
        if not re.match(pattern, phone_number):
            raise ValueError('Invalid phone number')
        return phone_number


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str
