def calculate_confidence(
    discount_percent: float,
    sample_size: int,
):
    """
    Returns (label, score)
    """

    if sample_size >= 30 and discount_percent >= 40:
        return "High", 0.9

    if sample_size >= 15 and discount_percent >= 30:
        return "Medium", 0.7

    if sample_size >= 7 and discount_percent >= 20:
        return "Low", 0.5

    return "Very Low", 0.3
