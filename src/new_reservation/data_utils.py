import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Room types will be loaded from metadata.json and room_mapping.json
ROOM_TYPE_DESCRIPTIONS = {}
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
metadata_path = os.path.join(base_dir, "data", "metadata.json")
room_mapping_path = os.path.join(base_dir, "data", "room_mapping.json")
booking_data_path = os.path.join(base_dir, "data", "sample_reservations.csv")


# Function to load room type descriptions from metadata.json
def load_room_descriptions():
    """Load room descriptions from metadata.json file"""
    import json
    import os

    # Load the metadata file
    # Get the absolute path of the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Load the metadata file using absolute path
    metadata = load_metadata()
    # Load the room mapping file
    with open(room_mapping_path, "r") as f:
        room_mapping = json.load(f)

    # Extract room types from all hotels
    # Structure: {'hotel_name': {'room_code': room_description, ...}, ...}
    hotel_room_descriptions = {}

    # Also maintain a global room descriptions dictionary for backward compatibility
    global_room_descriptions = {}

    # Hotel name and keyword mapping
    HOTEL_NAME_KEYWORD_MAPPING = {}

    price_mapping = metadata.get("PriceMapping", {})

    for hotel in metadata.get("HotelsAndResorts", []):
        hotel_name = hotel.get("Name")
        hotel_keyword = hotel.get("Keyword")
        HOTEL_NAME_KEYWORD_MAPPING[hotel_name] = hotel_keyword
        # Initialize hotel's room descriptions
        hotel_room_descriptions[hotel_keyword] = {}

        for room in hotel.get("RoomTypes", []):
            # Find the room code from the mapping
            room_type = room.get("Type").upper()
            room_code = None

            if room_type in room_mapping:
                room_code = room_mapping[room_type]
                # print(f"room type for hotel {hotel_name}: {room_type} {room_code} ")
                # print(f"room type for hotel {hotel_name}: {room_type} {room_code} ")

            if room_code:
                # Calculate base rate from price mapping
                base_rate = 150  # Default rate if not found
                if room.get("Price") in price_mapping:
                    base_rate = price_mapping[room.get("Price")]

                # Create room description entry
                room_description = {
                    "type_name": room_type,
                    "description": room.get("Description", ""),
                    "amenities": room.get("Amenities", []),
                    "total_count": room.get("TotalCount", 0),
                    "base_rate": base_rate,
                    "capacity": 2,  # Default capacity
                    "hotel_name": hotel_name,  # Store hotel name for reference
                    "hotel_keyword": hotel_keyword,  # Store hotel keyword for lookup
                }
                # print(f"room description {room_description}")

                # Adjust capacity based on room type keywords
                if "Suite" in room_type or "Presidential" in room_type:
                    room_description["capacity"] = 3
                if "Family" in room_type or "Presidential" in room_type:
                    room_description["capacity"] = 4

                # Add to both hotel-specific and global dictionaries
                hotel_room_descriptions[hotel_keyword][room_code] = room_description
                global_room_descriptions[room_code] = (
                    room_description  # Last hotel with this code will win
                )

    print(f"Loaded room descriptions for {len(hotel_room_descriptions)} hotels")
    return {
        "hotel_specific": hotel_room_descriptions,
        "global": global_room_descriptions,
        "hotel_name_keyword_mapping": HOTEL_NAME_KEYWORD_MAPPING,
    }


def load_metadata():
    """Load hotel metadata from JSON file"""
    try:

        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        print("Metadata loaded successfully")
        return metadata
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return None


# Meal plan descriptions with pricing
MEAL_PLAN_DESCRIPTIONS = {
    "AI": {
        "name": "All Inclusive",
        "description": "All meals, snacks, beverages, and select activities included",
        "price_per_person": 85,
    },
    "BB": {
        "name": "Bed & Breakfast",
        "description": "Room with daily breakfast included",
        "price_per_person": 25,
    },
    "FB": {
        "name": "Full Board",
        "description": "Breakfast, lunch, and dinner included",
        "price_per_person": 60,
    },
    "HB": {
        "name": "Half Board",
        "description": "Breakfast and dinner included",
        "price_per_person": 45,
    },
    "": {
        "name": "Room Only",
        "description": "Room accommodation only, no meals included",
        "price_per_person": 0,
    },
}


def load_booking_data():
    """Load and process booking data from CSV file"""
    try:
        booking_data = pd.read_csv(booking_data_path)
        print("Loaded csv file")

        # Convert date column to datetime
        booking_data["stg_stay_dt"] = pd.to_datetime(booking_data["stg_stay_dt"])
        return booking_data
    except Exception as e:
        print(f"Error loading booking data: {e}")
        return None


def check_room_availability(
    property_name: str,
    check_in: str,
    check_out: str,
    rooms_needed: int = 1,
    budget_min: int = 0,
    budget_max: int = 0,
) -> List[Dict]:
    """
    Check availability and return available room types for a given property and dates.

    Args:
        property_name (str): Name of the hotel/property
        check_in (str): Check-in date in 'YYYY-MM-DD' format
        check_out (str): Check-out date in 'YYYY-MM-DD' format
        rooms_needed (int): Number of rooms needed (default: 1)
        budget_min (int): Minimum budget per night (default: 0, no minimum)
        budget_max (int): Maximum budget per night (default: 0, no maximum)

    Returns:
        List[Dict]: List of available room types with details
    """
    print(f"INSIDE UTIL FNChecking availability for {property_name} from {check_in} to {check_out}")
    try:
        # Load required data
        room_data = load_room_descriptions()
        booking_data = load_booking_data()
        metadata = load_metadata()

        if not room_data or booking_data is None or not metadata:
            print("Error: Could not load required data")
            return []

        # Get hotel name to keyword mapping
        hotel_name_keyword_mapping = room_data.get("hotel_name_keyword_mapping", {})
        hotel_room_descriptions = room_data.get("hotel_specific", {})

        # Step 1: Find hotel keyword from property name
        hotel_keyword = hotel_name_keyword_mapping.get(property_name)
        if not hotel_keyword:
            print(f"Error: Property '{property_name}' not found in hotel mapping")
            return []

        # Step 3: Convert dates and create date range
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        except ValueError as e:
            print(f"Error: Invalid date format. Use YYYY-MM-DD format. {e}")
            return []

        if check_in_date >= check_out_date:
            print("Error: Check-in date must be before check-out date")
            return []

        # Generate date range for the stay (excluding checkout date)
        date_range = pd.date_range(
            check_in_date, check_out_date - timedelta(days=1), freq="D"
        )
        # print(f"DEBUG: Date Range {date_range}")
        # Step 2: Get all room types for this hotel from room descriptions
        hotel_room_types = list(hotel_room_descriptions.get(hotel_keyword, {}).keys())

        if len(hotel_room_types) == 0:
            print(f"No room types found for hotel '{property_name}'")
            return []

        # Step 3: Check availability for each room type using actual room counts
        available_rooms = []

        for room_code in hotel_room_types:
            # Get room description to find actual total count for this room type
            room_info = hotel_room_descriptions.get(hotel_keyword, {}).get(room_code)

            if not room_info:
                continue  # Skip if no room info available

            # Use actual total count from room description instead of estimated division
            room_capacity = room_info.get("total_count", 0)

            if room_capacity == 0:
                continue  # Skip if no rooms of this type available

            min_available = room_capacity
            day_bookings = 0
            # Check availability for each night of the stay
            for date in date_range:
                day_bookings = booking_data[
                    (booking_data["stg_hotel_name_txt"] == hotel_keyword)
                    & (booking_data["stg_room_type_cd"] == room_code)
                    & (booking_data["stg_stay_dt"] == str(date.date()))
                ]["room_nights"].sum()

                # print(f"DEBUG: {date.date()} - Room Code: {room_code}, Capacity: {room_capacity}, Booked: {day_bookings}")
                available_on_date = room_capacity - day_bookings
                min_available = min(min_available, available_on_date)

            # Only include room types that have sufficient availability
            if min_available >= rooms_needed:
                available_rooms.append(
                    {
                        "room_code": room_code,
                        "room_type": room_info.get("type_name", room_code),
                        "description": room_info.get("description", ""),
                        "amenities": room_info.get("amenities", []),
                        "guest_capacity": room_info.get("capacity", 2),
                        "base_rate_per_night": room_info.get("base_rate", 150),
                        # 'available_rooms': int(min_available),
                        # 'total_capacity': room_capacity,
                        # 'hotel_name': room_info.get('hotel_name', property_name),
                        # 'hotel_keyword': hotel_keyword
                    }
                )

        # Apply budget filtering if budget range is specified
        if budget_min > 0 or budget_max > 0:
            filtered_rooms = []
            for room in available_rooms:
                room_rate = room["base_rate_per_night"]

                # Check if room fits within budget range
                if budget_min > 0 and room_rate < budget_min:
                    continue  # Room is below minimum budget
                if budget_max > 0 and room_rate > budget_max:
                    continue  # Room is above maximum budget

                filtered_rooms.append(room)

            available_rooms = filtered_rooms
            if budget_min > 0 or budget_max > 0:
                budget_str = (
                    f" within budget range ${budget_min}-${budget_max}"
                    if budget_min > 0 and budget_max > 0
                    else (
                        f" above ${budget_min}"
                        if budget_min > 0
                        else f" under ${budget_max}"
                    )
                )
                # print(f"After budget filtering{budget_str}: {len(available_rooms)} room types remain")

        # Sort by price (lowest to highest)
        available_rooms.sort(key=lambda x: x["base_rate_per_night"])

        print(
            f"Found {len(available_rooms)} available room types for '{property_name}' from {check_in} to {check_out}"
        )
        return available_rooms

    except Exception as e:
        print(f"Error checking availability: {e}")
        return []
