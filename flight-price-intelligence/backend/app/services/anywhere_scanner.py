from datetime import date

from backend.app.services.flight_api.client import AmadeusClient
from backend.app.services.price_collector import collect_price
from backend.app.services.price_intelligence import get_price_baseline
from backend.app.services.deal_detector import is_valid_deal, calculate_discount
from backend.app.services.confidence import calculate_confidence
from backend.app.data.anywhere_destinations import POPULAR_DESTINATIONS
from backend.app.models.route import Route


def scan_anywhere(
    db,
    origin: str,
    threshold: int,
):
    """
    Scan popular destinations from origin and return
    confidence-sorted deal results.
    """

    amadeus = AmadeusClient()
    results = []

    for destination in POPULAR_DESTINATIONS:
        if destination == origin:
            continue

        offer = amadeus.get_cheapest_offer(
            origin=origin,
            destination=destination,
            departure_date=date.today().isoformat(),
        )

        if not offer:
            continue

        # Ensure route exists
        route = (
            db.query(Route)
            .filter(
                Route.origin_airport == origin,
                Route.destination_airport == destination,
            )
            .first()
        )

        if not route:
            route = Route(
                origin_airport=origin,
                destination_airport=destination,
                active=True,
            )
            db.add(route)
            db.commit()

        current_price = offer["price"]

        # Store today's price (build history)
        collect_price(
            db=db,
            route_id=route.id,
            origin=origin,
            destination=destination,
        )

        # Get historical intelligence
        historical_avg, recent_median, sample_size = get_price_baseline(
            db=db,
            route_id=route.id,
        )

        if historical_avg is None or recent_median is None:
            continue

        # Deal validation
        if not is_valid_deal(
            current_price=current_price,
            historical_avg=historical_avg,
            recent_median=recent_median,
            threshold=threshold,
        ):
            continue

        discount = calculate_discount(current_price, historical_avg)

        confidence_label, confidence_score = calculate_confidence(
            discount_percent=discount,
            sample_size=sample_size,
        )

        results.append({
            "destination": destination,
            "price": current_price,
            "discount": discount,
            "confidence_label": confidence_label,
            "confidence_score": confidence_score,
            "sample_size": sample_size,
        })

    # Sort by confidence first, then discount
    results.sort(
        key=lambda r: (r["confidence_score"], r["discount"]),
        reverse=True,
    )

    return results
