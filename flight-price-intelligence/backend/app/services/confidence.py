def calculate_confidence(
    discount_percent: float,
    sample_size: int,
):
    """
    Calculate confidence level for a detected flight deal.

    Confidence is based on:
    - How large the discount is
    - How much historical data exists (sample size)

    Returns:
        (confidence_label: str, confidence_score: float)
    """

    # Strong data + strong discount
    if sample_size >= 30 and discount_percent >= 40:
        return "High", 0.9

    # Good data + decent discount
    if sample_size >= 15 and discount_percent >= 30:
        return "Medium", 0.7

    # Minimum usable data + noticeable discount
    if sample_size >= 7 and discount_percent >= 20:
        return "Low", 0.5

    # Very early / weak signal
    return "Very Low", 0.3
