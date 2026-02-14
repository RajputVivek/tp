from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from backend.app.models.price_snapshot import PriceSnapshot


MIN_SAMPLE_SIZE = 7          # minimum data points required
LOOKBACK_DAYS = 30           # rolling window


def get_price_baseline(
    db: Session,
    route_id: int,
):
    """
    Returns (historical_avg, recent_median) if enough data exists,
    otherwise returns (None, None).
    """

    cutoff_date = date.today() - timedelta(days=LOOKBACK_DAYS)

    prices = (
        db.query(PriceSnapshot.price)
        .filter(
            PriceSnapshot.route_id == route_id,
            PriceSnapshot.departure_date >= cutoff_date,
        )
        .all()
    )

    if len(prices) < MIN_SAMPLE_SIZE:
        return None, None

    values = sorted(p[0] for p in prices)

    avg_price = sum(values) / len(values)

    mid = len(values) // 2
    if len(values) % 2 == 0:
        median_price = (values[mid - 1] + values[mid]) / 2
    else:
        median_price = values[mid]

    return avg_price, median_price
