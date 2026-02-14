from datetime import date, timedelta

from backend.app.services.flight_api.client import AmadeusClient
from backend.app.services.price_collector import collect_price
from backend.app.services.price_intelligence import get_price_baseline
from backend.app.services.deal_detector import is_valid_deal, calculate_discount
from backend.app.services.confidence import calculate_confidence
from backend.app.services.deal_explainer import explain_deal
from backend.app.models.route import Route


# How far ahead we search
LOOKAHEAD_DAYS = 90

# How frequently we sample dates (to control API usage)
DATE_STEP_DAYS = 7


def scan_best_date(
    db,
    origin: str,
    destination: str,
    threshold: int,
):
    """
    Scan multiple future dates and return the best deal found.
    """

    amadeus = AmadeusClient()
    best_result = None

    today = date.today()

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

    # Iterate through future dates
    for offset in range(0, LOOKAHEAD_DAYS + 1, DATE_STEP_DAYS):
        travel_date = today + timedelta(days=offset)

        offer = amadeus.get_cheapest_offer(
            origin=origin,
            destination=destination,
            departure_date=travel_date.isoformat(),
        )

        if not offer:
            continue

        current_price = offer["price"]

        # Store price snapshot
        collect_price(
            db=db,
            route_id=route.id,
            origin=origin,
            destination=destination,
        )

        # Get intelligence
        historical_avg, recent_median, sample_size = get_price_baseline(
            db=db,
            route_id=route.id,
        )

        if historical_avg is None or recent_median is None:
            continue

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

        explanation = explain_deal(
            current_price=current_price,
            historical_avg=historical_avg,
            recent_median=recent_median,
            discount_percent=discount,
            sample_size=sample_size,
        )

        candidate = {
            "destination": destination,
            "departure_date": travel_date,
            "price": current_price,
            "discount": discount,
            "confidence_label": confidence_label,
            "confidence_score": confidence_score,
            "explanation": explanation,
        }

        # Pick best by confidence → discount
        if not best_result:
            best_result = candidate
        else:
            if (
                candidate["confidence_score"] > best_result["confidence_score"]
                or (
                    candidate["confidence_score"] == best_result["confidence_score"]
                    and candidate["discount"] > best_result["discount"]
                )
            ):
                best_result = candidate

    return best_result
