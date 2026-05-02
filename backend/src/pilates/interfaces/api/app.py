import contextlib
import typing

import fastapi
from fastapi import responses as fastapi_responses
from fastapi.middleware.cors import CORSMiddleware

from pilates import config, version
from pilates.interfaces.api import routers


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI) -> typing.AsyncIterator[None]:
    settings = config.Settings()
    app.state.settings = settings
    yield


app = fastapi.FastAPI(lifespan=lifespan)

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    routers.auth_router,
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    routers.exercises_router,
    prefix="/exercises",
    tags=["exercises"],
)
app.include_router(
    routers.lesson_plans_router,
    prefix="/lesson-plans",
    tags=["lesson-plans"],
)


@app.get("/health")
def health_check() -> fastapi_responses.JSONResponse:
    return fastapi_responses.JSONResponse(
        status_code=200, content={"version": version.__version__}
    )
