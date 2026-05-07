from pilates.domain import exercises


def difficulty_score(difficulty: exercises.Difficulty) -> int:
    return {
        exercises.Difficulty.BEGINNER: 1,
        exercises.Difficulty.INTERMEDIATE: 5,
        exercises.Difficulty.ADVANCED: 10,
    }[difficulty]
