from amadeus import Client, ResponseError
from backend.app.core.config import (
    AMADEUS_API_KEY,
    AMADEUS_API_SECRET,
)


class AmadeusClient:
    def __init__(self):
        if not AMADEUS_API_KEY or not AMADEUS_API_SECRET:
            raise RuntimeError(
                "Amadeus API credentials missing. "
                "Set AMADEUS_API_KEY and AMADEUS_API_SECRET."
            )

        self.client = Client(
            client_id=AMADEUS_API_KEY,
            client_secret=AMADEUS_API_SECRET,
        )

    def get_cheapest_offer(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        adults: int = 1,
    ):
        try:
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=adults,
                max=5,
            )

            offers = response.data
            if not offers:
                return None

            cheapest = min(
                offers,
                key=lambda o: float(o["price"]["total"])
            )

            return {
                "price": float(cheapest["price"]["total"]),
                "currency": cheapest["price"]["currency"],
                "airline": cheapest["validatingAirlineCodes"][0],
                "stops": len(
                    cheapest["itineraries"][0]["segments"]
                ) - 1,
            }

        except ResponseError as error:
            print("❌ Amadeus API error:", error)
            return None
