import re
import uuid
from typing import Optional

from fastapi import HTTPException, Header
from starlette.requests import Request

from routers.authserver.models import User, UserRoles
from routers.blogs.models import Blog


async def has_access(request: Request, blog_id: Optional[uuid.UUID], raise_exception: bool = True) -> bool:
    user = await is_auth(request.headers.get("authorization"))
    is_admin = await UserRoles.objects().filter(UserRoles.role_id == user.id).exists()
    is_owner = await Blog.objects().filter(Blog.owner_id == user.id, Blog.id == blog_id).exists()

    if is_owner or is_admin:
        return user

    if raise_exception:
        raise HTTPException(status_code=400, detail="You do not have permission to interact with this blog, or the blog does not exists")

    return False


async def is_auth(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Place token to header")

    regex = r"^token ([\d\w]{8}-[\d\w]{4}-[\d\w]{4}-[\d\w]{4}-[\d\w]{12})$"  # check access_token on uuid verified
    token = re.match(regex, authorization.lower(), re.IGNORECASE)

    if token is None:
        raise HTTPException(status_code=401, detail="Invalidate access_token")

    account = await User.objects().filter(User.token == token.group(1)).first()

    if account is None:
        raise HTTPException(status_code=401, detail="Invalidate access_token")

    return account
