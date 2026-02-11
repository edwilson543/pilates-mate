import fastapi

from . import routers


app = fastapi.FastAPI()

app.include_router(routers.exercise_router, prefix="/exercises", tags=["exercises"])
app.include_router(
    routers.lesson_plan_router, prefix="/lesson-plans", tags=["lesson-plans"]
)
