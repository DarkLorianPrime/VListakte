from fastapi import FastAPI
from starlette.requests import Request

app = FastAPI()


class Middleware:
    async def __call__(self, request: Request, call_next):
        request.scope["middleware"] = {}
        token = request.headers.get("authorization")
        if token is None:
            request.scope["middleware"]['userdata'] = False
            return await call_next(request)
        request.scope["middlewaredata"]['userdata'] = False
        return await call_next(request)


@app.get("/")
async def root(request: Request):
    print(request.__dict__.get("scope"))
    return {"loading": 'loaded'}


app.middleware("http")(Middleware())
