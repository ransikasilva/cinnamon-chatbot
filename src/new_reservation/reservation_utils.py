import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Use the same import pattern as in reservation_tools.py

from models import get_llm
from new_reservation.data_utils import load_metadata



def filter_hotels_by_location_and_type(hotels_data, location):
    """
    Filter hotels based on location and type criteria:
    - If location is Sri Lanka: include only hotels and resorts (exclude Maldives type)
    - If location is Maldives: include only Maldives type
    Returns list of filtered hotels with name, description, and type
    """
    filtered_hotels = []

    for hotel in hotels_data:
        hotel_type = hotel.get("Type", "")
        hotel_location = hotel.get("Location", "")

        # Filter based on location
        if location == "Sri Lanka":
            # For Sri Lanka: include hotels and resorts but exclude Maldives type
            if "Sri Lanka" in hotel_location and hotel_type != "Maldives":
                filtered_hotels.append(
                    {
                        "Name": hotel.get("Name", ""),
                        "Type": hotel_type,
                        "Location": hotel_location,
                        "UniqueDescription": hotel.get("UniqueDescription", ""),
                        "RoomTypes": hotel.get("RoomTypes", []),
                        "TotalRooms": hotel.get("TotalRooms", 0),
                    }
                )
        elif location == "Maldives":
            # For Maldives: include only Maldives type
            if hotel_type == "Maldives":
                filtered_hotels.append(
                    {
                        "Name": hotel.get("Name", ""),
                        "Type": hotel_type,
                        "Location": hotel_location,
                        "UniqueDescription": hotel.get("UniqueDescription", ""),
                        "RoomTypes": hotel.get("RoomTypes", []),
                        "TotalRooms": hotel.get("TotalRooms", 0),
                    }
                )

    return filtered_hotels


def calculate_total_cost(reservation_state):
    """Calculate the total cost based on room rate, duration, guests, children, and meal plan"""

    # Get reservation details
    duration = reservation_state.get("duration", 1)
    guests = reservation_state.get("guests", 1)
    children = reservation_state.get("children", 0)
    rooms_needed = reservation_state.get("rooms_needed", 1)
    meal_type = reservation_state.get("meal_type", "Room Only")
    selected_room_data = reservation_state.get("selected_room_data", {})

    # Get room rate per night
    room_rate_per_night = selected_room_data.get(
        "base_rate_per_night", 200
    )  # Default fallback

    # Calculate base room cost
    base_room_cost = room_rate_per_night * duration * rooms_needed

    # Define meal plan costs per person per day
    meal_costs = {
        "room only": 0,
        "breakfast included": 25,
        "half board": 50,
        "full board": 75,
        "all inclusive": 120,
    }

    # Get meal cost per person per day
    meal_cost_per_day = meal_costs.get(meal_type.lower(), 0)

    # Calculate total meal costs
    total_people = guests + children
    total_meal_cost = meal_cost_per_day * total_people * duration

    # Calculate total cost
    total_cost = base_room_cost + total_meal_cost

    return {
        "total_cost": total_cost,
        "breakdown": {
            "room_cost": base_room_cost,
            "meal_cost": total_meal_cost,
            "room_rate_per_night": room_rate_per_night,
            "meal_cost_per_person_per_day": meal_cost_per_day,
            "duration": duration,
            "guests": guests,
            "children": children,
            "rooms": rooms_needed,
        },
    }


def parse_booking_details(booking_info: str) -> dict:
    """Parse user booking information into structured data"""
    import re
    from datetime import datetime, timedelta

    info = booking_info.lower()
    original_info = booking_info  # Keep original case for dates
    parsed = {
        "check_in": None,
        "check_out": None,
        "guests": None,
        "children": None,
        "rooms": None,
        "budget_range": None,
    }

    # Parse check-in date (various formats)
    checkin_patterns = [
        r"check-in[:\s]+(\d{4}-\d{2}-\d{2})",  # check-in 2025-10-09
        r"checkin[:\s]+(\d{4}-\d{2}-\d{2})",  # checkin 2025-10-09
        r"(\d{4}-\d{2}-\d{2})\s*(?:to|,|\s+check)",  # 2025-10-09 to/,/check
    ]

    for pattern in checkin_patterns:
        match = re.search(pattern, original_info, re.IGNORECASE)
        if match:
            parsed["check_in"] = match.group(1)
            break

    # Parse check-out date (various formats)
    checkout_patterns = [
        r"check-out[:\s]+(\d{4}-\d{2}-\d{2})",  # check-out 2025-10-15
        r"checkout[:\s]+(\d{4}-\d{2}-\d{2})",  # checkout 2025-10-15
        r"(?:to|,)\s*(\d{4}-\d{2}-\d{2})",  # to 2025-10-15
        r"check-out\s+(\d{4}-\d{2}-\d{2})",  # check-out 2025-10-15
    ]

    for pattern in checkout_patterns:
        match = re.search(pattern, original_info, re.IGNORECASE)
        if match:
            parsed["check_out"] = match.group(1)
            break

    # Parse guest count
    guest_matches = re.findall(r"(\d+)\s*(?:adult|guest|people|person)", info)
    if guest_matches:
        parsed["guests"] = int(guest_matches[0])

    # Parse children count
    children_matches = re.findall(r"(\d+)\s*(?:child|children|kid)", info)
    if children_matches:
        parsed["children"] = int(children_matches[0])

    # Parse room count
    room_matches = re.findall(r"(\d+)\s*room", info)
    if room_matches:
        parsed["rooms"] = int(room_matches[0])

    # Parse budget range - improved pattern to avoid matching dates
    budget_patterns = [
        r"budget\s+\$?(\d+)[-\s]*(?:to|-|\$)\s*\$?(\d+)",  # budget $100-$500
        r"\$(\d{2,4})[-\s]*(?:to|-)\s*\$(\d{2,4})",  # $100-$500 (2-4 digits to avoid dates)
        r"budget\s+\$?(\d+)\s*[-]\s*\$?(\d+)",  # budget $100-$500
    ]

    for pattern in budget_patterns:
        budget_matches = re.findall(pattern, info)
        if budget_matches:
            min_budget, max_budget = budget_matches[0]
            # Only accept reasonable budget ranges (not dates)
            min_val, max_val = int(min_budget), int(max_budget)
            if min_val < 2000 and max_val < 2000 and min_val < max_val:
                parsed["budget_range"] = [min_val, max_val]
                break

    return parsed


def extract_property_name(user_query: str) -> Optional[str]:
    """Extract hotel/property name from user query using LLM"""
    try:
        # Load hotel data to get valid property names
        metadata = load_metadata()
        hotels_data = metadata.get("HotelsAndResorts", [])
        
        if not hotels_data:
            return None
        
        # Get list of hotel names for validation
        hotel_names = [hotel.get("Name", "") for hotel in hotels_data]
        
        # Create LLM prompt
        prompt = f"""Extract the hotel or property name mentioned in the user's query, if any.
If no hotel/property name is mentioned, return "None".

USER QUERY: "{user_query}"

AVAILABLE HOTELS:
{', '.join(hotel_names)}

Return only the exact hotel name from the list above, or "None" if no match found. Be generous with partial matches.
"""
        
        # Get LLM response
        llm = get_llm()
        response = llm.invoke(prompt)
        extracted_name = response.content if hasattr(response, "content") else str(response)
        
        # Clean up and validate
        extracted_name = extracted_name.strip().strip('"\'')
        if extracted_name.lower() == "none" or not extracted_name:
            return None
            
        # Find best match from available hotels
        best_match = None
        for hotel_name in hotel_names:
            if hotel_name.lower() == extracted_name.lower():
                return hotel_name  # Exact match
            elif hotel_name.lower() in extracted_name.lower() or extracted_name.lower() in hotel_name.lower():
                best_match = hotel_name  # Partial match
                
        return best_match
        
    except Exception as e:
        print(f"Error extracting property name: {e}")
        return None


def extract_location(user_query: str) -> Optional[str]:
    """Extract location (Sri Lanka or Maldives) from user query using both direct matching and LLM"""
    # First try direct matching for efficiency
    user_query_lower = user_query.lower()
    
    if "sri lanka" in user_query_lower:
        return "Sri Lanka"
    elif "maldives" in user_query_lower:
        return "Maldives"
    
    # If direct matching fails, try with LLM for more robust detection
    try:
        prompt = f"""
Determine if the user is asking about Sri Lanka or Maldives in their query.
If neither location is clearly mentioned, return "Unknown".

USER QUERY: "{user_query}"

RESPOND WITH ONLY ONE OF THESE THREE OPTIONS:
- Sri Lanka
- Maldives
- Unknown
        """
        
        llm = get_llm()
        response = llm.invoke(prompt)
        location = response.content if hasattr(response, "content") else str(response)
        
        location = location.strip().strip('"\'')
        if location in ["Sri Lanka", "Maldives"]:
            return location
            
        return None
    except Exception as e:
        print(f"Error extracting location with LLM: {e}")
        return None


def extract_booking_details_llm(user_query: str) -> Dict:
    """
    Use LLM to extract booking details from user query
    
    Args:
        user_query: User's natural language query that might contain booking details
        
    Returns:
        Dict with extracted booking details: check_in, check_out, guests, children, rooms, budget_range
    """
    try:
        llm = get_llm()
        
        # Format today's date for context
        today = datetime.now()
        current_year = today.year
        
        # Create a prompt that asks the LLM to extract booking details
        prompt = f"""
Extract booking details from the user's query and format the response as JSON. Today is {today.strftime('%B %d, %Y')}.

USER QUERY: "{user_query}"

Extract these fields (return null if not present):
1. check_in: ISO format date (YYYY-MM-DD) when the user wants to check in
2. check_out: ISO format date (YYYY-MM-DD) when the user wants to check out
3. guests: Number of adult guests (integer)
4. children: Number of children (integer, default to 0 if not specified)
5. rooms: Number of rooms needed (integer, default to 1 if not specified)
6. budget_range: Array with [min, max] values in USD for the price range per night

INSTRUCTIONS:
- Format dates in ISO format (YYYY-MM-DD)
- If month/day are mentioned but no year, assume the current year ({current_year}) or next year if the date would be in the past
- If only a duration is mentioned (e.g., "5 nights starting Dec 12"), calculate the check-out date
- If budget is a single value, use [value-50, value+50] as the range
- Dates like "next weekend", "next month", "this Friday" should be converted to actual dates
- For budget range, if only one number is mentioned (e.g., "$300"), create a reasonable range around it

RESPOND WITH VALID JSON ONLY, like this:
{{
  "check_in": "YYYY-MM-DD",
  "check_out": "YYYY-MM-DD",
  "guests": 2,
  "children": 0,
  "rooms": 1,
  "budget_range": [100, 300]
}}
        """
        
        response = llm.invoke(prompt)
        response_text = response.content if hasattr(response, "content") else str(response)
        
        # Extract the JSON part of the response
        import re
        json_match = re.search(r'({[\s\S]*})', response_text)
        if json_match:
            json_str = json_match.group(1)
            booking_details = json.loads(json_str)
            return booking_details
        
        return {}
    except Exception as e:
        print(f"Error extracting booking details with LLM: {e}")
        return {}


def validate_property(property_name: str, location: Optional[str]) -> Optional[Dict]:
    """Validate property exists and return its data"""
    try:
        # Load hotel data
        metadata = load_metadata()
        hotels_data = metadata.get("HotelsAndResorts", [])
        
        if not hotels_data:
            return None
        
        # First try exact match
        for hotel in hotels_data:
            hotel_name = hotel.get("Name", "")
            if hotel_name.lower() == property_name.lower():
                # If location is specified, make sure it matches
                if location and location != "Unknown":
                    hotel_location = hotel.get("Location", "")
                    if location == "Sri Lanka" and "Sri Lanka" not in hotel_location:
                        continue
                    if location == "Maldives" and "Maldives" not in hotel_location and hotel.get("Type") != "Maldives":
                        continue
                
                return hotel
        
        # Try partial match
        for hotel in hotels_data:
            hotel_name = hotel.get("Name", "")
            if property_name.lower() in hotel_name.lower() or hotel_name.lower() in property_name.lower():
                # If location is specified, make sure it matches
                if location and location != "Unknown":
                    hotel_location = hotel.get("Location", "")
                    if location == "Sri Lanka" and "Sri Lanka" not in hotel_location:
                        continue
                    if location == "Maldives" and "Maldives" not in hotel_location and hotel.get("Type") != "Maldives":
                        continue
                
                return hotel
                
        return None
        
    except Exception as e:
        print(f"Error validating property: {e}")
        return None