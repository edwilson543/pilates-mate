import datetime as dt

import attrs

from pilates.domain import lesson_plans


@attrs.frozen
class FakeRepository(lesson_plans.Repository):
    _exercises: list[lesson_plans.Exercise] = attrs.field(factory=list)
    _lesson_plans: list[lesson_plans.LessonPlan] = attrs.field(factory=list)

    _next_sequence_id: int = attrs.field(init=False)
    _next_set_id: int = attrs.field(init=False)

    def __attrs_post_init__(self) -> None:
        # Initialize sequence ID counter by scanning existing lesson plans
        max_sequence_id = 0
        for plan in self._lesson_plans:
            for section in [plan.warm_up, plan.main_session, plan.cool_down]:
                for sequence in section:
                    if sequence.id > max_sequence_id:
                        max_sequence_id = sequence.id
        object.__setattr__(self, "_next_sequence_id", max_sequence_id + 1)

        # Initialize set ID counter by scanning existing lesson plans
        max_set_id = 0
        for plan in self._lesson_plans:
            for section in [plan.warm_up, plan.main_session, plan.cool_down]:
                for sequence in section:
                    for exercise_set in sequence.sets:
                        if exercise_set.id > max_set_id:
                            max_set_id = exercise_set.id
        object.__setattr__(self, "_next_set_id", max_set_id + 1)

    def create_exercise(
        self,
        *,
        name: str,
        description: str,
        category: lesson_plans.ExerciseCategory,
        difficulty: lesson_plans.Difficulty,
        primary_muscle_group: lesson_plans.MuscleGroup,
        starting_position: lesson_plans.StartingPosition,
        movement_variants: list[lesson_plans.MovementVariant],
        equipment_variants: list[lesson_plans.Equipment],
    ) -> int:
        next_id = len(self._exercises) + 1

        new_exercise = lesson_plans.Exercise(
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
        self._exercises.append(new_exercise)

        return next_id

    def get_exercises(self) -> list[lesson_plans.Exercise]:
        return self._exercises.copy()

    def get_exercise(self, exercise_id: int) -> lesson_plans.Exercise:
        for exercise in self._exercises:
            if exercise.id == exercise_id:
                return exercise
        raise lesson_plans.ExerciseDoesNotExist(exercise_id=exercise_id)

    def update_exercise(
        self,
        *,
        id: int,
        name: str,
        category: lesson_plans.ExerciseCategory,
        description: str,
        difficulty: lesson_plans.Difficulty,
        primary_muscle_group: lesson_plans.MuscleGroup,
        starting_position: lesson_plans.StartingPosition,
        movement_variants: list[lesson_plans.MovementVariant],
        equipment_variants: list[lesson_plans.Equipment],
    ) -> None:
        def _update(exercise_: lesson_plans.Exercise) -> None:
            exercise_.name = name
            exercise_.description = description
            exercise_.category = category
            exercise_.difficulty = difficulty
            exercise_.primary_muscle_group = primary_muscle_group
            exercise_.starting_position = starting_position
            exercise_.movement_variants = movement_variants
            exercise_.equipment_variants = equipment_variants

        for exercise in self._exercises:
            if exercise.id == id:
                _update(exercise)
                # Since exercises are denormalized on lesson plans, we need to propagate changes.
                for lesson_plan in self._lesson_plans:
                    for lp_exercise in lesson_plan.exercises:
                        if lp_exercise.id == id:
                            _update(lp_exercise)

                return None

        raise lesson_plans.ExerciseDoesNotExist(exercise_id=id)

    def _update_sequences(
        self,
        sequences: list[lesson_plans.ExerciseSequence],
        exercise_id: int,
        updated_exercise: lesson_plans.Exercise,
    ) -> list[lesson_plans.ExerciseSequence]:
        """Update exercise references in a list of sequences."""
        updated_sequences = []
        for sequence in sequences:
            updated_sets = []
            for exercise_set in sequence.sets:
                if exercise_set.exercise.id == exercise_id:
                    updated_set = exercise_set.model_copy(
                        update={"exercise": updated_exercise}
                    )
                    updated_sets.append(updated_set)
                else:
                    updated_sets.append(exercise_set)

            updated_sequence = sequence.model_copy(update={"sets": updated_sets})
            updated_sequences.append(updated_sequence)

        return updated_sequences

    def create_lesson_plan(
        self,
        *,
        name: str,
        description: str,
        date: dt.date,
        warm_up: list[lesson_plans.ExerciseSequence],
        main_session: list[lesson_plans.ExerciseSequence],
        cool_down: list[lesson_plans.ExerciseSequence],
    ) -> int:
        next_id = len(self._lesson_plans) + 1

        new_lesson_plan = lesson_plans.LessonPlan(
            id=next_id,
            name=name,
            description=description,
            date=date,
            warm_up=warm_up,
            main_session=main_session,
            cool_down=cool_down,
        )
        self._lesson_plans.append(new_lesson_plan)

        return next_id

    def get_lesson_plans(self) -> list[lesson_plans.LessonPlan]:
        return self._lesson_plans.copy()

    def get_lesson_plan(self, lesson_plan_id: int) -> lesson_plans.LessonPlan:
        for plan in self._lesson_plans:
            if plan.id == lesson_plan_id:
                return plan
        raise lesson_plans.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)

    def delete_lesson_plan(self, lesson_plan_id: int) -> None:
        plan_exists = any(plan.id == lesson_plan_id for plan in self._lesson_plans)
        if not plan_exists:
            raise lesson_plans.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)

        filtered_plans = [
            plan for plan in self._lesson_plans if plan.id != lesson_plan_id
        ]
        object.__setattr__(self, "_lesson_plans", filtered_plans)

    def add_sequence_to_section(
        self,
        *,
        lesson_plan_id: int,
        section: lesson_plans.LessonPlanSection,
        name: str,
        reps: int,
        notes: str,
    ) -> int:
        # Find the lesson plan
        plan_index = None
        for idx, plan in enumerate(self._lesson_plans):
            if plan.id == lesson_plan_id:
                plan_index = idx
                break

        if plan_index is None:
            raise lesson_plans.LessonPlanDoesNotExist(lesson_plan_id=lesson_plan_id)

        # Generate sequence ID
        sequence_id = self._next_sequence_id
        object.__setattr__(self, "_next_sequence_id", self._next_sequence_id + 1)

        # Create new sequence with empty sets
        new_sequence = lesson_plans.ExerciseSequence(
            id=sequence_id,
            name=name,
            sets=[],
            reps=reps,
            notes=notes,
        )

        # Get field name for section
        field_name = _section_to_field_name(section)

        # Get current plan and append to appropriate section
        current_plan = self._lesson_plans[plan_index]
        current_section = getattr(current_plan, field_name)
        updated_section = current_section + [new_sequence]

        # Update plan
        updated_plan = current_plan.model_copy(update={field_name: updated_section})
        updated_plans = self._lesson_plans.copy()
        updated_plans[plan_index] = updated_plan
        object.__setattr__(self, "_lesson_plans", updated_plans)

        return sequence_id

    def add_set_to_sequence(
        self,
        *,
        sequence_id: int,
        exercise_id: int,
        reps: int,
        duration_seconds: int,
        movement_variant: lesson_plans.MovementVariant,
        equipment_variant: list[lesson_plans.Equipment],
    ) -> int:
        # Look up exercise
        exercise = self.get_exercise(exercise_id)

        # Find sequence across all lesson plans
        plan_index = None
        section_name = None
        sequence_index = None

        for p_idx, plan in enumerate(self._lesson_plans):
            for s_name in ["warm_up", "main_session", "cool_down"]:
                section = getattr(plan, s_name)
                for seq_idx, sequence in enumerate(section):
                    if sequence.id == sequence_id:
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

        # Type narrowing: if sequence_index is not None, then plan_index and section_name are also not None
        assert plan_index is not None
        assert section_name is not None

        # Generate set ID
        set_id = self._next_set_id
        object.__setattr__(self, "_next_set_id", self._next_set_id + 1)

        # Create new set with denormalized exercise data
        new_set = lesson_plans.ExerciseSet(
            id=set_id,
            exercise=exercise,
            reps=reps,
            duration_seconds=duration_seconds,
            movement_variant=movement_variant,
            equipment_variant=equipment_variant,
        )

        # Get current plan and section
        current_plan = self._lesson_plans[plan_index]
        current_section = getattr(current_plan, section_name)
        current_sequence = current_section[sequence_index]

        # Append set to sequence
        updated_sets = current_sequence.sets + [new_set]
        updated_sequence = current_sequence.model_copy(update={"sets": updated_sets})

        # Update section with updated sequence
        updated_section = current_section.copy()
        updated_section[sequence_index] = updated_sequence

        # Update plan
        updated_plan = current_plan.model_copy(update={section_name: updated_section})
        updated_plans = self._lesson_plans.copy()
        updated_plans[plan_index] = updated_plan
        object.__setattr__(self, "_lesson_plans", updated_plans)

        return set_id

    def get_exercise_set(self, set_id: int) -> lesson_plans.ExerciseSet:
        """Find set across all lesson plans."""
        for plan in self._lesson_plans:
            for section in [plan.warm_up, plan.main_session, plan.cool_down]:
                for sequence in section:
                    for exercise_set in sequence.sets:
                        if exercise_set.id == set_id:
                            return exercise_set
        raise lesson_plans.SetDoesNotExist(set_id=set_id)

    def update_exercise_set(
        self,
        *,
        id: int,
        reps: int,
        duration_seconds: int,
        movement_variant: lesson_plans.MovementVariant,
        equipment_variant: list[lesson_plans.Equipment],
    ) -> None:
        # Find set location (plan_index, section_name, sequence_index, set_index)
        plan_index = None
        section_name = None
        sequence_index = None
        set_index = None

        for p_idx, plan in enumerate(self._lesson_plans):
            for s_name in ["warm_up", "main_session", "cool_down"]:
                section = getattr(plan, s_name)
                for seq_idx, sequence in enumerate(section):
                    for set_idx, exercise_set in enumerate(sequence.sets):
                        if exercise_set.id == id:
                            plan_index = p_idx
                            section_name = s_name
                            sequence_index = seq_idx
                            set_index = set_idx
                            break
                    if set_index is not None:
                        break
                if set_index is not None:
                    break
            if set_index is not None:
                break

        if set_index is None:
            raise lesson_plans.SetDoesNotExist(set_id=id)

        # Type narrowing
        assert plan_index is not None
        assert section_name is not None
        assert sequence_index is not None

        # Get current objects
        current_plan = self._lesson_plans[plan_index]
        current_section = getattr(current_plan, section_name)
        current_sequence = current_section[sequence_index]
        current_set = current_sequence.sets[set_index]

        # Create updated set using model_copy
        updated_set = current_set.model_copy(
            update={
                "reps": reps,
                "duration_seconds": duration_seconds,
                "movement_variant": movement_variant,
                "equipment_variant": equipment_variant,
            }
        )

        # Update sequence with new sets list
        updated_sets = current_sequence.sets.copy()
        updated_sets[set_index] = updated_set
        updated_sequence = current_sequence.model_copy(update={"sets": updated_sets})

        # Update section with new sequence
        updated_section = current_section.copy()
        updated_section[sequence_index] = updated_sequence

        # Update plan with new section
        updated_plan = current_plan.model_copy(update={section_name: updated_section})

        # Update repository with new plan list
        updated_plans = self._lesson_plans.copy()
        updated_plans[plan_index] = updated_plan
        object.__setattr__(self, "_lesson_plans", updated_plans)

    def delete_exercise_set(self, set_id: int) -> None:
        # Find set location
        plan_index = None
        section_name = None
        sequence_index = None
        set_index = None

        for p_idx, plan in enumerate(self._lesson_plans):
            for s_name in ["warm_up", "main_session", "cool_down"]:
                section = getattr(plan, s_name)
                for seq_idx, sequence in enumerate(section):
                    for set_idx, exercise_set in enumerate(sequence.sets):
                        if exercise_set.id == set_id:
                            plan_index = p_idx
                            section_name = s_name
                            sequence_index = seq_idx
                            set_index = set_idx
                            break
                    if set_index is not None:
                        break
                if set_index is not None:
                    break
            if set_index is not None:
                break

        if set_index is None:
            raise lesson_plans.SetDoesNotExist(set_id=set_id)

        # Type narrowing
        assert plan_index is not None
        assert section_name is not None
        assert sequence_index is not None

        # Get current objects
        current_plan = self._lesson_plans[plan_index]
        current_section = getattr(current_plan, section_name)
        current_sequence = current_section[sequence_index]

        # Filter out the set
        updated_sets = [s for s in current_sequence.sets if s.id != set_id]
        updated_sequence = current_sequence.model_copy(update={"sets": updated_sets})

        # Update section with new sequence
        updated_section = current_section.copy()
        updated_section[sequence_index] = updated_sequence

        # Update plan with new section
        updated_plan = current_plan.model_copy(update={section_name: updated_section})

        # Update repository with new plan list
        updated_plans = self._lesson_plans.copy()
        updated_plans[plan_index] = updated_plan
        object.__setattr__(self, "_lesson_plans", updated_plans)

    def update_exercise_sequence(
        self,
        *,
        id: int,
        name: str,
        reps: int,
        notes: str,
    ) -> None:
        # Find sequence location
        plan_index = None
        section_name = None
        sequence_index = None

        for p_idx, plan in enumerate(self._lesson_plans):
            for s_name in ["warm_up", "main_session", "cool_down"]:
                section = getattr(plan, s_name)
                for seq_idx, sequence in enumerate(section):
                    if sequence.id == id:
                        plan_index = p_idx
                        section_name = s_name
                        sequence_index = seq_idx
                        break
                if sequence_index is not None:
                    break
            if sequence_index is not None:
                break

        if sequence_index is None:
            raise lesson_plans.SequenceDoesNotExist(sequence_id=id)

        # Type narrowing
        assert plan_index is not None
        assert section_name is not None

        # Get current objects
        current_plan = self._lesson_plans[plan_index]
        current_section = getattr(current_plan, section_name)
        current_sequence = current_section[sequence_index]

        # Update sequence metadata (preserving sets)
        updated_sequence = current_sequence.model_copy(
            update={
                "name": name,
                "reps": reps,
                "notes": notes,
            }
        )

        # Update section with new sequence
        updated_section = current_section.copy()
        updated_section[sequence_index] = updated_sequence

        # Update plan with new section
        updated_plan = current_plan.model_copy(update={section_name: updated_section})

        # Update repository with new plan list
        updated_plans = self._lesson_plans.copy()
        updated_plans[plan_index] = updated_plan
        object.__setattr__(self, "_lesson_plans", updated_plans)

    def delete_exercise_sequence(self, sequence_id: int) -> None:
        # Find sequence location
        plan_index = None
        section_name = None
        sequence_index = None

        for p_idx, plan in enumerate(self._lesson_plans):
            for s_name in ["warm_up", "main_session", "cool_down"]:
                section = getattr(plan, s_name)
                for seq_idx, sequence in enumerate(section):
                    if sequence.id == sequence_id:
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

        # Type narrowing
        assert plan_index is not None
        assert section_name is not None

        # Get current objects
        current_plan = self._lesson_plans[plan_index]
        current_section = getattr(current_plan, section_name)

        # Filter out the sequence
        updated_section = [s for s in current_section if s.id != sequence_id]

        # Update plan with new section
        updated_plan = current_plan.model_copy(update={section_name: updated_section})

        # Update repository with new plan list
        updated_plans = self._lesson_plans.copy()
        updated_plans[plan_index] = updated_plan
        object.__setattr__(self, "_lesson_plans", updated_plans)


def _section_to_field_name(section: lesson_plans.LessonPlanSection) -> str:
    """Convert LessonPlanSection enum to field name."""
    mapping = {
        lesson_plans.LessonPlanSection.WARM_UP: "warm_up",
        lesson_plans.LessonPlanSection.MAIN_SESSION: "main_session",
        lesson_plans.LessonPlanSection.COOL_DOWN: "cool_down",
    }
    return mapping[section]
