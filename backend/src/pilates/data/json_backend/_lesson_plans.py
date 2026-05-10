import datetime as dt
import pathlib
import typing

import attrs

from pilates.domain import exercises, lesson_plans

from . import _mixins


@attrs.frozen
class JSONRepository(lesson_plans.Repository, _mixins.JSONRepositoryMixin):
    database_file: pathlib.Path

    def create_lesson_plan(
        self,
        *,
        name: str,
        date: dt.date,
        requirements: lesson_plans.LessonPlanRequirements,
    ) -> int:
        data = self._read_database()

        next_id = max((plan["id"] for plan in data["lesson_plans"]), default=0) + 1

        new_lesson_plan = lesson_plans.LessonPlan(
            id=next_id,
            name=name,
            description="",
            date=date,
            requirements=requirements,
            status=lesson_plans.LessonPlanStatus.PENDING_GENERATION,
            warm_up=[],
            main_session=[],
            cool_down=[],
        )
        data["lesson_plans"].append(new_lesson_plan.model_dump(mode="json"))

        self._write_database(data)

        return next_id

    def update_lesson_plan(
        self,
        lesson_plan_id: int,
        *,
        name: str,
        description: str,
        status: lesson_plans.LessonPlanStatus,
    ) -> None:
        data = self._read_database()

        for plan in data["lesson_plans"]:
            if plan["id"] == lesson_plan_id:
                plan["name"] = name
                plan["description"] = description
                plan["status"] = status.value
                self._write_database(data)
                return

        raise lesson_plans.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)

    def get_lesson_plans(self) -> list[lesson_plans.LessonPlan]:
        data = self._read_database()
        return [
            lesson_plans.LessonPlan.model_validate(plan)
            for plan in data["lesson_plans"]
        ]

    def get_lesson_plan(self, lesson_plan_id: int) -> lesson_plans.LessonPlan:
        for plan in self.get_lesson_plans():
            if plan.id == lesson_plan_id:
                return plan
        raise lesson_plans.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)

    def delete_lesson_plan(self, lesson_plan_id: int) -> None:
        data = self._read_database()

        # Verify plan exists
        plan_exists = any(plan["id"] == lesson_plan_id for plan in data["lesson_plans"])
        if not plan_exists:
            raise lesson_plans.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)

        # Filter out the plan
        data["lesson_plans"] = [
            plan for plan in data["lesson_plans"] if plan["id"] != lesson_plan_id
        ]

        self._write_database(data)

    def add_sequence_to_section(
        self,
        *,
        lesson_plan_id: int,
        section: lesson_plans.LessonPlanSection,
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
            raise lesson_plans.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)

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
        new_sequence = lesson_plans.ExerciseSequence(
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
        movement_variant: exercises.MovementVariant,
        equipment_variant: list[exercises.Equipment],
    ) -> int:
        data = self._read_database()
        _validate_exercise_id(data, exercise_id)

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
            raise lesson_plans.SequenceDoesNotExist(sequence_id=sequence_id)

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
        new_set = lesson_plans.ExerciseSet(
            id=next_id,
            # In the db repository, the foreign key will ensure data integrity...
            exercise_id=exercise_id,
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

    def get_exercise_set(self, set_id: int) -> lesson_plans.ExerciseSet:
        data = self._read_database()
        for plan in data["lesson_plans"]:
            for section_name in ["warm_up", "main_session", "cool_down"]:
                for sequence in plan[section_name]:
                    for set_item in sequence["sets"]:
                        if set_item["id"] == set_id:
                            return lesson_plans.ExerciseSet.model_validate(set_item)
        raise lesson_plans.SetDoesNotExist(set_id=set_id)

    def update_exercise_set(
        self,
        *,
        id: int,
        reps: int,
        duration_seconds: int,
        movement_variant: exercises.MovementVariant,
        equipment_variant: list[exercises.Equipment],
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
                            set_item["equipment_variant"] = [
                                eq.value for eq in equipment_variant
                            ]
                            set_found = True
                            break
                    if set_found:
                        break
                if set_found:
                    break
            if set_found:
                break

        if not set_found:
            raise lesson_plans.SetDoesNotExist(set_id=id)

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
            raise lesson_plans.SetDoesNotExist(set_id=set_id)

        self._write_database(data)

    def update_exercise_sequence(
        self,
        *,
        id: int,
        name: str,
        reps: int,
        notes: str,
    ) -> None:
        data = self._read_database()

        # Find and update sequence dict in place
        sequence_found = False
        for plan in data["lesson_plans"]:
            for section_name in ["warm_up", "main_session", "cool_down"]:
                for sequence in plan[section_name]:
                    if sequence["id"] == id:
                        sequence["name"] = name
                        sequence["reps"] = reps
                        sequence["notes"] = notes
                        sequence_found = True
                        break
                if sequence_found:
                    break
            if sequence_found:
                break

        if not sequence_found:
            raise lesson_plans.SequenceDoesNotExist(sequence_id=id)

        self._write_database(data)

    def delete_exercise_sequence(self, sequence_id: int) -> None:
        data = self._read_database()

        # Find section containing sequence and filter it out
        sequence_found = False
        for plan in data["lesson_plans"]:
            for section_name in ["warm_up", "main_session", "cool_down"]:
                original_length = len(plan[section_name])
                plan[section_name] = [
                    seq for seq in plan[section_name] if seq["id"] != sequence_id
                ]
                if len(plan[section_name]) < original_length:
                    sequence_found = True
                    break
            if sequence_found:
                break

        if not sequence_found:
            raise lesson_plans.SequenceDoesNotExist(sequence_id=sequence_id)

        self._write_database(data)


def _validate_exercise_id(data: dict[str, typing.Any], exercise_id: int) -> None:
    for exercise in data["exercises"]:
        if exercise["id"] == exercise_id:
            return
    raise exercises.ExerciseDoesNotExist(exercise_id=exercise_id)


def _section_to_field_name(section: lesson_plans.LessonPlanSection) -> str:
    """Convert LessonPlanSection enum to field name."""
    mapping = {
        lesson_plans.LessonPlanSection.WARM_UP: "warm_up",
        lesson_plans.LessonPlanSection.MAIN_SESSION: "main_session",
        lesson_plans.LessonPlanSection.COOL_DOWN: "cool_down",
    }
    return mapping[section]
