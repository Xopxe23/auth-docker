from pydantic import BaseModel, EmailStr, field_validator


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


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str
