
# Validation
## Exercise validity
Evaluation of whether the exercises included in the generated plan actually exist in the exercise bank.
- 100% of exercises should be valid.
- Any invalid exercises will be listed.
Note that if the same invalid exercises appears multiple times in the plan, this metric penalises it every
time it is used.

**Outcome:** 100.0%

## Equipment validity
Validates that all equipment used in the plan is available according to requirements.
- 100% of equipment should be valid.
- Any invalid equipment will be listed.
Note that if the same invalid equipment appears multiple times in the plan, this metric penalises it every
time it is used.

**Outcome:** 100.0%

## Movement variant validity
Validates that movement variants used for each exercise are valid according to the exercise bank.
- 100% should be valid.
- Any sets with invalid movement variants will be counted.

**Outcome:** 100.0%

## Equipment variant validity
Validates that equipment variants used for each exercise are valid according to the exercise bank.
- 100% should be valid.
- Any sets with invalid equipment for the exercise will be counted.
Note: empty list is always valid (no equipment).

**Outcome:** 100.0%

# Requirements compliance
## Target duration
Comparison of the duration of the generated lesson plan relative to the required duration.
- If this is 100%, then the generated lesson plan is the ideal duration.
- If this is less than 100%, then the generated lesson plan is too short.
- If this is greater than 100%, then the generated lesson plan is too long.
A duration in the range 90-110% is deemed acceptable.

**Outcome:** 97.824%

## Difficulty score
Compares the difficulty distribution of the generated plan against target difficulty.
- Uses scoring: Beginner=1, Intermediate=5, Advanced=10.
- 100% means perfect match, <100% means easier, >100% means harder.

**Outcome:** 130.5% (generated: 3.80, target: 5.33)

## Muscle group coverage
Percentage of exercise sets whose primary muscle group matches requirements.
- This should be in the range 70-90%.
- A score of less than 70% means the wrong muscle groups are being targeted too much.
- A score of greater than 90% means the class is not varied enough

**Outcome:** 72.6% (required: [<MuscleGroup.CHEST: 'CHEST'>, <MuscleGroup.CORE: 'CORE'>, <MuscleGroup.GLUTES: 'GLUTES'>, <MuscleGroup.HIP_FLEXORS: 'HIP_FLEXORS'>, <MuscleGroup.INNER_THIGHS: 'INNER_THIGHS'>, <MuscleGroup.TRICEPS: 'TRICEPS'>], in plan: [<MuscleGroup.BACK_EXTENSORS: 'BACK_EXTENSORS'>, <MuscleGroup.CORE: 'CORE'>, <MuscleGroup.GLUTES: 'GLUTES'>, <MuscleGroup.HAMSTRINGS: 'HAMSTRINGS'>, <MuscleGroup.INNER_THIGHS: 'INNER_THIGHS'>, <MuscleGroup.OBLIQUES: 'OBLIQUES'>, <MuscleGroup.SHOULDERS: 'SHOULDERS'>])

## Equipment utilization
Percentage of available equipment actually used in the plan.
- If just one or two pieces of equipment are available, this should be 100%.
- If more than two pieces of equipment are available, this can be less than 100%.

**Outcome:** 100.0% (available: [], used: [<Equipment.BALL: 'BALL'>])

# Structural quality
## Section balance
Evaluates time distribution across lesson plan sections.
- Ideal: warm-up 10%, main session 80%, cool-down 10%.
- Correlation coefficient shows alignment (1.0 = perfect).

**Outcome:** Correlation: 1.00 (warm-up: 14.7%, main: 71.4%, cool-down: 13.9%)

## Transition quality
Measures smoothness of flow by counting position changes between sequences.
- Lower percentages are better (fewer position changes = smoother flow).
- Position changes are counted between consecutive sequences across all sections.

**Outcome:** 80.5% (70/87 transitions require position change)

## Progressive difficulty
Measures whether difficulty increases through the main session.
- Sequences should get gradually harder during the class.
- Regression count shows how many times difficulty drops significantly.

**Outcome:** Progressive: Yes (regressions: 1, trajectory: [4.64, 4.22, 4.47, 5.83, 3.53, 5.82, 7.50, 4.98])

## Variant ordering compliance
Checks that sequences follow proper variant ordering rules.
- First set in a sequence should use STANDARD variant.
- PULSE/HOLD variants should only appear at sequence ends (last set).
- Returns percentage of sequences following these rules.

**Outcome:** 96.842%

## Equipment consistency compliance
Checks that equipment usage is consistent within each sequence.
- All sets in a sequence should use the same equipment (or none).
- Returns percentage of sequences with consistent equipment usage.

**Outcome:** 97.883%

## Muscle group focus compliance
Checks that muscle group focus is consistent within each sequence.
- All sets in a sequence should target the same primary muscle group.
- Returns percentage of sequences with consistent muscle group focus.

**Outcome:** 32.367%

## Starting position consistency compliance
Checks that starting position is consistent within each sequence.
- All exercises in a sequence should share the same starting position.
- Returns percentage of sequences with consistent starting position.

**Outcome:** 94.992%
