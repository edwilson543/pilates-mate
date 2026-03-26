import pydantic

from pilates.domain import exercises, templates, vendors

from . import _models, _repository


class UnableToGenerateLessonPlan(Exception):
    pass


class LessonPlanRequirements(pydantic.BaseModel):
    duration_minutes: int
    target_difficulty: exercises.Difficulty
    target_muscle_groups: list[exercises.MuscleGroup]
    example_lesson_plan_ids: list[int] = []
    available_equipment: list[exercises.Equipment]
    user_prompt: str


class GeneratedExercise(pydantic.BaseModel):
    id: int
    # Name is just included since LLMs are autoregressive.
    name: str


class GeneratedExerciseSet(pydantic.BaseModel):
    exercise: GeneratedExercise
    reps: int
    duration_seconds: int
    movement_variant: exercises.MovementVariant
    equipment_variant: list[exercises.Equipment]


class GeneratedExerciseSequence(pydantic.BaseModel):
    name: str
    sets: list[GeneratedExerciseSet]
    reps: int
    notes: str


class GeneratedLessonPlan(pydantic.BaseModel):
    name: str
    description: str
    warm_up: list[GeneratedExerciseSequence]
    main_session: list[GeneratedExerciseSequence]
    cool_down: list[GeneratedExerciseSequence]

    @property
    def warm_up_duration_seconds(self) -> float:
        return sum(
            set.duration_seconds * sequence.reps
            for sequence in self.warm_up
            for set in sequence.sets
        )

    @property
    def main_session_duration_seconds(self) -> float:
        return sum(
            set.duration_seconds * sequence.reps
            for sequence in self.main_session
            for set in sequence.sets
        )

    @property
    def cool_down_duration_seconds(self) -> float:
        return sum(
            set.duration_seconds * sequence.reps
            for sequence in self.cool_down
            for set in sequence.sets
        )

    @property
    def duration_seconds(self) -> float:
        return sum(
            set.duration_seconds * sequence.reps
            for sequence in self.sequences
            for set in sequence.sets
        )

    @property
    def duration_minutes(self) -> float:
        return self.duration_seconds / 60

    @property
    def total_reps(self) -> int:
        return sum(
            set.reps * sequence.reps
            for sequence in self.sequences
            for set in sequence.sets
        )

    @property
    def exercises(self) -> list[GeneratedExercise]:
        return [set.exercise for set in self.sets]

    @property
    def sets(self) -> list[GeneratedExerciseSet]:
        return [set for sequence in self.sequences for set in sequence.sets]

    @property
    def sequences(self) -> list[GeneratedExerciseSequence]:
        return self.warm_up + self.main_session + self.cool_down


async def generate_lesson_plan(
    *,
    requirements: LessonPlanRequirements,
    client: vendors.CompletionClient,
    system_prompt: str,
) -> GeneratedLessonPlan:
    try:
        return await client.get_completion(
            system_prompt=system_prompt,
            user_prompt=requirements.user_prompt,
            output_format=GeneratedLessonPlan,
        )
    except vendors.UnableToGetCompletion as exc:
        raise UnableToGenerateLessonPlan from exc


def get_system_prompt(
    requirements: LessonPlanRequirements,
    lesson_plans_repo: _repository.Repository,
    exercises_repo: exercises.Repository,
    version: str = "v1",
) -> str:
    all_exercises = exercises_repo.get_exercises()
    example_lesson_plans = _get_example_lesson_plans(requirements, lesson_plans_repo)

    return _render_system_prompt(
        duration_minutes=requirements.duration_minutes,
        target_difficulty=requirements.target_difficulty,
        target_muscle_groups=requirements.target_muscle_groups,
        available_equipment=requirements.available_equipment,
        all_exercises=all_exercises,
        example_lesson_plans=example_lesson_plans,
        version=version,
    )


def _get_example_lesson_plans(
    requirements: LessonPlanRequirements,
    lesson_plans_repo: _repository.Repository,
) -> list[_models.LessonPlan]:
    all_lesson_plans = lesson_plans_repo.get_lesson_plans()
    if requirements.example_lesson_plan_ids:
        example_lesson_plans = [
            lesson_plan
            for lesson_plan in all_lesson_plans
            if lesson_plan in requirements.example_lesson_plan_ids
        ]
    else:
        # Fallback to using the three most recent plans.
        example_lesson_plans = sorted(all_lesson_plans, key=lambda lp: lp.date)[-3:]

    return example_lesson_plans


def _render_system_prompt(
    *,
    duration_minutes: int,
    target_difficulty: exercises.Difficulty,
    target_muscle_groups: list[exercises.MuscleGroup],
    available_equipment: list[exercises.Equipment],
    all_exercises: list[exercises.Exercise],
    example_lesson_plans: list[_models.LessonPlan],
    version: str = "v1",
) -> str:
    prompt_variables = {
        "duration_minutes": duration_minutes,
        "target_difficulty": target_difficulty,
        "target_muscle_groups": target_muscle_groups,
        "available_equipment": available_equipment,
        "exercises": {exercise.id: exercise for exercise in all_exercises},
        "example_lesson_plans": example_lesson_plans,
    }

    return templates.render(
        directory=f"lesson-planning/{version}",
        filename="system.jinja",
        variables=prompt_variables,
    )
