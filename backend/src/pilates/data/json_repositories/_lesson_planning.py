import datetime as dt
import json
import pathlib

import attrs

from pilates.domain import lesson_planning


@attrs.frozen
class JSONRepository(lesson_planning.Repository):
    database_file: pathlib.Path = pathlib.Path(__file__).parent / "database.json"

    def create_exercise(
        self,
        *,
        name: str,
        description: str,
        category: lesson_planning.ExerciseCategory,
        difficulty: lesson_planning.Difficulty,
        primary_muscle_group: lesson_planning.MuscleGroup,
        starting_position: lesson_planning.StartingPosition,
        movement_variants: list[lesson_planning.MovementVariant],
        equipment_variants: list[lesson_planning.Equipment],
    ) -> int:
        data = self._read_database()

        next_id = max((exercise["id"] for exercise in data["exercises"]), default=0) + 1
        new_exercise = lesson_planning.Exercise(
            id=next_id,
            name=name,
            description=description,
            category=category,
            difficulty=difficulty,
            primary_muscle_group=primary_muscle_group,
            starting_position=starting_position,
            movement_variants=movement_variants,
            equipment_variants=equipment_variants,
        )
        data["exercises"].append(new_exercise.model_dump())

        self._write_database(data)
        return next_id

    def get_exercises(self) -> list[lesson_planning.Exercise]:
        data = self._read_database()
        return [
            lesson_planning.Exercise.model_validate(exercise)
            for exercise in data["exercises"]
        ]

    def get_exercise(self, exercise_id: int) -> lesson_planning.Exercise:
        for exercise in self.get_exercises():
            if exercise.id == exercise_id:
                return exercise
        raise lesson_planning.ExerciseDoesNotExist(exercise_id=exercise_id)

    def update_exercise(
        self,
        *,
        id: int,
        name: str,
        description: str,
        category: lesson_planning.ExerciseCategory,
        difficulty: lesson_planning.Difficulty,
        primary_muscle_group: lesson_planning.MuscleGroup,
        starting_position: lesson_planning.StartingPosition,
        movement_variants: list[lesson_planning.MovementVariant],
        equipment_variants: list[lesson_planning.Equipment],
    ) -> None:
        data = self._read_database()

        # Find exercise index
        exercise_index = None
        for idx, exercise in enumerate(data["exercises"]):
            if exercise["id"] == id:
                exercise_index = idx
                break

        if exercise_index is None:
            raise lesson_planning.ExerciseDoesNotExist(exercise_id=id)

        # Create updated exercise
        updated_exercise = lesson_planning.Exercise(
            id=id,
            name=name,
            category=category,
            description=description,
            difficulty=difficulty,
            primary_muscle_group=primary_muscle_group,
            starting_position=starting_position,
            movement_variants=movement_variants,
            equipment_variants=equipment_variants,
        )

        # Update in exercises array
        data["exercises"][exercise_index] = updated_exercise.model_dump()

        # Update all references in lesson plans (denormalization handling)
        for plan in data["lesson_plans"]:
            for section in ["warm_up", "main_session", "cool_down"]:
                for sequence in plan[section]:
                    for set_item in sequence["sets"]:
                        if set_item["exercise"]["id"] == id:
                            set_item["exercise"] = updated_exercise.model_dump()

        self._write_database(data)

    def create_lesson_plan(
        self,
        *,
        name: str,
        description: str,
        date: dt.date,
        warm_up: list[lesson_planning.ExerciseSequence],
        main_session: list[lesson_planning.ExerciseSequence],
        cool_down: list[lesson_planning.ExerciseSequence],
    ) -> int:
        data = self._read_database()

        next_id = max((plan["id"] for plan in data["lesson_plans"]), default=0) + 1

        new_lesson_plan = lesson_planning.LessonPlan(
            id=next_id,
            name=name,
            description=description,
            date=date,
            warm_up=warm_up,
            main_session=main_session,
            cool_down=cool_down,
        )
        data["lesson_plans"].append(new_lesson_plan.model_dump(mode="json"))

        self._write_database(data)

        return next_id

    def get_lesson_plans(self) -> list[lesson_planning.LessonPlan]:
        data = self._read_database()
        return [
            lesson_planning.LessonPlan.model_validate(plan)
            for plan in data["lesson_plans"]
        ]

    def get_lesson_plan(self, lesson_plan_id: int) -> lesson_planning.LessonPlan:
        for plan in self.get_lesson_plans():
            if plan.id == lesson_plan_id:
                return plan
        raise lesson_planning.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)

    def delete_lesson_plan(self, lesson_plan_id: int) -> None:
        data = self._read_database()

        # Verify plan exists
        plan_exists = any(plan["id"] == lesson_plan_id for plan in data["lesson_plans"])
        if not plan_exists:
            raise lesson_planning.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)

        # Filter out the plan
        data["lesson_plans"] = [
            plan for plan in data["lesson_plans"] if plan["id"] != lesson_plan_id
        ]

        self._write_database(data)

    def add_sequence_to_section(
        self,
        *,
        lesson_plan_id: int,
        section: lesson_planning.LessonPlanSection,
        name: str,
        reps: int,
        notes: str,
    ) -> int:
        data = self._read_database()

        # Verify lesson plan exists
        plan_index = None
        for idx, plan in enumerate(data["lesson_plans"]):
            if plan["id"] == lesson_plan_id:
                plan_index = idx
                break

        if plan_index is None:
            raise lesson_planning.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)

        # Generate sequence ID
        next_id = (
            max(
                (
                    seq["id"]
                    for plan in data["lesson_plans"]
                    for section_name in ["warm_up", "main_session", "cool_down"]
                    for seq in plan[section_name]
                ),
                default=0,
            )
            + 1
        )

        # Create new sequence with empty sets
        new_sequence = lesson_planning.ExerciseSequence(
            id=next_id,
            name=name,
            sets=[],
            reps=reps,
            notes=notes,
        )

        # Get field name for section
        field_name = _section_to_field_name(section)

        # Append to appropriate section
        data["lesson_plans"][plan_index][field_name].append(
            new_sequence.model_dump(mode="json")
        )

        self._write_database(data)

        return next_id

    def add_set_to_sequence(
        self,
        *,
        sequence_id: int,
        exercise_id: int,
        reps: int,
        duration_seconds: int,
        movement_variant: lesson_planning.MovementVariant,
        equipment_variant: list[lesson_planning.Equipment],
    ) -> int:
        data = self._read_database()

        # Look up exercise
        exercise = self.get_exercise(exercise_id)

        # Find sequence across all lesson plans
        plan_index = None
        section_name = None
        sequence_index = None

        for p_idx, plan in enumerate(data["lesson_plans"]):
            for s_name in ["warm_up", "main_session", "cool_down"]:
                for seq_idx, sequence in enumerate(plan[s_name]):
                    if sequence["id"] == sequence_id:
                        plan_index = p_idx
                        section_name = s_name
                        sequence_index = seq_idx
                        break
                if sequence_index is not None:
                    break
            if sequence_index is not None:
                break

        if sequence_index is None:
            raise lesson_planning.SequenceDoesNotExist(sequence_id=sequence_id)

        # Generate set ID
        next_id = (
            max(
                (
                    set_item["id"]
                    for plan in data["lesson_plans"]
                    for section_name in ["warm_up", "main_session", "cool_down"]
                    for seq in plan[section_name]
                    for set_item in seq["sets"]
                ),
                default=0,
            )
            + 1
        )

        # Create new set with denormalized exercise data
        new_set = lesson_planning.ExerciseSet(
            id=next_id,
            exercise=exercise,
            reps=reps,
            duration_seconds=duration_seconds,
            movement_variant=movement_variant,
            equipment_variant=equipment_variant,
        )

        # Append set to sequence
        data["lesson_plans"][plan_index][section_name][sequence_index]["sets"].append(
            new_set.model_dump(mode="json")
        )

        self._write_database(data)

        return next_id

    def get_exercise_set(self, set_id: int) -> lesson_planning.ExerciseSet:
        data = self._read_database()
        for plan in data["lesson_plans"]:
            for section_name in ["warm_up", "main_session", "cool_down"]:
                for sequence in plan[section_name]:
                    for set_item in sequence["sets"]:
                        if set_item["id"] == set_id:
                            return lesson_planning.ExerciseSet.model_validate(set_item)
        raise lesson_planning.SetDoesNotExist(set_id=set_id)

    def update_exercise_set(
        self,
        *,
        id: int,
        reps: int,
        duration_seconds: int,
        movement_variant: lesson_planning.MovementVariant,
        equipment_variant: list[lesson_planning.Equipment],
    ) -> None:
        data = self._read_database()

        # Find and update set dict in place
        set_found = False
        for plan in data["lesson_plans"]:
            for section_name in ["warm_up", "main_session", "cool_down"]:
                for sequence in plan[section_name]:
                    for set_item in sequence["sets"]:
                        if set_item["id"] == id:
                            set_item["reps"] = reps
                            set_item["duration_seconds"] = duration_seconds
                            set_item["movement_variant"] = movement_variant.value
                            set_item["equipment_variant"] = [eq.value for eq in equipment_variant]
                            set_found = True
                            break
                    if set_found:
                        break
                if set_found:
                    break
            if set_found:
                break

        if not set_found:
            raise lesson_planning.SetDoesNotExist(set_id=id)

        self._write_database(data)

    def delete_exercise_set(self, set_id: int) -> None:
        data = self._read_database()

        # Find sequence containing set and filter it out
        set_found = False
        for plan in data["lesson_plans"]:
            for section_name in ["warm_up", "main_session", "cool_down"]:
                for sequence in plan[section_name]:
                    original_length = len(sequence["sets"])
                    sequence["sets"] = [
                        s for s in sequence["sets"] if s["id"] != set_id
                    ]
                    if len(sequence["sets"]) < original_length:
                        set_found = True
                        break
                if set_found:
                    break
            if set_found:
                break

        if not set_found:
            raise lesson_planning.SetDoesNotExist(set_id=set_id)

        self._write_database(data)

    # Helpers.

    def _read_database(self) -> dict:
        self._maybe_init_database()
        with open(self.database_file, "r") as f:
            return json.load(f)

    def _write_database(self, data: dict) -> None:
        with open(self.database_file, "w") as f:
            json.dump(data, f, indent=2)

    def _maybe_init_database(self) -> None:
        if self.database_file.is_file():
            return None

        data: dict[str, list] = {
            "lesson_plans": [],
            "exercises": [],
        }

        with open(self.database_file, "x") as f:
            json.dump(data, f)


def _section_to_field_name(section: lesson_planning.LessonPlanSection) -> str:
    """Convert LessonPlanSection enum to field name."""
    mapping = {
        lesson_planning.LessonPlanSection.WARM_UP: "warm_up",
        lesson_planning.LessonPlanSection.MAIN_SESSION: "main_session",
        lesson_planning.LessonPlanSection.COOL_DOWN: "cool_down",
    }
    return mapping[section]
