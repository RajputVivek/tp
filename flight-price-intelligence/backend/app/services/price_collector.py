import random
from datetime import date, timedelta
from sqlalchemy.orm import Session

from backend.app.models.price_snapshot import PriceSnapshot
from backend.app.models.route import Route


def collect_prices_for_route(
    db: Session,
    route: Route,
    days_ahead: int = 30
):
    """
    Stub price collector.
    Replace internals with real API later.
    """

    today = date.today()

    for i in range(1, days_ahead + 1):
        departure_date = today + timedelta(days=i)

        fake_price = random.randint(3000, 12000)

        snapshot = PriceSnapshot(
            route_id=route.id,
            departure_date=departure_date,
            price=fake_price,
            currency="INR",
            airline="FAKEAIR",
            stops=random.choice([0, 1])
        )

        db.add(snapshot)

    db.commit()
