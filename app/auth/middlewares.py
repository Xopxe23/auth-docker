import datetime
from typing import Callable

from fastapi import Request, Response

from app.auth.repositories import UserRepository
from app.auth.services import UserService
from app.database import async_session_maker


async def refresh_tokens_middleware(
    request: Request,
    call_next: Callable[[Request], Response],
) -> Response:
    session = async_session_maker()
    user_repo = UserRepository(session)
    user_service = UserService(user_repo)
    access_token = request.cookies.get("ACCESS_TOKEN")
    if access_token is not None:
        access_token_data = user_service.parse_token(access_token)
        if access_token_data["exp"] > datetime.datetime.now().timestamp():
            return await call_next(request)

    refresh_token = request.cookies.get("REFRESH_TOKEN")
    if not refresh_token:
        return await call_next(request)

    refresh_token_data = await user_service.get_refresh_token(refresh_token)
    if not refresh_token_data:
        return await call_next(request)

    user = await user_service.get_by_id(refresh_token_data.user_id)
    if not user:
        return await call_next(request)

    new_tokens = await user_service.generate_tokens(user)
    access_token = new_tokens["access_token"]
    refresh_token = new_tokens["refresh_token"]
    request.cookies.pop("REFRESH_TOKEN")
    # request.cookies.pop("ACCESS_TOKEN")
    new_cookies = {
        "ACCESS_TOKEN": new_tokens["access_token"],
        "REFRESH_TOKEN": new_tokens["refresh_token"]
    }
    request.cookies.update(**new_cookies)
    print(request.cookies)
    response = await call_next(request)
    user_service.set_login_cookie(response, access_token, refresh_token)
    return response
