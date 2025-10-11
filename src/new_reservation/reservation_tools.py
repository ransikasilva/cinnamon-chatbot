import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import streamlit as st
from langchain_core.tools import tool

from models import get_llm
from new_reservation.data_utils import check_room_availability, load_metadata
from new_reservation.reservation_utils import (
    calculate_total_cost,
    filter_hotels_by_location_and_type,
    parse_booking_details,
    extract_property_name,
    extract_booking_details_llm,
    extract_location,
    validate_property,
    extract_guest_count_nlp,
    extract_property_preferences_nlp,
    extract_travel_dates_nlp,
    extract_budget_nlp,
)

# Global reservation state that syncs with session state
_global_reservation_state = {
    "step": None,
    "location": None,  # Sri Lanka or Maldives
    "property_type": None,
    "property": None,  # Selected hotel name
    "recommended_property": None,  # LLM recommended property
    "recommended_property_data": None,  # Full hotel data for recommendation
    "check_in": None,
    "check_out": None,
    "duration": None,
    "guests": None,
    "children": 0,  # Number of children
    "rooms_needed": 1,
    "budget_range": [100, 500],  # [min, max] in USD per night
    "room_type": None,
    "meal_type": None,  # breakfast, half board, full board, all inclusive
    "total_cost": 0,
    "preferences": {},
    "confirmation_details": {},
}


def sync_to_session_state():
    """Sync global reservation state to Streamlit session state"""
    global _global_reservation_state
    try:
        if hasattr(st, "session_state") and "reservation_state" in st.session_state:
            st.session_state.reservation_state.update(_global_reservation_state)
    except:
        pass


def sync_from_session_state():
    """Sync Streamlit session state to global reservation state"""
    global _global_reservation_state
    
    try:
        if hasattr(st, "session_state") and "reservation_state" in st.session_state:
            _global_reservation_state.update(st.session_state.reservation_state)
    except:
        pass


def get_reservation_state():
    """Get reservation state (global version that works in tools)"""
    global _global_reservation_state
    return _global_reservation_state


@tool
def process_reservation_query(user_query: str) -> str:
    """
    Universal query processor that handles ANY user input related to reservations.
    This is the PRIMARY tool for processing conversational booking queries.
    
    Intelligently extracts ALL available information from natural language:
    - Destination (Sri Lanka or Maldives)
    - Guest count (solo, couple, family, specific numbers)
    - Property preferences (coastal, luxury, budget, city, etc.)
    - Travel dates (next weekend, in December, specific dates)
    - Budget hints
    
    Updates reservation state dynamically and provides contextual next steps.
    
    ✅ USE THIS TOOL FOR:
    - Conversational queries: "I'm a solo traveler planning a trip to Sri Lanka"
    - Partial information: "Something coastal for next weekend"
    - Updates: "Actually make it 2 people" or "I prefer luxury hotels"
    - Exploratory: "Help me plan my trip to Maldives"
    - ANY booking-related user input that doesn't fit rigid tool parameters
    
    ❌ DO NOT USE FOR:
    - Pure information queries with no booking intent (use get_information)
    - Final confirmations (use confirm_final_reservation)
    - Room/meal selection from presented options (use select_room_type, select_meal_plan)
    
    Args:
        user_query: User's natural language input about their reservation
        
    Returns:
        str: Contextual response with next steps based on collected information
    """
    sync_from_session_state()
    reservation_state = get_reservation_state()
    
    print(f"🔍 DEBUG: process_reservation_query called with: '{user_query}'")
    
    # Store original query for context
    original_query = user_query
    
    # Extract all possible information from the query
    extracted_info = {}
    
    # 1. Extract location (Sri Lanka or Maldives)
    location = extract_location(user_query)
    if location:
        extracted_info['location'] = location
        reservation_state['location'] = location
        print(f"✓ Extracted location: {location}")
    
    # 2. Extract guest count using NLP
    guest_info = extract_guest_count_nlp(user_query)
    if guest_info.get('adults') is not None and guest_info.get('confidence') in ['high', 'medium']:
        extracted_info['guests'] = guest_info['adults']
        extracted_info['children'] = guest_info.get('children', 0)
        reservation_state['guests'] = guest_info['adults']
        reservation_state['children'] = guest_info.get('children', 0)
        print(f"✓ Extracted guests: {guest_info['adults']} adults, {guest_info.get('children', 0)} children")
    
    # 3. Extract property preferences
    current_location = reservation_state.get('location')
    preferences_info = extract_property_preferences_nlp(user_query, current_location)
    if preferences_info.get('property_type') and preferences_info.get('confidence') in ['high', 'medium']:
        extracted_info['property_type'] = preferences_info['property_type']
        extracted_info['preferences'] = {
            'keywords': preferences_info.get('keywords', []),
            'description': preferences_info.get('preferences_text', '')
        }
        reservation_state['property_type'] = preferences_info['property_type']
        reservation_state['preferences'].update(extracted_info['preferences'])
        print(f"✓ Extracted preferences: {preferences_info['property_type']} - {preferences_info.get('keywords', [])}")
    
    # 4. Extract travel dates
    date_info = extract_travel_dates_nlp(user_query)
    if date_info.get('check_in') and date_info.get('confidence') in ['high', 'medium']:
        extracted_info['check_in'] = date_info['check_in']
        extracted_info['check_out'] = date_info['check_out']
        reservation_state['check_in'] = date_info['check_in']
        reservation_state['check_out'] = date_info['check_out']
        if date_info.get('duration'):
            reservation_state['duration'] = date_info['duration']
            extracted_info['duration'] = date_info['duration']
        print(f"✓ Extracted dates: {date_info['check_in']} to {date_info['check_out']}")
    elif date_info.get('duration'):
        # Duration mentioned without specific dates
        extracted_info['duration'] = date_info['duration']
        reservation_state['duration'] = date_info['duration']
        print(f"✓ Extracted duration: {date_info['duration']} nights")
    elif date_info.get('timeframe'):
        extracted_info['timeframe'] = date_info['timeframe']
        print(f"✓ Extracted timeframe: {date_info['timeframe']}")
    
    # 5. Extract budget
    budget_info = extract_budget_nlp(user_query)
    if budget_info.get('budget_min') is not None and budget_info.get('confidence') in ['high', 'medium']:
        extracted_info['budget_min'] = budget_info['budget_min']
        extracted_info['budget_max'] = budget_info['budget_max']
        reservation_state['budget_range'] = [budget_info['budget_min'], budget_info['budget_max']]
        
        # If total budget was given, store it for reference
        if budget_info.get('total_budget'):
            extracted_info['total_budget'] = budget_info['total_budget']
            
        print(f"✓ Extracted budget: ${budget_info['budget_min']}-${budget_info['budget_max']} per night")
    
    # 6. Try to extract property name (in case user mentions specific hotel)
    property_name = extract_property_name(user_query)
    if property_name:
        property_data = validate_property(property_name, reservation_state.get('location'))
        if property_data:
            extracted_info['property'] = property_data['Name']
            reservation_state['property'] = property_data['Name']
            reservation_state['recommended_property'] = property_data['Name']
            reservation_state['recommended_property_data'] = property_data
            print(f"✓ Extracted property: {property_data['Name']}")
    
    # Sync updated state
    sync_to_session_state()
    
    # Build contextual response based on what we have and what we need
    return build_contextual_response(reservation_state, extracted_info, original_query)


def build_contextual_response(reservation_state: Dict, extracted_info: Dict, original_query: str) -> str:
    """
    Build a contextual response based on current reservation state and newly extracted information
    """
    # What do we have now?
    has_location = reservation_state.get('location') is not None
    has_guests = reservation_state.get('guests') is not None
    has_preferences = bool(reservation_state.get('property_type') or reservation_state.get('preferences', {}).get('keywords'))
    has_dates = reservation_state.get('check_in') is not None
    has_property = reservation_state.get('property') is not None
    
    # Acknowledge what was just extracted
    acknowledgment = ""
    if extracted_info:
        acknowledgment = "Perfect! "
        extracted_items = []
        
        if 'location' in extracted_info:
            extracted_items.append(f"**{extracted_info['location']}**")
        
        if 'guests' in extracted_info:
            guest_text = f"**{extracted_info['guests']} guest" + ("s" if extracted_info['guests'] > 1 else "") + "**"
            if extracted_info.get('children', 0) > 0:
                guest_text += f" and **{extracted_info['children']} child" + ("ren" if extracted_info['children'] > 1 else "") + "**"
            extracted_items.append(guest_text)
        
        if 'property_type' in extracted_info or 'preferences' in extracted_info:
            pref_desc = extracted_info.get('preferences', {}).get('description', extracted_info.get('property_type', ''))
            if pref_desc:
                extracted_items.append(f"**{pref_desc}**")
        
        if 'check_in' in extracted_info:
            extracted_items.append(f"**{extracted_info['check_in']} to {extracted_info['check_out']}**")
        elif 'duration' in extracted_info:
            extracted_items.append(f"**{extracted_info['duration']} nights**")
        elif 'timeframe' in extracted_info:
            extracted_items.append(f"**{extracted_info['timeframe']}**")
        
        if 'budget_min' in extracted_info:
            extracted_items.append(f"**${extracted_info['budget_min']}-${extracted_info['budget_max']} per night**")
        
        if 'property' in extracted_info:
            extracted_items.append(f"**{extracted_info['property']}**")
        
        if extracted_items:
            acknowledgment += "I've got: " + ", ".join(extracted_items) + ". "
    
    # Determine next step based on what we have
    response = acknowledgment
    
    # SCENARIO 1: We have a specific property - move toward booking details
    if has_property:
        if has_dates and has_guests:
            # Ready to check availability
            reservation_state['step'] = 'availability_check'
            sync_to_session_state()
            response += f"\n\nLet me check availability at **{reservation_state['property']}** for your dates!"
            
            # Auto-trigger availability check
            try:
                from new_reservation.reservation_tools import check_availability_and_show_rooms
                availability_result = check_availability_and_show_rooms("proceed")
                return response + "\n\n" + availability_result
            except Exception as e:
                print(f"Error auto-checking availability: {e}")
                return response
        else:
            # Need dates or guests
            reservation_state['step'] = 'booking_details'
            sync_to_session_state()
            missing = []
            if not has_dates:
                missing.append("📅 **travel dates**")
            if not has_guests:
                missing.append("👥 **number of guests**")
            
            response += f"\n\nGreat choice on **{reservation_state['property']}**! To proceed, I need: {' and '.join(missing)}."
            return response
    
    # SCENARIO 2: We have location + preferences - recommend property
    if has_location and has_preferences:
        # Build preference description for AI selection
        pref_keywords = reservation_state.get('preferences', {}).get('keywords', [])
        property_type = reservation_state.get('property_type', '')
        
        preference_desc = f"{property_type} property"
        if pref_keywords:
            preference_desc += f" with {', '.join(pref_keywords)}"
        
        response += f"\n\nLet me find the perfect {preference_desc} in **{reservation_state['location']}** for you!\n\n"
        
        # Call select_property_with_ai
        try:
            from new_reservation.reservation_tools import select_property_with_ai
            property_result = select_property_with_ai(preference_desc)
            return response + property_result
        except Exception as e:
            print(f"Error calling select_property_with_ai: {e}")
            return response + f"I'll help you find the perfect property. What specific features are most important to you?"
    
    # SCENARIO 3: We have location but no preferences - ask for preferences
    if has_location and not has_preferences:
        reservation_state['step'] = 'property_selection'
        sync_to_session_state()
        
        response += f"\n\nWonderful! **{reservation_state['location']}** is an amazing destination! 🌴\n\n"
        response += "To find your perfect property, tell me more about what you're looking for:\n\n"
        response += "• **Beach relaxation** or **city exploration**?\n"
        response += "• **Luxury resort** or **budget-friendly** accommodation?\n"
        response += "• Any specific features or amenities you'd like?\n\n"
        response += "Or simply describe your ideal vacation and I'll find the perfect match!"
        
        return response
    
    # SCENARIO 4: No location - ask for destination
    if not has_location:
        reservation_state['step'] = 'location'
        sync_to_session_state()
        
        response += "\n\nI'd love to help you plan your trip! 🌍\n\n"
        response += "First, which destination are you interested in?\n\n"
        response += "🇱🇰 **Sri Lanka** - Beaches, culture, and diverse experiences\n"
        response += "🏝️ **Maldives** - Luxury island resorts and crystal waters\n\n"
        response += "Let me know and I'll help you find the perfect property!"
        
        return response
    
    # FALLBACK: Generic helpful response
    reservation_state['step'] = 'property_selection'
    sync_to_session_state()
    response += "\n\nI'm here to help you plan the perfect trip! What would you like to know more about?"
    return response


@tool
def start_reservation_process() -> str:
    """Starts the new reservation/booking process"""
    sync_from_session_state()
    reservation_state = get_reservation_state()

    # Initialize reservation state for new flow
    reservation_state.update(
        {
            "step": "location",
            "location": None,
            "property_type": None,
            "property": None,
            "recommended_property": None,
            "recommended_property_data": None,
            "check_in": None,
            "check_out": None,
            "duration": None,
            "guests": None,
            "children": 0,
            "rooms_needed": 1,
            "budget_range": [100, 500],
            "room_type": None,
            "meal_type": None,
            "total_cost": 0,
            "preferences": {},
            "confirmation_details": {},
        }
    )

    sync_to_session_state()

    return f"""
Let's start with the most important decision - your destination:
<div>
<h4>Sri Lanka </h4> <p>Beautiful island with diverse experiences
   • Pristine beaches in Bentota and Beruwala
   • Vibrant city life in Colombo
   • Cultural heritage and wildlife experiences
   </p>
\n\n
<img src="https://images.unsplash.com/photo-1566296314736-6eaac1ca0cb9?q=80&w=1528&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" width="300" height="200" style=" border: 3px solid #ddd; border-radius: 10px; padding: 5px;">

</div>

<h4>Maldives</h4> <p>Tropical paradise with luxury resorts
   • Crystal clear waters and overwater villas
   • World-class diving and snorkeling
   • Ultimate relaxation and romance
   </p>

\n\n

<img src="https://images.unsplash.com/photo-1573843981267-be1999ff37cd?q=80&w=1374&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" width="300" height="200" style=" border: 3px solid #ddd; border-radius: 10px; padding: 5px;">

\n\n

Which destination calls to your heart? You can choose using the buttons above or simply tell me!"""


@tool
def set_destination_preference(destination: str) -> str:
    """Set the user's preferred destination (Sri Lanka or Maldives)"""
    print(f"DEBUG:Tool Input: {destination}")
    sync_from_session_state()
    reservation_state = get_reservation_state()

    # if reservation_state["step"] != "location":
    #     return "Let me help you start fresh. Please tell me which destination interests you."

    destination_clean = destination.strip().title()

    if "sri lanka" in destination.lower():
        destination_clean = "Sri Lanka"
    elif "maldives" in destination.lower():
        destination_clean = "Maldives"

    reservation_state["location"] = destination_clean
    reservation_state["step"] = "property_selection"
    sync_to_session_state()

    return f"""Excellent choice! 🎉 **{destination_clean}** is absolutely stunning!

Now, tell me about your dream {destination_clean} experience! What are you looking for?

For example:
• *"Luxury beachfront resort for honeymoon"*
• *"Family-friendly hotel with kids activities"*  
• *"Business hotel in the city center"*
• *"Cultural experience near heritage sites"*
• *"Budget-friendly beach vacation"*
• *"Overwater villa for romantic getaway"*

Describe your perfect vacation and I'll find the ideal property for you! ✨"""


@tool
def select_property_with_ai(user_preferences: str) -> str:
    """
    Use intelligent property selection with clarifying questions when needed.
    
    Automatically extracts location (Sri Lanka or Maldives) from user_preferences if not already set.
    
    Args:
        user_preferences: User's description of their ideal property/vacation
        
    Returns:
        str: Property recommendations or request for more information
    """

    sync_from_session_state()
    reservation_state = get_reservation_state()

    location = reservation_state.get("location")
    
    # If location is not set, try to extract it from user preferences
    if not location:
        extracted_location = extract_location(user_preferences)
        
        if extracted_location:
            # Location found in the query - set it automatically
            location = extracted_location
            reservation_state["location"] = location
            reservation_state["step"] = "property_selection"
            sync_to_session_state()
        else:
            # Location not found - ask user to specify
            return """I'd love to help you find the perfect property! 

To give you the best recommendations, could you let me know which destination you're interested in?
• **Sri Lanka** - Beach resorts, city hotels, and cultural experiences
• **Maldives** - Luxury island resorts and overwater villas

You can simply say "Sri Lanka" or "Maldives", or describe what you're looking for!"""

    # Load hotel data
    try:
        metadata = load_metadata()
        hotels_data = metadata.get("HotelsAndResorts", [])
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return "I'm sorry, I encountered an error loading hotel information. Please try again."

    # Filter hotels by location
    filtered_hotels = filter_hotels_by_location_and_type(hotels_data, location)

    if not filtered_hotels:
        return f"I'm sorry, no properties are available for {location} at the moment."

    return perform_llm_selection(
        filtered_hotels, location, user_preferences, reservation_state
    )


def perform_llm_selection(
    location_hotels, location, user_preferences, reservation_state
):
    """Perform intelligent LLM selection - handle both single and multiple hotel recommendations in one flow"""
    from models import get_llm

    # Prepare detailed hotel information for LLM
    hotels_info = []
    for i, hotel in enumerate(location_hotels, 1):
        hotel_info = f"""
Hotel {i}: {hotel.get('Name', '')}
Type: {hotel.get('Type', '')}
Location: {hotel.get('Location', '')}
Description: {hotel.get('UniqueDescription', '')}
"""
        hotels_info.append(hotel_info)

    # Create LLM prompt for intelligent analysis
    analysis_prompt = f"""You are an expert hotel concierge. Analyze user preferences and recommend the best matching hotels.

USER'S DESTINATION: {location}
USER'S PREFERENCES: "{user_preferences}"

AVAILABLE HOTELS:
{chr(10).join(hotels_info)}

TASK: Recommend 1-3 hotels that best match the user preferences, with reasons for each.

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "recommended_hotels": [list of hotel names that match well],
    "reasoning": "Brief explanation written directly to the user about why these hotels were selected. Write as if speaking to the user directly (avoid saying 'user's preference' - instead say 'your preferences' or be more direct)",
    "individual_reasons": {{
        "Hotel Name 1": ["Reason 1", "Reason 2"],
        "Hotel Name 2": ["Reason 1", "Reason 2"]
    }}
}}

GUIDELINES:
- Recommend 1 hotel if preferences are very specific (exact location, unique features, clear budget tier)
- Recommend 2-3 hotels if preferences are general (just "luxury", "beach", "family-friendly") 
- Focus on hotels that genuinely match the stated preferences
- Provide compelling, specific reasons for each hotel
- If only 1 hotel matches well, only recommend that one
- Write reasoning as if speaking directly to the user (e.g., "Based on your interest in luxury accommodations..." instead of "These hotels align with the user's preference...")

RESPOND ONLY WITH VALID JSON, NO OTHER TEXT."""

    try:
        llm = get_llm()
        response = llm.invoke(analysis_prompt)
        response_text = (
            response.content if hasattr(response, "content") else str(response)
        )

        # Parse JSON response
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        json_str = response_text[json_start:json_end]

        analysis = json.loads(json_str)
        selected_hotel_names = analysis.get("recommended_hotels", [])
        reasoning = analysis.get("reasoning", "")
        individual_reasons = analysis.get("individual_reasons", {})

        # Find matching hotel objects
        matching_hotels = []
        for hotel_name in selected_hotel_names:
            for hotel in location_hotels:
                if (
                    hotel_name.lower() in hotel.get("Name", "").lower()
                    or hotel.get("Name", "").lower() in hotel_name.lower()
                ):
                    matching_hotels.append(hotel)
                    break

        # Fallback if no matches found
        if not matching_hotels:
            matching_hotels = [location_hotels[0]]

        # Store all recommendations in the same format - always use property_confirmation step
        if len(matching_hotels) == 1:
            # Single recommendation
            selected_hotel = matching_hotels[0]
            hotel_name = selected_hotel["Name"]
            reasons = individual_reasons.get(
                hotel_name,
                [
                    "🏨 Perfectly matches your preferences",
                    "✨ Excellent choice for your getaway",
                ],
            )

            reservation_state["recommended_property"] = hotel_name
            reservation_state["recommended_property_data"] = selected_hotel
            reservation_state["recommended_hotels"] = (
                matching_hotels  # Store for alternatives
            )
            reservation_state["step"] = "property_confirmation"
            sync_to_session_state()

            return f"""🎉 **Perfect match found!** Based on your preferences:

**{hotel_name}**
📍 {selected_hotel.get('Location', '')}

{selected_hotel.get('UniqueDescription', '')}

✨ **Why this property is perfect for you:**
{chr(10).join(['• ' + reason for reason in reasons])}

"""
        #  **What would you like to do?**
        # • Say *"Yes, let's book this"* to continue with this recommendation
        # • Say *"Show me alternatives"* to see other options"""

        else:
            # Multiple recommendations - stay in property_selection until user picks one
            reservation_state["recommended_hotels"] = matching_hotels
            reservation_state["step"] = "property_selection"  # Keep in selection mode
            sync_to_session_state()

            response_text = f"""🏨 **Excellent options!** I found {len(matching_hotels)} properties that match your preferences:

{reasoning}

"""

            for i, hotel in enumerate(matching_hotels, 1):
                hotel_name = hotel["Name"]
                reasons = individual_reasons.get(
                    hotel_name, ["Great match for your preferences"]
                )

                response_text += f"""**{i}. {hotel_name}**
📍 {hotel.get('Location', '')}
{hotel.get('UniqueDescription', '')}

✨ **Why this works for you:**
{chr(10).join(['• ' + reason for reason in reasons])}

"""

            response_text += """**Ready to choose?**
• **Select by number or name** (e.g., "1" or "Cinnamon Grand")
• Say *"Tell me more about [hotel name]"* for details
• Say *"Show me all alternatives"* for complete list"""

            return response_text

    except Exception as e:
        print(f"Error in LLM selection analysis: {e}")
        # Fallback to single hotel selection
        selected_hotel = location_hotels[0]
        reservation_state["recommended_property"] = selected_hotel["Name"]
        reservation_state["recommended_property_data"] = selected_hotel
        reservation_state["recommended_hotels"] = [selected_hotel]
        reservation_state["step"] = "property_confirmation"
        sync_to_session_state()

        return f"""🎉 I recommend **{selected_hotel['Name']}** for your {location} getaway!

📍 {selected_hotel.get('Location', '')}
{selected_hotel.get('UniqueDescription', '')}

**What would you like to do?**
• Say *"Yes, let's book this"* to continue with this recommendation  
• Say *"Show me alternatives"* to see other options"""


@tool
def show_property_alternatives() -> str:
    """Show all available properties when user requests alternatives to the current recommendation"""
    sync_from_session_state()
    reservation_state = get_reservation_state()

    if reservation_state["step"] not in ["property_confirmation", "property_selection"]:
        return "Please wait for a property recommendation first."

    location = reservation_state.get("location")
    if not location:
        return "Please select your destination first."

    try:
        # Load hotel data
        metadata = load_metadata()

        hotels_data = metadata.get("HotelsAndResorts", [])
        price_mapping = metadata.get("PriceMapping", {})

        # Filter by location using the existing function
        location_hotels = filter_hotels_by_location_and_type(hotels_data, location)

        if not location_hotels:
            return (
                f"I'm sorry, no properties are available for {location} at the moment."
            )

        # Store all location hotels for future selection
        reservation_state["all_location_hotels"] = location_hotels
        reservation_state["step"] = "property_selection"  # Set to selection mode
        sync_to_session_state()

        # Create alternatives list
        alternatives_text = f"Here are all our available properties in {location}:\n\n"

        for i, hotel in enumerate(location_hotels, 1):
            room_types = hotel.get("RoomTypes", [])
            if room_types:
                prices = [
                    price_mapping.get(room.get("Price", ""), 0) for room in room_types
                ]
                valid_prices = [p for p in prices if p > 0]
                if valid_prices:
                    price_range = f"${min(valid_prices)}-${max(valid_prices)}/night"
                else:
                    price_range = "Contact for pricing"
            else:
                price_range = "Contact for pricing"

            alternatives_text += f"""**{i}. {hotel.get('Name', '')}**
📍 {hotel.get('Location', '')}
💰 {price_range}
{hotel.get('UniqueDescription', '')}

"""

        alternatives_text += """Please tell me:
• **Which property interests you most?** (by number or name)
• **What specific features** you're looking for
• **Your budget preference** or any other requirements

I'll help you select the perfect property for your stay!"""

        return alternatives_text

    except Exception as e:
        print(f"Error loading alternatives: {e}")
        return "I'm sorry, I encountered an error loading the available properties. Please try again."


@tool
def confirm_property_selection(hotel_name: str) -> str:
    """
    Confirm and proceed with booking for a selected hotel property.
    
    IMPORTANT - LLM MUST PROVIDE THE COMPLETE, EXACT HOTEL NAME:
    
    Before calling this tool, the LLM MUST:
    1. If user says "yes", "book this", "confirm" → Use the currently recommended hotel's exact name
    2. If user provides a number (e.g., "2", "option 1") → Convert to the corresponding hotel name from the list
    3. If user provides partial name (e.g., "Grand") → Match and provide the complete hotel name (e.g., "Cinnamon Grand Colombo")
    4. Search the recommended_hotels, all_location_hotels, or entire database to find the exact match
    
    Args:
        hotel_name: The COMPLETE and EXACT hotel name to book (e.g., "Cinnamon Grand Colombo", "Cinnamon Lakeside Colombo")
                   NOT partial names, NOT numbers, NOT "yes/confirm" - only the full hotel name from the database.
    
    Returns:
        str: Booking confirmation message with next steps
    
    Examples of CORRECT usage:
        User says: "Yes, I'll book it" (single recommendation shown)
        → LLM calls: confirm_property_selection("Cinnamon Grand Colombo")
        
        User says: "I want option 2" (list of 3 hotels shown, #2 is Cinnamon Lakeside)
        → LLM calls: confirm_property_selection("Cinnamon Lakeside Colombo")
        
        User says: "I want to book Cinnamon Grand"
        → LLM calls: confirm_property_selection("Cinnamon Grand Colombo")
        
        User says: "Book the Lakeside hotel"
        → LLM calls: confirm_property_selection("Cinnamon Lakeside Colombo")
    
    Examples of INCORRECT usage (DO NOT DO THIS):
        ❌ confirm_property_selection("yes")
        ❌ confirm_property_selection("2")
        ❌ confirm_property_selection("Grand")
        ❌ confirm_property_selection("book this")
    """
    sync_from_session_state()
    reservation_state = get_reservation_state()

    # Get available hotel lists
    recommended_hotels = reservation_state.get("recommended_hotels", [])
    all_location_hotels = reservation_state.get("all_location_hotels", [])
    current_location = reservation_state.get("location")
    
    # Search for the hotel by exact name match
    hotel_found = None
    
    # 1. Search in recommended hotels first
    if recommended_hotels:
        for hotel in recommended_hotels:
            if hotel.get("Name", "").lower() == hotel_name.lower():
                hotel_found = hotel
                break
    
    # 2. Search in all location hotels
    if not hotel_found and all_location_hotels:
        for hotel in all_location_hotels:
            if hotel.get("Name", "").lower() == hotel_name.lower():
                hotel_found = hotel
                break
    
    # 3. Search entire database as fallback
    if not hotel_found:
        try:
            metadata = load_metadata()
            all_hotels = metadata.get("HotelsAndResorts", [])
            
            for hotel in all_hotels:
                if hotel.get("Name", "").lower() == hotel_name.lower():
                    # Validate location match if location is set
                    if current_location:
                        hotel_location = hotel.get("Location", "")
                        hotel_type = hotel.get("Type", "")
                        
                        if current_location == "Sri Lanka" and "Sri Lanka" in hotel_location and hotel_type != "Maldives":
                            hotel_found = hotel
                            break
                        elif current_location == "Maldives" and (hotel_type == "Maldives" or "Maldives" in hotel_location):
                            hotel_found = hotel
                            break
                    else:
                        # No location constraint
                        hotel_found = hotel
                        break
        except Exception as e:
            print(f"Error searching database: {e}")
    
    # If hotel found, proceed with booking
    if hotel_found:
        # Set location if not already set
        if not reservation_state.get("location"):
            if hotel_found.get("Type") == "Maldives" or "Maldives" in hotel_found.get("Location", ""):
                reservation_state["location"] = "Maldives"
            elif "Sri Lanka" in hotel_found.get("Location", ""):
                reservation_state["location"] = "Sri Lanka"
            sync_to_session_state()
        
        return proceed_with_booking(hotel_found, reservation_state)
    
    # Hotel not found - provide helpful error message
    available_options = []
    if recommended_hotels:
        available_options = [h.get("Name", "") for h in recommended_hotels]
    elif all_location_hotels:
        available_options = [h.get("Name", "") for h in all_location_hotels]
    
    if available_options:
        options_text = "\n".join([f"• {name}" for name in available_options])
        return f"""I couldn't find a hotel with the exact name '{hotel_name}'.

Available options:
{options_text}

Please select one of the above properties."""
    else:
        return f"I couldn't find '{hotel_name}' in our system. Please start the property selection process again or ask to see available properties."


def proceed_with_booking(selected_hotel, reservation_state):
    """Helper function to proceed with booking for a selected hotel"""
    reservation_state["property"] = selected_hotel["Name"]
    reservation_state["recommended_property"] = selected_hotel["Name"]
    reservation_state["recommended_property_data"] = selected_hotel
    reservation_state["step"] = "booking_details"
    # Clear alternatives list since selection is made
    reservation_state["all_location_hotels"] = []
    sync_to_session_state()

    # Build response based on what information we already have
    response = f"Excellent choice! 🎉 **{selected_hotel['Name']}** it is!\n\n"
    
    # Check what information we already have
    has_dates = reservation_state.get('check_in') is not None
    has_timeframe = reservation_state.get('duration') is not None or reservation_state.get('timeframe') is not None
    has_guests = reservation_state.get('guests') is not None
    has_budget = reservation_state.get('budget_range') is not None and reservation_state['budget_range'] != [100, 500]
    
    # Show what we have so far
    confirmed_details = []
    if has_guests:
        guest_text = f"� {reservation_state['guests']} adult" + ("s" if reservation_state['guests'] > 1 else "")
        if reservation_state.get('children', 0) > 0:
            guest_text += f", {reservation_state['children']} child" + ("ren" if reservation_state['children'] > 1 else "")
        confirmed_details.append(guest_text)
    
    if has_dates:
        from datetime import datetime
        check_in_date = datetime.strptime(reservation_state['check_in'], "%Y-%m-%d")
        check_out_date = datetime.strptime(reservation_state['check_out'], "%Y-%m-%d")
        duration = (check_out_date - check_in_date).days
        confirmed_details.append(f"📅 {reservation_state['check_in']} to {reservation_state['check_out']} ({duration} nights)")
    elif has_timeframe:
        if reservation_state.get('duration'):
            confirmed_details.append(f"📅 {reservation_state['duration']} nights")
    
    if has_budget:
        confirmed_details.append(f"💰 ${reservation_state['budget_range'][0]}-${reservation_state['budget_range'][1]} per night")
    
    # Show confirmed details if we have any
    if confirmed_details:
        response += "Here's what I have so far:\n" + "\n".join(confirmed_details) + "\n\n"
    
    # CRITICAL: We need ACTUAL DATES (check_in/check_out) to check availability
    # Duration or timeframe alone is NOT sufficient
    missing_info = []
    
    # Check for actual dates - duration/timeframe is not enough for availability check
    if not has_dates:
        if has_timeframe:
            # We have duration/timeframe but not actual dates
            if reservation_state.get('duration'):
                missing_info.append(f"📅 **Specific dates** for your {reservation_state['duration']} night stay")
            elif reservation_state.get('timeframe'):
                missing_info.append(f"📅 **Specific dates** in {reservation_state.get('timeframe')}")
            else:
                missing_info.append("📅 **Travel dates** (check-in and check-out)")
        else:
            missing_info.append("📅 **Travel dates** (check-in and check-out)")
    
    if not has_guests:
        missing_info.append("👥 **Number of guests** (adults and children)")
    
    if not has_budget:
        missing_info.append("💰 **Budget range** per night")
    
    if missing_info:
        response += "To complete your booking, please provide:\n" + "\n".join(missing_info) + "\n\n"
        
        # Add helpful hint if we have timeframe/duration but need specific dates
        if has_timeframe and not has_dates:
            if reservation_state.get('timeframe'):
                response += f"💡 *Tip: I know you want to travel in {reservation_state.get('timeframe')}, but I need specific check-in and check-out dates to check room availability.*\n\n"
            elif reservation_state.get('duration'):
                response += f"💡 *Tip: I know you want a {reservation_state.get('duration')} night stay, but I need specific check-in and check-out dates to check room availability.*\n\n"
        
        response += "You can use the form above or tell me in the chat!"
    else:
        # We have ALL required info including ACTUAL dates - ready to check availability
        response += "Perfect! I have all the details. Let me check availability for you!"
        reservation_state["step"] = "availability_check"
        sync_to_session_state()
    
    return response



@tool
def check_availability_and_show_rooms(confirmation: str = "proceed") -> str:
    """Check room availability and show options within the user's budget"""
    sync_from_session_state()
    reservation_state = get_reservation_state()

    if reservation_state["step"] != "availability_check":
        return "Please provide your booking details first."

    property_name = reservation_state.get("property")
    if not property_name:
        return "Please select a property first."

    try:
        # Check availability using the hotel data manager
        available_rooms = check_room_availability(
            property_name=property_name,
            check_in=reservation_state["check_in"],
            check_out=reservation_state["check_out"],
            rooms_needed=reservation_state["rooms_needed"],
            budget_min=reservation_state["budget_range"][0],
            budget_max=reservation_state["budget_range"][1],
        )
        # print(f"DEBUG:Available rooms: {available_rooms}")
        if not available_rooms:
            return f"I'm sorry, no rooms are available at {property_name} for your dates. Would you like to try different dates or see alternative properties?"

        #         if not available_rooms:
        #             # Show all available rooms with price indication
        #             room_list = "\n".join([f"• {room['type']} - ${room['price_per_night']}/night" for room in available_rooms])
        #             return f"""No rooms are available within your budget
        # Available rooms at {property_name}:
        # {room_list}

        # Would you like to:
        # • Adjust your budget range
        # • Choose from available rooms
        # • See alternative properties?"""

        reservation_state["step"] = "room_selection"
        reservation_state["available_rooms"] = available_rooms  # Store for later use
        sync_to_session_state()

        rooms_text = f"🏨 **Great news!** Here are available rooms at **{property_name}** within your budget:\n\n"

        for i, room in enumerate(available_rooms, 1):
            rooms_text += f"""**{i}. {room['room_type']}**
💰 ${room['base_rate_per_night']}
📝 {room['description']}

"""

        rooms_text += "Which room type would you prefer? You can choose by number or tell me your preference!"

        return rooms_text

    except Exception as e:
        print(f"Error checking availability: {e}")
        return f"I encountered an issue checking availability. Please try again or contact our reservations team."


@tool
def select_room_type(room_choice: str) -> str:
    """Handle room type selection"""
    sync_from_session_state()
    reservation_state = get_reservation_state()

    if reservation_state["step"] != "room_selection":
        return "Please check room availability first."

    # Find the selected room from available rooms
    available_rooms = reservation_state.get("available_rooms", [])
    selected_room = None

    # Try to match by number first
    import re

    number_match = re.search(r"\b(\d+)\b", room_choice)
    if number_match:
        choice_num = int(number_match.group(1))
        if 1 <= choice_num <= len(available_rooms):
            selected_room = available_rooms[choice_num - 1]

    # If not found by number, try to match by room type name
    if not selected_room:
        for room in available_rooms:
            if room_choice.lower() in room.get("room_type", "").lower():
                selected_room = room
                break

    # Fallback to first room if no match
    if not selected_room and available_rooms:
        selected_room = available_rooms[0]

    if selected_room:
        reservation_state["room_type"] = selected_room["room_type"]
        reservation_state["selected_room_data"] = (
            selected_room  # Store complete room data
        )
        reservation_state["step"] = "meal_selection"
        sync_to_session_state()

        return f"""Excellent choice! 🎉 You've selected: **{selected_room['room_type']}**

💰 Room Rate: ${selected_room['base_rate_per_night']}/night
📝 {selected_room.get('description', '')}

Now, let's choose your meal plan. What dining experience would you prefer?

🍽️ **Available Meal Plans:**

• **Room Only** - Maximum flexibility to explore local dining

• **Breakfast Included** - Start each day with a delicious breakfast (+$25/person/day)

• **Half Board** - Breakfast and dinner included (+$50/person/day)

• **Full Board** - All meals included (+$75/person/day)

• **All Inclusive** - Meals, drinks, and activities included (+$120/person/day)

What sounds perfect for your vacation?"""

    else:
        return "I couldn't find that room type. Please choose from the available options by number or name."


@tool
def select_meal_plan(meal_choice: str) -> str:
    """Handle meal plan selection and calculate total cost"""
    sync_from_session_state()
    reservation_state = get_reservation_state()

    if reservation_state["step"] != "meal_selection":
        return "Please select your room type first."

    reservation_state["meal_type"] = meal_choice
    reservation_state["step"] = "final_confirmation"

    # Calculate total cost using proper calculation
    cost_details = calculate_total_cost(reservation_state)
    reservation_state["total_cost"] = cost_details["total_cost"]
    reservation_state["cost_breakdown"] = cost_details["breakdown"]

    sync_to_session_state()

    # Create detailed cost breakdown
    breakdown = cost_details["breakdown"]
    total_people = breakdown["guests"] + breakdown["children"]

    cost_summary = f"""Perfect! 🌟 Your **{meal_choice}** meal plan is confirmed.

📋 **Reservation Summary:**

🏨 **Hotel:** {reservation_state.get('property')}

📅 **Dates:** {reservation_state.get('check_in')} to {reservation_state.get('check_out')} ({breakdown['duration']} nights)

👥 **Guests:** {breakdown['guests']} adults"""

    if breakdown["children"] > 0:
        cost_summary += f", {breakdown['children']} children"

    cost_summary += f"""
�🛏️ **Rooms:** {breakdown['rooms']} x {reservation_state.get('room_type')}

🍽️ **Meals:** {meal_choice}

💰 **Cost Breakdown:**

 🛏️ **Room Charges:**  \n\n                          
 ${breakdown['room_rate_per_night']}/night × {breakdown['duration']} nights × {breakdown['rooms']} room(s) 
 = ${breakdown['room_cost']:,.2f}    \n\n """

    if breakdown["meal_cost"] > 0:
        cost_summary += f"""                                                
🍽️ **Meal Plan:**     \n\n                          
${breakdown['meal_cost_per_person_per_day']}/person/day × {total_people} guest(s) × {breakdown['duration']} days     
 = ${breakdown['meal_cost']:,.2f}        \n\n                   """

    cost_summary += f"""

**Total Cost: ${cost_details['total_cost']:,.2f}**

Everything looks perfect! Shall I proceed with the final booking confirmation?"""

    return cost_summary


@tool
def confirm_final_reservation(confirmation: str) -> str:
    """Finalize the reservation"""
    sync_from_session_state()
    reservation_state = get_reservation_state()

    if reservation_state["step"] != "final_confirmation":
        return "Please complete all booking steps first."

    if "yes" in confirmation.lower() or "confirm" in confirmation.lower():
        # Generate booking reference
        import random

        booking_ref = f"CN{random.randint(100000, 999999)}"

        reservation_state["confirmation_details"] = {
            "booking_reference": booking_ref,
            "confirmed_at": datetime.now().isoformat(),
        }

        sync_to_session_state()

        return f"""🎉 **BOOKING CONFIRMED!** 

📧 **Booking Reference:** {booking_ref}

✅ **Your Reservation:**
🏨 {reservation_state.get('property')}
📅 {reservation_state.get('check_in')} to {reservation_state.get('check_out')}
👥 {reservation_state.get('guests')} guests
🛏️ {reservation_state.get('room_type')}
🍽️ {reservation_state.get('meal_type')}

💰 **Total Cost:** ${reservation_state.get('total_cost')}

📧 **A confirmation email will be sent to you shortly with all details.**

Thank you for choosing Cinnamon Hotels! We can't wait to welcome you! 🌟

Need any changes or have questions? Just ask!"""

    return "Please confirm if you'd like to finalize this booking by saying 'Yes, confirm' or let me know if you need any changes."


@tool
def get_information(query: str) -> str:
    """
    Get detailed information about hotels, amenities, services, or any hotel-related questions.
    
    Args:
        query (str): User's question about hotels, amenities, locations, facilities, etc.
        
    Returns:
        str: Detailed answer based on hotel metadata
        
    Examples:
        - "What amenities does Cinnamon Grand have?"
        - "Tell me about hotels in Colombo"
        - "What room types are available at Cinnamon Lakeside?"
        - "Which hotels have spa facilities?"
        - "What's the difference between properties in Sri Lanka vs Maldives?"
    """
    try:
        # Load complete hotel metadata
        metadata = load_metadata()
        hotels_data = metadata.get("HotelsAndResorts", [])
        price_mapping = metadata.get("PriceMapping", {})
        
        if not hotels_data:
            return "I'm sorry, I couldn't load hotel information at the moment. Please try again."
        
        # Get current reservation context if available
        sync_from_session_state()
        reservation_state = get_reservation_state()
        current_location = reservation_state.get("location")
        current_property = reservation_state.get("property")
        
        # Prepare comprehensive hotel data for LLM
        hotels_info = []
        for hotel in hotels_data:
            # Get room types with pricing
            room_info = []
            for room in hotel.get("RoomTypes", []):
                price_key = room.get("Price", "")
                price_value = price_mapping.get(price_key, "Contact for pricing")
                room_info.append({
                    "type": room.get("RoomType", ""),
                    "price": price_value,
                    "description": room.get("Description", "")
                })
            
            hotel_info = {
                "name": hotel.get("Name", ""),
                "location": hotel.get("Location", ""),
                "type": hotel.get("Type", ""),
                "description": hotel.get("UniqueDescription", ""),
                "amenities": hotel.get("Amenities", []),
                "dining": hotel.get("DiningOptions", []),
                "activities": hotel.get("Activities", []),
                "room_types": room_info,
                "nearby_attractions": hotel.get("NearbyAttractions", [])
            }
            hotels_info.append(hotel_info)
        
        # Create LLM prompt for hotel information query
        # context_info = ""
        # if current_location:
        #     context_info += f"User is currently interested in: {current_location}\n"
        # if current_property:
        #     context_info += f"User's selected property: {current_property}\n"
        
        info_prompt = f"""You are a knowledgeable hotel concierge at Cinnamon Hotels. Answer the user's question about hotels using the provided data.

USER'S QUESTION: "{query}"

HOTEL DATA:
{json.dumps(hotels_info, indent=2)}

GUIDELINES:
- Provide accurate, helpful information based only on the data provided BUT DO NOT PROVIDE INFO AS IT IS IN THE DATASET.
- Be conversational and friendly, as if speaking to a guest
- If the question is about a specific hotel, focus on that property
- If comparing hotels, highlight key differences
- Include relevant details like pricing, amenities, locations
- If information isn't available in the data, say so honestly
- Format your response nicely with emojis and clear sections
- Keep responses concise but comprehensive DONT PROVIDE INFO AS IT IS IN THE DATASET.

RESPOND DIRECTLY TO THE USER'S QUESTION:"""

        # Get LLM response
        llm = get_llm()
        response = llm.invoke(info_prompt)
        response_text = response.content if hasattr(response, "content") else str(response)
        
        return response_text
        
    except Exception as e:
        print(f"Error in hotel information query: {e}")
        return "I'm sorry, I encountered an error while looking up hotel information. Please try asking again or contact our support team for assistance."
    

@tool
def provide_booking_details(
    property_name: str = None,
    location: str = None,
    check_in: str = None,
    check_out: str = None,
    guests: int = None,
    children: int = None,
    rooms: int = None,
    budget_min: int = None,
    budget_max: int = None
) -> str:
    """
    Provide or update booking details at any point in the reservation process.
    This unified tool handles both initial booking requests and updates to existing bookings.
    
    The LLM should extract booking details from the user's query using conversation context
    and pass them as individual parameters. The tool intelligently determines what to do based
    on the current reservation state and which parameters are provided.
    
    ✅ USE THIS TOOL WHEN USER PROVIDES ANY BOOKING DETAILS:
    - Initial request with property: "I want to book Cinnamon Grand for next weekend"
    - Initial request without property but with details: "Next weekend, 2 adults, budget $300-500" (after property selected)
    - Updating dates: "Actually, make it the weekend after that"
    - Changing guests: "Change it to 3 adults instead"
    - Updating budget: "Increase budget to $500-700"
    - Complete details: "Oct 15-18, 2 adults, 1 child, budget $200-400"
    
    ❌ DO NOT USE THIS TOOL FOR:
    - General booking request without details: "I want to make a booking" (use start_reservation_process)
    - Just asking questions: "What hotels are available?" (use get_information)
    - Property selection without booking details: "I'm looking for a luxury beach resort" (use select_property_with_ai)
    
    Args:
        property_name (str, optional): Full hotel/property name (e.g., "Cinnamon Grand Colombo")
        location (str, optional): Destination - either "Sri Lanka" or "Maldives"
        check_in (str, optional): Check-in date in YYYY-MM-DD format
        check_out (str, optional): Check-out date in YYYY-MM-DD format
        guests (int, optional): Number of adult guests
        children (int, optional): Number of children
        rooms (int, optional): Number of rooms needed
        budget_min (int, optional): Minimum budget per night in USD
        budget_max (int, optional): Maximum budget per night in USD
        
    Returns:
        str: Response message with next steps
    """
    # Sync with session state
    sync_from_session_state()
    reservation_state = get_reservation_state()
    
    print(f"provide_booking_details called with: property={property_name}, location={location}, "
          f"check_in={check_in}, check_out={check_out}, guests={guests}, children={children}, "
          f"rooms={rooms}, budget=({budget_min}, {budget_max})")
    
    # Update reservation state with provided parameters
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
    
    # Update with other provided information
    if check_in:
        reservation_state["check_in"] = check_in
    if check_out:
        reservation_state["check_out"] = check_out
    if guests:
        reservation_state["guests"] = guests
    if children is not None:
        reservation_state["children"] = children
    if rooms:
        reservation_state["rooms_needed"] = rooms
    if budget_min and budget_max:
        reservation_state["budget_range"] = [budget_min, budget_max]

    # Calculate duration if both dates are available
    if reservation_state.get("check_in") and reservation_state.get("check_out"):
        try:
            check_in_date = datetime.strptime(reservation_state["check_in"], "%Y-%m-%d")
            check_out_date = datetime.strptime(reservation_state["check_out"], "%Y-%m-%d")
            reservation_state["duration"] = (check_out_date - check_in_date).days
        except Exception as e:
            print(f"Error calculating duration: {e}")
    
    # Determine which step to jump to based on current state and available information
    current_step = reservation_state.get("step")
    has_property = reservation_state.get("property") is not None
    
    # Check if this is a fresh booking (property just provided in this call)
    property_just_provided = property_name is not None
    
    # If property is already selected or just provided, check if we can proceed to availability
    if has_property:
        # We have a property - check if we have all required booking details
        has_dates = reservation_state.get("check_in") and reservation_state.get("check_out")
        has_guests = reservation_state.get("guests") is not None
        has_budget = reservation_state.get("budget_range") is not None
        
        # Check if children, rooms, or budget were explicitly provided (not just defaults)
        children_provided = children is not None
        rooms_provided = rooms is not None
        budget_provided = budget_min is not None and budget_max is not None
        
        # Only auto-proceed to availability if:
        # 1. We're NOT in initial booking (property just provided) OR
        # 2. User explicitly provided children, rooms, AND budget (all details)
        # 3. AND we have dates and guests
        can_auto_proceed = (
            not property_just_provided and 
            has_dates and 
            has_guests and 
            has_budget
        ) or (
            property_just_provided and 
            has_dates and 
            has_guests and 
            children_provided and 
            rooms_provided and 
            budget_provided
        )
        
        if can_auto_proceed:
            # All required details present - proceed to availability check
            reservation_state["step"] = "availability_check"
            sync_to_session_state()
            
            summary = f"""Perfect! Here's what I have:

📅 **Dates:** {reservation_state['check_in']} to {reservation_state['check_out']} ({reservation_state['duration']} nights)
👥 **Guests:** {reservation_state['guests']} adults"""

            if reservation_state.get("children", 0) > 0:
                summary += f", {reservation_state['children']} children"

            summary += f"""
🛏️ **Rooms:** {reservation_state['rooms_needed']}
💰 **Budget:** ${reservation_state['budget_range'][0]}-${reservation_state['budget_range'][1]} per night

Now let me check availability and show you the perfect rooms for your stay!"""

            # Automatically proceed to check availability
            try:
                availability_result = check_availability_and_show_rooms("proceed")
                return summary + "\n\n" + availability_result
            except Exception as e:
                print(f"Error in automatic availability check: {e}")
                return summary + "\n\nI'll check availability for you in just a moment..."
        else:
            # Property selected but user should review/confirm details via widget
            reservation_state["step"] = "booking_details"
            sync_to_session_state()
            
            # Build a message about what we have so far
            confirmed_details = []
            if has_dates:
                confirmed_details.append(f"📅 Dates: {reservation_state['check_in']} to {reservation_state['check_out']}")
            if has_guests:
                confirmed_details.append(f"👥 Guests: {reservation_state['guests']} adults")
            
            confirmation_msg = f"""Great! I have your property selected: **{reservation_state['property']}**

"""
            
            if confirmed_details:
                confirmation_msg += "Here's what I have so far:\n" + "\n".join(confirmed_details) + "\n\n"
            
            confirmation_msg += """Please review and complete your booking details using the form above. You can adjust:
• Travel dates (check-in and check-out)
• Number of guests (adults and children)
• Number of rooms needed
• Your budget range per night

Once you've filled in all details, click **✅ Confirm Details** to proceed!"""
            
            return confirmation_msg
    
    else:
        # No property and no location - need to start fresh
        reservation_state["step"] = "location"
        sync_to_session_state()
        
        return """I'd be happy to help you make a reservation! 

To get started, please let me know:
🌎 Where would you like to stay - Sri Lanka or Maldives?

Once you let me know your destination, I can help find the perfect property for your stay!"""
    
