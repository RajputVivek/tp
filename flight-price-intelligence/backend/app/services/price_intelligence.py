from datetime import date, timedelta
from sqlalchemy.orm import Session

from backend.app.models.price_snapshot import PriceSnapshot


# Minimum data required before judging a deal
MIN_SAMPLE_SIZE = 7

# Rolling window for intelligence (days)
LOOKBACK_DAYS = 30


def get_price_baseline(
    db: Session,
    route_id: int,
):
    """
    Returns:
        (historical_avg, recent_median, sample_size)

    If not enough data exists:
        (None, None, 0)
    """

    cutoff_date = date.today() - timedelta(days=LOOKBACK_DAYS)

    snapshots = (
        db.query(PriceSnapshot.price)
        .filter(
            PriceSnapshot.route_id == route_id,
            PriceSnapshot.departure_date >= cutoff_date,
        )
        .all()
    )

    # Flatten [(price,), (price,)] → [price, price]
    prices = [row[0] for row in snapshots]

    sample_size = len(prices)

    # Not enough data yet → learn first
    if sample_size < MIN_SAMPLE_SIZE:
        return None, None, 0

    # Sort for median calculation
    prices.sort()

    # Average
    historical_avg = sum(prices) / sample_size

    # Median
    mid = sample_size // 2
    if sample_size % 2 == 0:
        recent_median = (prices[mid - 1] + prices[mid]) / 2
    else:
        recent_median = prices[mid]

    return historical_avg, recent_median, sample_size
