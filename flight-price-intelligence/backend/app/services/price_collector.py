from datetime import date
from sqlalchemy.orm import Session

from backend.app.models.price_snapshot import PriceSnapshot
from backend.app.services.flight_api.client import AmadeusClient


def collect_price(
    db: Session,
    route_id: int,
    origin: str,
    destination: str,
):
    amadeus = AmadeusClient()

    offer = amadeus.get_cheapest_offer(
        origin=origin,
        destination=destination,
        departure_date=date.today().isoformat(),
    )

    if not offer:
        return None

    snapshot = PriceSnapshot(
        route_id=route_id,
        departure_date=date.today(),
        price=offer["price"],
        currency=offer["currency"],
        airline=offer["airline"],
        stops=offer["stops"],
    )

    db.add(snapshot)
    db.commit()

    return snapshot
