import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from datetime import datetime
from typing import Dict, List, Optional

# Use the same import pattern as in reservation_tools.py
from langchain_core.tools import tool

from models import get_llm
from new_reservation.reservation_utils import parse_booking_details
from new_reservation.data_utils import load_metadata
from new_reservation.reservation_tools import (
    get_reservation_state,
    sync_from_session_state,
    sync_to_session_state
)

@tool
def extract_and_jump_to_booking_details(user_query: str) -> str:
    """
    Extract booking information from the user's query and update reservation state,
    skipping directly to the appropriate step in the booking flow.
    
    Args:
        user_query (str): The user's initial query that might contain booking details
        
    Returns:
        str: Response message with next steps
    """
    # Sync with session state
    sync_from_session_state()
    reservation_state = get_reservation_state()
    
    # Extract structured booking details using LLM
    parsed_info = extract_booking_details_llm(user_query)
    print(f"LLM parsed booking details: {parsed_info}")
    
    # Extract property/hotel name using LLM
    property_name = extract_property_name(user_query)
    print(f"Extracted property name: {property_name}")
    # Extract location (Sri Lanka or Maldives)
    location = extract_location(user_query)
    print(f"Extracted location: {location}")
    # Update reservation state with extracted information
    if location:
        reservation_state["location"] = location
        
    if property_name:
        # Validate property exists in our data
        property_data = validate_property(property_name, location)
        
        if property_data:
            reservation_state["property"] = property_data["Name"]
            reservation_state["property_type"] = property_data["Type"]
            # Also set as recommended property to maintain consistency
            reservation_state["recommended_property"] = property_data["Name"]
            reservation_state["recommended_property_data"] = property_data
    
    # Update with other parsed information from LLM
    if parsed_info.get("check_in"):
        reservation_state["check_in"] = parsed_info["check_in"]
    if parsed_info.get("check_out"):
        reservation_state["check_out"] = parsed_info["check_out"]
    if parsed_info.get("guests"):
        reservation_state["guests"] = parsed_info["guests"]
    if parsed_info.get("children") is not None:
        reservation_state["children"] = parsed_info["children"]
    if parsed_info.get("rooms"):
        reservation_state["rooms_needed"] = parsed_info["rooms"]
    if parsed_info.get("budget_range"):
        reservation_state["budget_range"] = parsed_info["budget_range"]

    # Calculate duration if both dates are available
    if reservation_state.get("check_in") and reservation_state.get("check_out"):
        try:
            check_in_date = datetime.strptime(reservation_state["check_in"], "%Y-%m-%d")
            check_out_date = datetime.strptime(reservation_state["check_out"], "%Y-%m-%d")
            reservation_state["duration"] = (check_out_date - check_in_date).days
        except Exception as e:
            print(f"Error calculating duration: {e}")
    
    # Count how many key details we have to determine the best next step
    details_count = 0
    key_details = {
        "property": property_name is not None,
        "location": location is not None,
        "check_in": reservation_state.get("check_in") is not None,
        "check_out": reservation_state.get("check_out") is not None,
        "guests": reservation_state.get("guests") is not None
    }
    details_count = sum(1 for v in key_details.values() if v)
    

    print(f"Key Details:")
    # Determine which step to jump to based on available information
    if key_details["property"]:
        # If we have property, go to booking details step
        reservation_state["step"] = "booking_details"
    elif key_details["location"]:
        # If we only have location, go to property selection step
        reservation_state["step"] = "property_selection"
    elif details_count >= 2:
        # If we have multiple details but no location/property, start booking process
        reservation_state["step"] = "location"
    else:
        # If we have minimal information, just start fresh
        reservation_state["step"] = "location"
    
    # Sync back to session state
    sync_to_session_state()
    
    # Generate a friendly, personalized response based on what we extracted
    extracted_items = []
    if property_name:
        extracted_items.append(f"🏨 **Property:** {property_name}")
    
    if reservation_state.get("check_in") and reservation_state.get("check_out"):
        extracted_items.append(f"📅 **Dates:** {reservation_state['check_in']} to {reservation_state['check_out']}")
        if reservation_state.get("duration"):
            extracted_items[-1] += f" ({reservation_state['duration']} nights)"
    
    if reservation_state.get("guests"):
        guest_text = f"👥 **Guests:** {reservation_state['guests']} adults"
        if reservation_state.get("children", 0) > 0:
            guest_text += f", {reservation_state['children']} children"
        extracted_items.append(guest_text)
    
    if reservation_state.get("rooms_needed", 1) > 1:
        extracted_items.append(f"�️ **Rooms:** {reservation_state['rooms_needed']}")
    
    if reservation_state.get("budget_range"):
        extracted_items.append(f"� **Budget:** ${reservation_state['budget_range'][0]}-${reservation_state['budget_range'][1]} per night")
    
    if extracted_items:
        extracted_info = "\n".join(extracted_items)
        
        if property_name and (reservation_state.get("check_in") and reservation_state.get("check_out") and reservation_state.get("guests")):
            # Most complete information
            return f"""Great! I've extracted your booking preferences:

{extracted_info}

You can now fill in any additional details using the form, or tell me more about what you're looking for!"""
        
        elif property_name:
            # We have property but missing other key details
            missing_details = []
            if not reservation_state.get("check_in") or not reservation_state.get("check_out"):
                missing_details.append("📅 When would you like to check in and check out?")
            if not reservation_state.get("guests"):
                missing_details.append("👥 How many guests will be staying?")
            
            return f"""I see you're interested in **{property_name}**! 

Here's what I have so far:
{extracted_info}

To proceed with your booking, I just need a few more details:
{chr(10).join(missing_details)}

You can provide this information in the form above or simply tell me in chat!"""
        
        elif location:
            # We only have location
            return f"""I see you're interested in visiting {location}! 

{extracted_info if len(extracted_items) > 1 else ''}

Tell me more about what you're looking for in a property:
• Are you looking for a beach resort, city hotel, or cultural experience?
• What's your preferred budget range?
• Any specific amenities or experiences you're seeking?

This will help me recommend the perfect property for your stay!"""
        
        else:
            # We have some booking details but no location or property
            return f"""I see you're looking to make a reservation! 

Here's what I have so far:
{extracted_info}

To get started, I just need to know:
🌎 Where would you like to stay - Sri Lanka or Maldives?

Once you let me know your destination, I can help find the perfect property for your stay!"""
    else:
        # We couldn't extract meaningful information
        return """I'd be happy to help you make a reservation! 

To get started, please let me know:
🌎 Where would you like to stay - Sri Lanka or Maldives?
📅 What are your travel dates?
👥 How many guests will be staying?

You can also tell me if you have a specific Cinnamon property in mind!"""


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