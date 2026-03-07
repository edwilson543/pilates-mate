"""
Automated system prompt optimization script.

This script uses an LLM to iteratively improve the system prompt template by:
1. Generating variations of the current template
2. Evaluating each variation across multiple test scenarios
3. Selecting the best performing variation
4. Using metrics feedback to guide the next iteration

The script uses the template versioning system to organize candidates and results.
"""

import pathlib
import shutil

import click
import pydantic

from pilates import config
from pilates.domain import lesson_plans
from pilates.interfaces.cli._main import async_command


class TemplateVariation(pydantic.BaseModel):
    """Output format for template variations from the optimizer LLM."""

    template_content: str


@click.command("optimise-prompt")
@click.option(
    "--max-iterations",
    default=5,
    type=int,
    help="Maximum number of optimization iterations (default: 5)",
)
@click.option(
    "--candidates-per-iteration",
    default=3,
    type=int,
    help="Number of candidate templates per iteration (default: 3)",
)
@click.option(
    "--improvement-threshold",
    default=0.01,
    type=float,
    help="Minimum score improvement to continue (default: 0.01)",
)
@click.option(
    "--base-version",
    default="v1",
    help="Base template version to optimize from (default: v1)",
)
@async_command
async def optimise_prompt(
    *,
    max_iterations: int,
    candidates_per_iteration: int,
    improvement_threshold: float,
    base_version: str,
) -> None:
    """Iteratively optimize system prompt template using LLM feedback."""
    click.echo("Starting system prompt optimization...")
    click.echo(
        f"Configuration: {max_iterations} iterations, "
        f"{candidates_per_iteration} candidates per iteration"
    )
    click.echo(f"Base version: {base_version}")
    click.echo()

    # Get the current template content.
    template_path = _get_template_path(base_version)
    with open(template_path) as f:
        current_template = f.read()

    # Initialize tracking variables.
    best_template = current_template
    best_version = base_version
    best_score = await _evaluate_template_version(best_version)
    click.echo(f"Baseline score ({base_version}): {best_score:.3f}")
    click.echo()

    # Optimization loop.
    for iteration in range(1, max_iterations + 1):
        click.echo(f"=== Iteration {iteration}/{max_iterations} ===")

        # Generate candidate variations.
        click.echo(f"Generating {candidates_per_iteration} candidate templates...")
        candidates = await _generate_template_variations(
            current_template=best_template,
            previous_score=best_score,
            iteration=iteration,
            candidates_per_iteration=candidates_per_iteration,
            base_version=base_version,
        )

        # Write candidates as versioned templates and evaluate.
        click.echo("Evaluating candidates...")
        candidate_scores = []
        for i, candidate in enumerate(candidates, 1):
            # Write candidate to versioned directory.
            candidate_version = f"v{iteration + 1}-candidate-{i}"
            _write_candidate_template(
                template_content=candidate,
                candidate_version=candidate_version,
                base_version=base_version,
            )

            # Evaluate using the versioning system.
            score = await _evaluate_template_version(candidate_version)
            candidate_scores.append((candidate, candidate_version, score))
            click.echo(f"  Candidate {i} ({candidate_version}): {score:.3f}")

        # Select best candidate.
        iteration_best_template, iteration_best_version, iteration_best_score = max(
            candidate_scores, key=lambda x: x[2]
        )

        # Check for improvement.
        improvement = iteration_best_score - best_score
        click.echo(
            f"Best iteration score: {iteration_best_score:.3f} (improvement: {improvement:+.3f})"
        )

        if improvement > improvement_threshold:
            click.echo(
                f"Improvement found! Promoting {iteration_best_version} to v{iteration + 1}."
            )

            # Promote best candidate to next version.
            next_version = f"v{iteration + 1}"
            _promote_candidate_to_version(iteration_best_version, next_version)

            best_template = iteration_best_template
            best_version = next_version
            best_score = iteration_best_score
        else:
            click.echo("No significant improvement. Stopping optimization.")
            break

        click.echo()

    # Summary.
    click.echo(f"Optimization complete. Final score: {best_score:.3f}")
    click.echo(f"Best template version: {best_version}")
    if best_version != base_version:
        template_dir = _get_templates_dir() / "lesson-planning" / best_version
        click.echo(f"Optimized templates saved to: {template_dir}")


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
    base_version: str,
) -> None:
    """
    Write a candidate template to a versioned directory.

    This creates a new version directory, copies sub-templates from base_version,
    and writes the candidate template as system.jinja.
    """
    templates_dir = _get_templates_dir()
    base_dir = templates_dir / "lesson-planning" / base_version
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
    candidates_per_iteration: int,
    base_version: str,
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
    for i in range(candidates_per_iteration):
        click.echo(f"  Generating candidate {i + 1}...")
        try:
            # Request the optimizer LLM to generate a variation.
            result = await completion_client.get_completion(
                system_prompt=meta_prompt,
                user_prompt=f"Generate variation {i + 1} of {candidates_per_iteration}.",
                output_format=TemplateVariation,
            )
            candidates.append(result.template_content)
        except Exception as e:
            click.echo(f"    Warning: Failed to generate candidate {i + 1}: {e}")
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


async def _evaluate_template_version(version: str) -> float:
    """
    Evaluate a template version by generating and scoring lesson plans.

    Returns a single numeric score (higher is better).
    """
    deps = config.get_evaluation_deps()
    evaluation = await lesson_plans.evaluate_system_prompt(version=version, deps=deps)

    return evaluation.to_numeric_score()
