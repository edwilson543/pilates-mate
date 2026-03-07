"""
Automated system prompt optimization script.

This script uses an LLM to iteratively improve the system prompt template by:
1. Generating variations of the current template
2. Evaluating each variation across multiple test scenarios
3. Selecting the best performing variation
4. Using metrics feedback to guide the next iteration

The script uses the template versioning system to organize candidates and results.
"""

import asyncio
import pathlib
import shutil

import pydantic

from pilates import config
from pilates.domain import exercises, lesson_plans


# Configuration parameters.
MAX_ITERATIONS = 5
CANDIDATES_PER_ITERATION = 3
IMPROVEMENT_THRESHOLD = 0.01
BASE_VERSION = "v1"


class TemplateVariation(pydantic.BaseModel):
    """Output format for template variations from the optimizer LLM."""

    template_content: str


async def _main() -> None:
    print("Starting system prompt optimization...")
    print(
        f"Configuration: {MAX_ITERATIONS} iterations, {CANDIDATES_PER_ITERATION} candidates per iteration"
    )
    print(f"Base version: {BASE_VERSION}")
    print()

    # Get the current template content.
    template_path = _get_template_path(BASE_VERSION)
    with open(template_path) as f:
        current_template = f.read()

    # Get evaluation requirements.
    requirements_list = _get_evaluation_requirements()

    # Initialize tracking variables.
    best_template = current_template
    best_version = BASE_VERSION
    best_score = await _evaluate_template_version(best_version, requirements_list)
    print(f"Baseline score ({BASE_VERSION}): {best_score:.3f}")
    print()

    # Optimization loop.
    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"=== Iteration {iteration}/{MAX_ITERATIONS} ===")

        # Generate candidate variations.
        print(f"Generating {CANDIDATES_PER_ITERATION} candidate templates...")
        candidates = await _generate_template_variations(
            current_template=best_template,
            previous_score=best_score,
            iteration=iteration,
        )

        # Write candidates as versioned templates and evaluate.
        print("Evaluating candidates...")
        candidate_scores = []
        for i, candidate in enumerate(candidates, 1):
            # Write candidate to versioned directory.
            candidate_version = f"v{iteration + 1}-candidate-{i}"
            _write_candidate_template(
                template_content=candidate,
                candidate_version=candidate_version,
            )

            # Evaluate using the versioning system.
            score = await _evaluate_template_version(
                candidate_version, requirements_list
            )
            candidate_scores.append((candidate, candidate_version, score))
            print(f"  Candidate {i} ({candidate_version}): {score:.3f}")

        # Select best candidate.
        iteration_best_template, iteration_best_version, iteration_best_score = max(
            candidate_scores, key=lambda x: x[2]
        )

        # Check for improvement.
        improvement = iteration_best_score - best_score
        print(
            f"Best iteration score: {iteration_best_score:.3f} (improvement: {improvement:+.3f})"
        )

        if improvement > IMPROVEMENT_THRESHOLD:
            print(
                f"Improvement found! Promoting {iteration_best_version} to v{iteration + 1}."
            )

            # Promote best candidate to next version.
            next_version = f"v{iteration + 1}"
            _promote_candidate_to_version(iteration_best_version, next_version)

            best_template = iteration_best_template
            best_version = next_version
            best_score = iteration_best_score
        else:
            print("No significant improvement. Stopping optimization.")
            break

        print()

    # Summary.
    print(f"Optimization complete. Final score: {best_score:.3f}")
    print(f"Best template version: {best_version}")
    if best_version != BASE_VERSION:
        template_dir = _get_templates_dir() / "lesson-planning" / best_version
        print(f"Optimized templates saved to: {template_dir}")


def _get_templates_dir() -> pathlib.Path:
    """Get the path to the templates directory."""
    return pathlib.Path(__file__).parents[3] / "domain" / "templates"


def _get_template_path(version: str) -> pathlib.Path:
    """Get the path to the system prompt template for a specific version."""
    return _get_templates_dir() / "lesson-planning" / version / "system.jinja"


def _write_candidate_template(
    *,
    template_content: str,
    candidate_version: str,
) -> None:
    """
    Write a candidate template to a versioned directory.

    This creates a new version directory, copies sub-templates from BASE_VERSION,
    and writes the candidate template as system.jinja.
    """
    templates_dir = _get_templates_dir()
    base_dir = templates_dir / "lesson-planning" / BASE_VERSION
    candidate_dir = templates_dir / "lesson-planning" / candidate_version

    # Create candidate directory.
    candidate_dir.mkdir(parents=True, exist_ok=True)

    # Copy sub-templates from base version.
    for sub_template in [
        "exercise.jinja",
        "exercise-sequence.jinja",
        "lesson-plan.jinja",
    ]:
        shutil.copy2(base_dir / sub_template, candidate_dir / sub_template)

    # Write candidate template.
    with open(candidate_dir / "system.jinja", "w") as f:
        f.write(template_content)


def _promote_candidate_to_version(
    candidate_version: str,
    target_version: str,
) -> None:
    """
    Promote a candidate version to a permanent version number.

    This renames the candidate directory to the target version name.
    """
    templates_dir = _get_templates_dir()
    candidate_dir = templates_dir / "lesson-planning" / candidate_version
    target_dir = templates_dir / "lesson-planning" / target_version

    # Remove target if it already exists.
    if target_dir.exists():
        shutil.rmtree(target_dir)

    # Rename candidate to target.
    candidate_dir.rename(target_dir)


async def _generate_template_variations(
    *,
    current_template: str,
    previous_score: float,
    iteration: int,
) -> list[str]:
    """
    Generate variations of the current template using an optimizer LLM.

    The optimizer LLM is given the current template and asked to produce
    improved versions while preserving Jinja2 syntax and template structure.
    """
    completion_client = config.get_completion_client()

    meta_prompt = _build_meta_optimization_prompt(
        current_template=current_template,
        previous_score=previous_score,
        iteration=iteration,
    )

    # For simplicity, we'll generate candidates one at a time.
    # Could be optimized to generate multiple in parallel.
    candidates = []
    for i in range(CANDIDATES_PER_ITERATION):
        print(f"  Generating candidate {i + 1}...")
        try:
            # Request the optimizer LLM to generate a variation.
            result = await completion_client.get_completion(
                system_prompt=meta_prompt,
                user_prompt=f"Generate variation {i + 1} of {CANDIDATES_PER_ITERATION}.",
                output_format=TemplateVariation,
            )
            candidates.append(result.template_content)
        except Exception as e:
            print(f"    Warning: Failed to generate candidate {i + 1}: {e}")
            # Fall back to current template if generation fails.
            candidates.append(current_template)

    return candidates


def _build_meta_optimization_prompt(
    *,
    current_template: str,
    previous_score: float,
    iteration: int,
) -> str:
    """
    Build the meta-prompt for the optimizer LLM.

    This prompt instructs the LLM on how to improve the template while
    preserving its structure and Jinja2 syntax.
    """
    return f"""You are a prompt engineering expert optimizing a Jinja2 template for generating Pilates lesson plans.

# Current Template
```jinja2
{current_template}
```

# Current Performance
Overall score: {previous_score:.3f} (higher is better)
Iteration: {iteration}

# Your Task
Generate an improved version of this template that will score higher on our evaluation metrics.

# Key Constraints (DO NOT VIOLATE)
1. Preserve ALL Jinja2 syntax exactly:
   - Keep all {{{{ variable }}}} placeholders unchanged
   - Keep all {{% for ... %}} loops unchanged
   - Keep all {{% if ... %}} conditionals unchanged
   - Keep template structure and includes

2. Only modify the instructional text - the prose that tells the LLM what to do

# What to Optimize
Based on typical issues seen in lesson plan generation:
- Improve clarity and specificity of instructions
- Add more concrete examples where helpful
- Strengthen requirements around structural consistency:
  * Sequences should maintain consistent muscle group focus
  * Sequences should minimize position changes
  * Variant ordering should follow proper rules
- Ensure difficulty progression guidance is clear
- Make equipment and position consistency requirements more explicit

# Output Format
Your response should be structured as JSON with a single field 'template_content'
containing the complete modified template. Start the template with '# Task' and
include the entire template text.
"""


async def _evaluate_template_version(
    version: str,
    requirements_list: list[lesson_plans.LessonPlanRequirements],
) -> float:
    """
    Evaluate a template version by generating and scoring lesson plans.

    Returns a single numeric score (higher is better).
    """
    # Generate and evaluate lesson plans using this template version.
    evaluation_tasks = [
        _generate_and_evaluate_with_version(
            version=version,
            requirements=requirements,
        )
        for requirements in requirements_list
    ]
    evaluations = await asyncio.gather(*evaluation_tasks)

    # Aggregate evaluations.
    aggregated = lesson_plans.GeneratedLessonPlanEvaluation.aggregate(evaluations)

    # Calculate overall score.
    score = _calculate_score_from_evaluation(aggregated)
    return score


async def _generate_and_evaluate_with_version(
    *,
    version: str,
    requirements: lesson_plans.LessonPlanRequirements,
) -> lesson_plans.GeneratedLessonPlanEvaluation:
    """
    Generate a lesson plan using a specific template version and evaluate it.
    """
    completion_client = config.get_completion_client()
    deps = config.get_evaluation_deps()
    uow = config.get_unit_of_work()

    # Get system prompt using the versioning system.
    system_prompt = lesson_plans.get_system_prompt(
        requirements=requirements,
        lesson_plans_repo=uow.lesson_plans,
        exercises_repo=uow.exercises,
        version=version,
    )

    # Generate lesson plan.
    generated_plan = await lesson_plans.generate_lesson_plan(
        requirements=requirements,
        client=completion_client,
        system_prompt=system_prompt,
    )

    # Evaluate the generated plan.
    return lesson_plans.evaluate_generated_lesson_plan(
        generated_plan=generated_plan,
        requirements=requirements,
        deps=deps,
    )


def _calculate_score_from_evaluation(
    evaluation: lesson_plans.GeneratedLessonPlanEvaluation,
) -> float:
    """
    Calculate a single numeric score from an evaluation.

    This is a simplified scoring function that penalizes failures
    and rewards good structural quality.
    """
    score = 100.0

    for eval_item in evaluation.evaluations:
        # Extract numeric value from metric.
        metric_value = _extract_metric_value(eval_item.outcome)

        if eval_item.category == lesson_plans.EvaluationCategory.VALIDATION:
            # Validation metrics should be 100%.
            if metric_value < 100:
                score -= (100 - metric_value) * 2.0  # Heavy penalty.

        elif (
            eval_item.category
            == lesson_plans.EvaluationCategory.REQUIREMENTS_COMPLIANCE
        ):
            # Requirements compliance should be within acceptable ranges.
            if "duration" in eval_item.name.lower():
                # Duration should be 90-110%.
                if not (90 <= metric_value <= 110):
                    score -= abs(metric_value - 100) * 0.5
            else:
                # Other metrics vary, but generally higher is better.
                pass

        elif eval_item.category == lesson_plans.EvaluationCategory.STRUCTURAL_QUALITY:
            # Structural quality metrics are what we're optimizing.
            if "transition" in eval_item.name.lower():
                # Lower transition rate is better.
                score += (100 - metric_value) * 0.3
            elif "compliance" in eval_item.name.lower():
                # Higher compliance is better.
                score += metric_value * 0.5
            elif "progressive" in eval_item.name.lower():
                # Progressive difficulty is good.
                if hasattr(eval_item.outcome, "is_progressive"):
                    score += 10.0 if eval_item.outcome.is_progressive else -5.0

    return max(score, 0.0)


def _extract_metric_value(metric: object) -> float:
    """
    Extract a numeric value from a metric object.

    Handles various metric types by checking for common attributes.
    """
    if hasattr(metric, "value"):
        return float(metric.value)
    elif hasattr(metric, "percentage_of_target"):
        return float(metric.percentage_of_target)
    elif hasattr(metric, "percentage_utilized"):
        return float(metric.percentage_utilized)
    elif hasattr(metric, "percentage_targeting_required_groups"):
        return float(metric.percentage_targeting_required_groups)
    elif hasattr(metric, "transition_rate"):
        return float(metric.transition_rate)
    elif hasattr(metric, "correlation_coefficient"):
        return float(metric.correlation_coefficient) * 100
    else:
        return 0.0


def _get_evaluation_requirements() -> list[lesson_plans.LessonPlanRequirements]:
    """
    Get the list of test scenarios for evaluation.

    This is the same as in evaluate_system_prompt.py but could be
    reduced for faster optimization iterations.
    """
    full_body = [
        lesson_plans.LessonPlanRequirements(
            duration_minutes=45,
            target_difficulty=difficulty,
            target_muscle_groups=[
                exercises.MuscleGroup.GLUTES,
                exercises.MuscleGroup.CORE,
                exercises.MuscleGroup.HIP_FLEXORS,
                exercises.MuscleGroup.INNER_THIGHS,
                exercises.MuscleGroup.CHEST,
                exercises.MuscleGroup.TRICEPS,
            ],
            example_lesson_plan_ids=[],
            available_equipment=available_equipment,
            user_prompt="Focus on core and glutes equally, but weave in some focus on the other muscle groups.",
        )
        for difficulty in exercises.Difficulty
        for available_equipment in [[], [exercises.Equipment.BALL]]
    ]
    core_focus = [
        lesson_plans.LessonPlanRequirements(
            duration_minutes=30,
            target_difficulty=difficulty,
            target_muscle_groups=[
                exercises.MuscleGroup.CORE,
                exercises.MuscleGroup.GLUTES,
                exercises.MuscleGroup.HIP_FLEXORS,
                exercises.MuscleGroup.INNER_THIGHS,
                exercises.MuscleGroup.CHEST,
                exercises.MuscleGroup.TRICEPS,
            ],
            example_lesson_plan_ids=[],
            available_equipment=[exercises.Equipment.BALL],
            user_prompt="Focus mainly on core today, with equal balance given to the other muscle groups.",
        )
        for difficulty in exercises.Difficulty
    ]
    glutes_focus = [
        lesson_plans.LessonPlanRequirements(
            duration_minutes=30,
            target_difficulty=difficulty,
            target_muscle_groups=[
                exercises.MuscleGroup.GLUTES,
                exercises.MuscleGroup.CORE,
                exercises.MuscleGroup.HIP_FLEXORS,
                exercises.MuscleGroup.INNER_THIGHS,
                exercises.MuscleGroup.CHEST,
                exercises.MuscleGroup.TRICEPS,
            ],
            example_lesson_plan_ids=[],
            available_equipment=[exercises.Equipment.BALL],
            user_prompt="Focus mainly on a glutes blast, with equal balance given to the other muscle groups.",
        )
        for difficulty in exercises.Difficulty
    ]
    return full_body + core_focus + glutes_focus


if __name__ == "__main__":
    asyncio.run(_main())
