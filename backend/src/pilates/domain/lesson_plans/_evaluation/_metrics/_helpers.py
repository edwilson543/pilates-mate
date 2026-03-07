def correlation_coefficient(
    actual: list[float],
    ideal: list[float],
) -> float:
    """Calculate Pearson correlation coefficient between two distributions."""
    if len(actual) != len(ideal) or len(actual) == 0:
        return 0.0

    n = len(actual)
    mean_actual = sum(actual) / n
    mean_ideal = sum(ideal) / n

    numerator = sum((a - mean_actual) * (i - mean_ideal) for a, i in zip(actual, ideal))
    denominator_actual = sum((a - mean_actual) ** 2 for a in actual)
    denominator_ideal = sum((i - mean_ideal) ** 2 for i in ideal)

    if denominator_actual == 0 or denominator_ideal == 0:
        return 0.0

    return numerator / (denominator_actual * denominator_ideal) ** 0.5
