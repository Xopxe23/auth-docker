import datetime

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import APIKeyCookie

from app.auth.exceptions import EmailTaken, IncorrectPassword, InvalidToken, PhoneNumberTaken, UserNotExists
from app.auth.responses import StatusResponse, UserResponse
from app.auth.schemas import UserCreateSchema, UserLoginSchema
from app.auth.services import UserService, get_user_service

auth_router = APIRouter(
    prefix="/auth",
    tags=["Users & Authentication"],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request",
            "content": {"application/json": {"example": {"detail": "bad request"}}}
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication Error",
            "content": {"application/json": {"example": {"detail": "unauthorized"}}}
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
            "content": {"application/json": {"example": {"detail": "not found"}}}
        },
    }
)

oauth2_scheme = APIKeyCookie(name="ACCESS_TOKEN", auto_error=False)


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
        user_data: UserCreateSchema,
        user_service: UserService = Depends(get_user_service)
) -> StatusResponse:
    existing_user = await user_service.get_by_email(user_data.email)
    if existing_user:
        raise EmailTaken
    existing_user = await user_service.get_by_phone_number(user_data.phone_number)
    if existing_user:
        raise PhoneNumberTaken
    user_data = user_data.model_dump()
    await user_service.create(user_data)
    return StatusResponse


@auth_router.post("/login")
async def login(
        response: Response,
        user_data: UserLoginSchema,
        user_service: UserService = Depends(get_user_service)
) -> StatusResponse:
    existing_user = await user_service.get_by_email(user_data.email)
    if not existing_user:
        raise UserNotExists
    verified = user_service.verify(existing_user, user_data.password)
    if not verified:
        raise IncorrectPassword
    tokens = await user_service.generate_tokens(existing_user)
    user_service.set_login_cookie(response, **tokens)
    return StatusResponse


@auth_router.post("/logout")
async def logout(
        response: Response,
        user_service: UserService = Depends(get_user_service)
) -> StatusResponse:
    user_service.set_logout_cookie(response)
    return StatusResponse


@auth_router.post("/refresh")
async def refresh_tokens(
        request: Request,
        response: Response,
        user_service: UserService = Depends(get_user_service)
) -> StatusResponse:
    refresh_token = request.cookies.get("REFRESH_TOKEN")
    if not refresh_token:
        raise InvalidToken
    refresh_token_data = await user_service.get_refresh_token(refresh_token)
    if not refresh_token_data:
        raise InvalidToken
    if refresh_token_data.expires_at < datetime.datetime.now():
        raise InvalidToken
    user = await user_service.get_by_id(refresh_token_data.user_id)
    new_tokens = await user_service.generate_tokens(user)
    user_service.set_login_cookie(response, **new_tokens)
    return StatusResponse


@auth_router.get("/me")
async def get_me(
        user_service: UserService = Depends(get_user_service),
        token: str | None = Depends(oauth2_scheme)
) -> UserResponse:
    if token is None:
        raise InvalidToken
    token_data = user_service.parse_token(token)
    email = token_data.get("sub")
    if email is None:
        raise InvalidToken
    user = await user_service.get_by_email(email)
    if user is None:
        raise InvalidToken
    return user
