from app.exceptions import BadRequest, NotAuthenticated


class ErrorCode:
    AUTHENTICATION_REQUIRED = "Authentication required"
    INVALID_TOKEN = "Invalid token"
    EMAIL_TAKEN = "Email is already taken"
    USER_NOT_EXISTS = "User not exists"
    INCORRECT_PASSWORD = "Incorrect password"


class EmailTaken(BadRequest):
    DETAIL = ErrorCode.EMAIL_TAKEN


class UserNotExists(BadRequest):
    DETAIL = ErrorCode.USER_NOT_EXISTS


class IncorrectPassword(BadRequest):
    DETAIL = ErrorCode.INCORRECT_PASSWORD


class InvalidToken(NotAuthenticated):
    DETAIL = ErrorCode.INVALID_TOKEN
