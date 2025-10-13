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


def extract_guest_count_nlp(query: str) -> Dict:
    """
    Extract guest count from natural language using LLM
    
    Examples:
        "solo traveler" -> {"adults": 1, "children": 0}
        "couple" -> {"adults": 2, "children": 0}
        "me and my wife" -> {"adults": 2, "children": 0}
        "family of 4" -> {"adults": 2, "children": 2} (assumption)
        "3 adults and 2 kids" -> {"adults": 3, "children": 2}
        "traveling with my 2 children" -> {"adults": 1, "children": 2}
    """
    try:
        llm = get_llm()
        
        prompt = f"""Extract the number of guests from this query.

USER QUERY: "{query}"

Return ONLY valid JSON with this exact format:
{{
  "adults": <number of adult guests, integer>,
  "children": <number of children, integer>,
  "confidence": <"high", "medium", or "low">
}}

RULES:
- "solo" or "solo traveler" = 1 adult, 0 children
- "couple" or "me and my wife/husband/partner" = 2 adults, 0 children  
- "family of X" where X ≤ 4 = 2 adults, (X-2) children
- "family of X" where X > 4 = round(X/2) adults, remaining children
- "X adults and Y children/kids" = X adults, Y children
- "traveling with X kids/children" = 1 adult, X children
- "group of X" = X adults, 0 children (unless kids mentioned)
- If no guest info found, return {{"adults": null, "children": null, "confidence": "low"}}

EXAMPLES:
- "solo traveler to Sri Lanka" -> {{"adults": 1, "children": 0, "confidence": "high"}}
- "me and my wife" -> {{"adults": 2, "children": 0, "confidence": "high"}}
- "family of 4" -> {{"adults": 2, "children": 2, "confidence": "medium"}}
- "3 adults 2 kids" -> {{"adults": 3, "children": 2, "confidence": "high"}}
"""
        
        response = llm.invoke(prompt)
        response_text = response.content if hasattr(response, "content") else str(response)
        
        # Extract JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            result = json.loads(json_match.group(0))
            return result
        
        return {"adults": None, "children": None, "confidence": "low"}
        
    except Exception as e:
        print(f"Error extracting guest count: {e}")
        return {"adults": None, "children": None, "confidence": "low"}


def extract_property_preferences_nlp(query: str, location: Optional[str] = None) -> Dict:
    """
    Extract property preferences from natural language
    
    Examples:
        "something coastal" -> {"property_type": "coastal", "keywords": ["beach", "ocean"]}
        "luxury beachfront resort" -> {"property_type": "luxury beach", "keywords": ["luxury", "beach"]}
        "budget city hotel" -> {"property_type": "budget city", "keywords": ["budget", "city"]}
        "romantic getaway" -> {"property_type": "romantic", "keywords": ["romantic", "couples"]}
    """
    try:
        llm = get_llm()
        
        location_context = f"\nDESTINATION: {location}" if location else ""
        
        prompt = f"""Extract property preferences and characteristics from this query.{location_context}

USER QUERY: "{query}"

Return ONLY valid JSON with this exact format:
{{
  "property_type": "<coastal|city|cultural|luxury|budget|family|romantic|business|adventure|null>",
  "keywords": [<list of relevant preference keywords>],
  "preferences_text": "<natural language summary of preferences>",
  "confidence": "<high|medium|low>"
}}

PROPERTY TYPE MAPPING:
- "coastal", "down south","beach", "beachfront", "seaside", "ocean" -> "coastal"
- "city", "urban", "downtown", "business district" -> "city"  
- "cultural", "heritage", "historical", "traditional" -> "cultural"
- "luxury", "premium", "high-end", "5-star" -> "luxury"
- "budget", "affordable", "cheap", "value" -> "budget"
- "family", "kids", "children" -> "family"
- "romantic", "honeymoon", "couples", "anniversary" -> "romantic"
- "business", "corporate", "meetings", "conference" -> "business"
- "adventure", "activities", "nature", "wildlife" -> "adventure"

EXAMPLES:
- "something coastal" -> {{"property_type": "coastal", "keywords": ["coastal", "beach"], "preferences_text": "coastal property", "confidence": "high"}}
- "luxury beachfront" -> {{"property_type": "luxury", "keywords": ["luxury", "beachfront", "upscale"], "preferences_text": "luxury beachfront resort", "confidence": "high"}}
- "budget city hotel" -> {{"property_type": "budget", "keywords": ["budget", "city", "affordable"], "preferences_text": "budget-friendly city hotel", "confidence": "high"}}
- No preferences mentioned -> {{"property_type": null, "keywords": [], "preferences_text": "", "confidence": "low"}}
"""
        
        response = llm.invoke(prompt)
        response_text = response.content if hasattr(response, "content") else str(response)
        
        # Extract JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            result = json.loads(json_match.group(0))
            return result
        
        return {"property_type": None, "keywords": [], "preferences_text": "", "confidence": "low"}
        
    except Exception as e:
        print(f"Error extracting property preferences: {e}")
        return {"property_type": None, "keywords": [], "preferences_text": "", "confidence": "low"}


def extract_travel_dates_nlp(query: str, conversation_context: str = "") -> Dict:
    """
    Extract travel dates from natural language
    
    Examples:
        "next weekend" -> calculates actual dates
        "in December" -> {"month": "December", "year": 2025}
        "Oct 15-18" -> {"check_in": "2025-10-15", "check_out": "2025-10-18"}
        "3 nights starting Friday" -> calculates dates
    """
    try:
        from datetime import datetime
        llm = get_llm()
        
        today = datetime.now()
        
        prompt = f"""Extract travel dates from the user's query. Today is {today.strftime('%A, %B %d, %Y')}.

USER QUERY: "{query}"
CONVERSATION CONTEXT: "{conversation_context}"

Return ONLY valid JSON with this exact format:
{{
  "check_in": "<YYYY-MM-DD or null>",
  "check_out": "<YYYY-MM-DD or null>",
  "duration": <number of nights or null>,
  "timeframe": "<specific timeframe like 'December 2025' or 'next month' or null>",
  "confidence": "<high|medium|low>"
}}

RULES:
- Convert relative dates to absolute dates (YYYY-MM-DD format)
- "next weekend" = upcoming Saturday-Sunday
- "this weekend" = current Saturday-Sunday (if before Saturday) or next weekend (if after Saturday)
- "next week" = 7 days from today
- Month names without year assume current year if month hasn't passed, otherwise next year
- If only duration mentioned (e.g., "3 nights"), set duration but leave dates null
- If no date info found, return all null values

EXAMPLES:
- "next weekend" (today is Thursday Oct 10) -> {{"check_in": "2025-10-11", "check_out": "2025-10-12", "duration": 1, "timeframe": "weekend", "confidence": "high"}}
- "in December" -> {{"check_in": null, "check_out": null, "duration": null, "timeframe": "December 2025", "confidence": "medium"}}
- "3 nights" -> {{"check_in": null, "check_out": null, "duration": 3, "timeframe": null, "confidence": "medium"}}
"""
        
        response = llm.invoke(prompt)
        response_text = response.content if hasattr(response, "content") else str(response)
        
        # Extract JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            result = json.loads(json_match.group(0))
            return result
        
        return {"check_in": None, "check_out": None, "duration": None, "timeframe": None, "confidence": "low"}
        
    except Exception as e:
        print(f"Error extracting travel dates: {e}")
        return {"check_in": None, "check_out": None, "duration": None, "timeframe": None, "confidence": "low"}


def extract_budget_nlp(query: str) -> Dict:
    """
    Extract budget information from natural language
    
    Examples:
        "$700" -> {"budget_min": 600, "budget_max": 800, "total_budget": 700}
        "$300-500" -> {"budget_min": 300, "budget_max": 500}
        "under $400" -> {"budget_min": 0, "budget_max": 400}
        "around $250 per night" -> {"budget_min": 200, "budget_max": 300}
        "budget is $1000 for 3 nights" -> {"budget_min": 300, "budget_max": 350, "total_budget": 1000}
    """
    try:
        llm = get_llm()
        
        prompt = f"""Extract budget information from the user's query.

USER QUERY: "{query}"

Return ONLY valid JSON with this exact format:
{{
  "budget_min": <minimum budget per night in USD, integer>,
  "budget_max": <maximum budget per night in USD, integer>,
  "total_budget": <total trip budget if mentioned, integer or null>,
  "budget_type": "<per_night|total|null>",
  "confidence": "<high|medium|low>"
}}

RULES:
- If single value WITHOUT "around" (e.g., "my budget is $700", "$700"), treat as MAXIMUM: min = 0, max = value
- If explicit range given (e.g., "$300-500"), use exact values
- "under X" or "below X" -> min: 0, max: X
- "above X" or "over X" or "at least X" -> min: X, max: X * 2
- "around X" -> min: X * 0.8, max: X * 1.2 (only when "around" is mentioned)
- If "per night" mentioned explicitly, budget_type = "per_night"
- If "total" or "for X nights" mentioned, budget_type = "total", calculate per-night range
- If total budget and duration both mentioned, calculate: per_night = total / nights
- Round all values to nearest 10

EXAMPLES:
- "my budget is $700" -> {{"budget_min": 0, "budget_max": 700, "total_budget": 700, "budget_type": "total", "confidence": "high"}}
- "$700" -> {{"budget_min": 0, "budget_max": 700, "total_budget": 700, "budget_type": "total", "confidence": "high"}}
- "$300-500 per night" -> {{"budget_min": 300, "budget_max": 500, "total_budget": null, "budget_type": "per_night", "confidence": "high"}}
- "under $400" -> {{"budget_min": 0, "budget_max": 400, "total_budget": null, "budget_type": null, "confidence": "high"}}
- "around $250" -> {{"budget_min": 200, "budget_max": 300, "total_budget": 250, "budget_type": null, "confidence": "medium"}}
- "at least $500" -> {{"budget_min": 500, "budget_max": 1000, "total_budget": null, "budget_type": null, "confidence": "medium"}}
- "$1000 for 3 nights" -> {{"budget_min": 0, "budget_max": 330, "total_budget": 1000, "budget_type": "total", "confidence": "high"}}
- "budget $600 for 2 nights" -> {{"budget_min": 0, "budget_max": 300, "total_budget": 600, "budget_type": "total", "confidence": "high"}}
"""
        
        response = llm.invoke(prompt)
        response_text = response.content if hasattr(response, "content") else str(response)
        
        # Extract JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            result = json.loads(json_match.group(0))
            return result
        
        return {"budget_min": None, "budget_max": None, "total_budget": None, "budget_type": None, "confidence": "low"}
        
    except Exception as e:
        print(f"Error extracting budget: {e}")
        return {"budget_min": None, "budget_max": None, "total_budget": None, "budget_type": None, "confidence": "low"}


def extract_rooms_needed_nlp(query: str, adults: int = None, children: int = None) -> Dict:
    """
    Extract number of rooms needed from natural language using LLM
    
    Takes into account the number of guests to make intelligent suggestions.
    
    Examples:
        "I need 2 rooms" -> {"rooms": 2, "confidence": "high"}
        "book 3 rooms for us" -> {"rooms": 3, "confidence": "high"}
        "just one room" -> {"rooms": 1, "confidence": "high"}
        "separate rooms for the kids" -> {"rooms": 2, "confidence": "medium"} (if 1 adult + 2 children)
        "we need separate accommodations" -> {"rooms": 2, "confidence": "medium"}
        "family room" -> {"rooms": 1, "confidence": "high"}
        "a couple of rooms" -> {"rooms": 2, "confidence": "high"}
    
    Args:
        query: User's natural language query
        adults: Number of adults (if known) - helps with intelligent inference
        children: Number of children (if known) - helps with intelligent inference
    """
    try:
        llm = get_llm()
        
        # Build context about guests if available
        guest_context = ""
        if adults is not None:
            guest_context = f"\nGuest context: {adults} adult(s)"
            if children is not None:
                guest_context += f", {children} child(ren)"
        
        prompt = f"""Extract the number of rooms needed from this query.
{guest_context}

USER QUERY: "{query}"

Return ONLY valid JSON with this exact format:
{{
  "rooms": <number of rooms needed, integer, or null if not mentioned>,
  "room_type_hint": <"family", "separate", "adjacent", "connecting", or null>,
  "confidence": <"high", "medium", or "low">
}}

RULES FOR EXTRACTION:
- Look for explicit numbers: "2 rooms", "three rooms", "a couple of rooms"
- "1 room", "one room", "single room", "just one room" = 1 room
- "2 rooms", "two rooms", "couple of rooms" = 2 rooms  
- "separate rooms" = infer based on guest count (2+ rooms)
- "family room" = 1 room (family type)
- "connecting rooms", "adjacent rooms" = 2 rooms
- "separate accommodations" = 2+ rooms
- If no room count mentioned, return {{"rooms": null, "confidence": "low"}}

INTELLIGENT INFERENCE (when explicit count not given):
- If "separate rooms" or "separate accommodations" mentioned:
  * With 1 adult + children = assume 2 rooms
  * With couples (2+ adults) + children = assume 2 rooms
  * Otherwise = 2 rooms
- If "family room" mentioned = 1 room with room_type_hint: "family"

EXAMPLES:
- "I need 2 rooms" -> {{"rooms": 2, "room_type_hint": null, "confidence": "high"}}
- "book me 3 rooms please" -> {{"rooms": 3, "room_type_hint": null, "confidence": "high"}}
- "just one room" -> {{"rooms": 1, "room_type_hint": null, "confidence": "high"}}
- "family room for us" -> {{"rooms": 1, "room_type_hint": "family", "confidence": "high"}}
- "separate rooms for kids" -> {{"rooms": 2, "room_type_hint": "separate", "confidence": "medium"}}
- "couple of rooms" -> {{"rooms": 2, "room_type_hint": null, "confidence": "high"}}
- "connecting rooms please" -> {{"rooms": 2, "room_type_hint": "connecting", "confidence": "high"}}
- "I want to book Cinnamon Grand" -> {{"rooms": null, "room_type_hint": null, "confidence": "low"}}
"""
        
        response = llm.invoke(prompt)
        response_text = response.content if hasattr(response, "content") else str(response)
        
        # Extract JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            result = json.loads(json_match.group(0))
            return result
        
        return {"rooms": None, "room_type_hint": None, "confidence": "low"}
        
    except Exception as e:
        print(f"Error extracting rooms needed: {e}")
        return {"rooms": None, "room_type_hint": None, "confidence": "low"}