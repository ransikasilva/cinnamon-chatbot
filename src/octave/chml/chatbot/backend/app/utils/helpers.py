"""Utility helper functions.

========================================================================================
 Copyright (c) 2025 OCTAVE. All rights reserved.

 This is proprietary and confidential software of OCTAVE.
 Unauthorized use, reproduction, or distribution is strictly prohibited.
========================================================================================
"""


def generate_reservation_url(booking_data: dict) -> str:
    """Generate Cinnamon Hotels reservation URL with query parameters."""
    base_url = "https://reservations.cinnamonhotels.com/"

    # Format dates for URL (YYYY-MM-DD)
    check_in = booking_data["check_in"]
    check_out = booking_data["check_out"]

    # Build URL with query parameters
    url = f"{base_url}?adult={booking_data['adults']}"
    url += f"&arrive={check_in}"
    url += f"&chain={booking_data['chain_id']}"
    url += f"&child={booking_data['children']}"
    url += "&currency=USD"
    url += f"&depart={check_out}"
    url += f"&hotel={booking_data['property_id']}"
    url += "&level=hotel"
    url += "&locale=en-US"
    url += "&productcurrency=USD"
    url += f"&rooms={booking_data['rooms']}"
    url += "&segment=BB"

    return url
