from datetime import date
from backend.app.services.flight_api.client import AmadeusClient
from backend.app.services.price_intelligence import get_price_baseline
from backend.app.services.price_collector import collect_price
from backend.app.services.deal_detector import is_valid_deal, calculate_discount
from backend.app.data.anywhere_destinations import POPULAR_DESTINATIONS


def scan_anywhere(db, origin, threshold):
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
        from backend.app.models.route import Route

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

        # Store price
        collect_price(
            db=db,
            route_id=route.id,
            origin=origin,
            destination=destination,
        )

        # Get historical baseline
        historical_avg, recent_median = get_price_baseline(
            db=db,
            route_id=route.id,
        )

        if not historical_avg or not recent_median:
            continue

        current_price = offer["price"]

        if not is_valid_deal(
            current_price=current_price,
            historical_avg=historical_avg,
            recent_median=recent_median,
            threshold=threshold,
        ):
            continue

        discount = calculate_discount(current_price, historical_avg)

        results.append({
            "destination": destination,
            "price": current_price,
            "discount": discount,
        })

    # Sort best deals first
    return sorted(results, key=lambda x: x["discount"], reverse=True)
