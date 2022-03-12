from starlette.requests import Request


class Middleware:
    async def __call__(self, request: Request, call_next):
        request.scope["middleware"] = {}
        token = request.headers.get("authorization")
        if token is None:
            request.scope["middleware"]['userdata'] = False
            return await call_next(request)
        request.scope["middleware"]['userdata'] = False
        return await call_next(request)