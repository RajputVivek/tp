def calculate_discount(current_price: float, baseline_price: float) -> float:
    if baseline_price <= 0:
        return 0.0
    return round(((baseline_price - current_price) / baseline_price) * 100, 2)


def is_valid_deal(
    current_price: float,
    historical_avg: float,
    recent_median: float,
    threshold: int
) -> bool:
    """
    Hybrid deal validation:
    - historical_avg: external baseline
    - recent_median: our short-term data
    """

    if current_price >= historical_avg:
        return False

    if current_price >= recent_median:
        return False

    discount = calculate_discount(current_price, historical_avg)

    return discount >= threshold
