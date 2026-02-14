def explain_deal(
    current_price: float,
    historical_avg: float,
    recent_median: float,
    discount_percent: float,
    sample_size: int,
):
    """
    Generate a human-readable explanation of why this is a good deal.
    """

    reasons = []

    # Strong discount explanation
    if discount_percent >= 40:
        reasons.append("price is significantly lower than usual")
    elif discount_percent >= 25:
        reasons.append("price is well below average")
    else:
        reasons.append("price is lower than typical")

    # Median comparison
    if current_price < recent_median:
        reasons.append("below recent median price")

    # Data confidence explanation
    if sample_size >= 30:
        reasons.append("based on strong historical data")
    elif sample_size >= 15:
        reasons.append("based on sufficient recent data")
    else:
        reasons.append("based on limited historical data")

    # Build final explanation
    explanation = "This is a good deal because " + ", ".join(reasons) + "."

    return explanation
