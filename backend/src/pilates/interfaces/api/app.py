import fastapi
from fastapi.middleware.cors import CORSMiddleware

from pilates.interfaces.api import routers


app = fastapi.FastAPI()

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.exercises_router, prefix="/exercises", tags=["exercises"])
app.include_router(
    routers.lesson_planning_router, prefix="/lesson-plans", tags=["lesson-plans"]
)
