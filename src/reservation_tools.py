from datetime import datetime, timedelta
from typing import Dict, List, Optional
from langchain_core.tools import tool
import json
from data_utils import check_room_availability
import streamlit as st
import os 
import json

# Global reservation state that syncs with session state
_global_reservation_state = {
    'step': None,
    'location': None,           # Sri Lanka or Maldives
    'property_type': None,      
    'property': None,           # Selected hotel name
    'recommended_property': None,  # LLM recommended property
    'recommended_property_data': None,  # Full hotel data for recommendation
    'check_in': None,
    'check_out': None,
    'duration': None,
    'guests': None,
    'children': 0,              # Number of children
    'rooms_needed': 1,
    'budget_range': [100, 500], # [min, max] in USD per night
    'room_type': None,
    'meal_type': None,          # breakfast, half board, full board, all inclusive
    'total_cost': 0,
    'preferences': {},
    'confirmation_details': {}
}

def sync_to_session_state():
    """Sync global reservation state to Streamlit session state"""
    global _global_reservation_state
    try:
        if hasattr(st, 'session_state') and 'reservation_state' in st.session_state:
            st.session_state.reservation_state.update(_global_reservation_state)
    except:
        pass

def sync_from_session_state():
    """Sync Streamlit session state to global reservation state"""
    global _global_reservation_state
    try:
        if hasattr(st, 'session_state') and 'reservation_state' in st.session_state:
            _global_reservation_state.update(st.session_state.reservation_state)
    except:
        pass

def get_reservation_state():
    """Get reservation state (global version that works in tools)"""
    global _global_reservation_state
    return _global_reservation_state

def filter_hotels_by_location_and_type(hotels_data, location):
    """
    Filter hotels based on location and type criteria:
    - If location is Sri Lanka: include only hotels and resorts (exclude Maldives type)
    - If location is Maldives: include only Maldives type
    Returns list of filtered hotels with name, description, and type
    """
    filtered_hotels = []
    
    for hotel in hotels_data:
        hotel_type = hotel.get('Type', '')
        hotel_location = hotel.get('Location', '')
        
        # Filter based on location
        if location == "Sri Lanka":
            # For Sri Lanka: include hotels and resorts but exclude Maldives type
            if 'Sri Lanka' in hotel_location and hotel_type != 'Maldives':
                filtered_hotels.append({
                    'Name': hotel.get('Name', ''),
                    'Type': hotel_type,
                    'Location': hotel_location,
                    'UniqueDescription': hotel.get('UniqueDescription', ''),
                    'RoomTypes': hotel.get('RoomTypes', []),
                    'TotalRooms': hotel.get('TotalRooms', 0)
                })
        elif location == "Maldives":
            # For Maldives: include only Maldives type
            if hotel_type == 'Maldives':
                filtered_hotels.append({
                    'Name': hotel.get('Name', ''),
                    'Type': hotel_type, 
                    'Location': hotel_location,
                    'UniqueDescription': hotel.get('UniqueDescription', ''),
                    'RoomTypes': hotel.get('RoomTypes', []),
                    'TotalRooms': hotel.get('TotalRooms', 0)
                })
    
    return filtered_hotels

@tool
def start_reservation_process() -> str:
    """Initialize a new reservation process with the updated flow"""
    sync_from_session_state()
    reservation_state = get_reservation_state()
    
    
    # Initialize reservation state for new flow
    reservation_state.update({
        'step': 'location',
        'location': None,
        'property_type': None,
        'property': None,
        'recommended_property': None,
        'recommended_property_data': None,
        'check_in': None,
        'check_out': None,
        'duration': None,
        'guests': None,
        'children': 0,
        'rooms_needed': 1,
        'budget_range': [100, 500],
        'room_type': None,
        'meal_type': None,
        'total_cost': 0,
        'preferences': {},
        'confirmation_details': {}
    })
    
    sync_to_session_state()
    
    return """🌟 **Welcome to Cinnamon Hotels!** I'm excited to help you plan the perfect getaway!

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

Which destination calls to your heart? You can choose using the buttons above or simply tell me! 🌴"""

@tool
def set_destination_preference(destination: str) -> str:
    """Set the user's preferred destination (Sri Lanka or Maldives)"""
    print(f"DEBUG:Tool Input: {destination}")
    sync_from_session_state()
    reservation_state = get_reservation_state()
    
    if reservation_state['step'] != 'location':
        return "Let me help you start fresh. Please tell me which destination interests you."
    
    destination_clean = destination.strip().title()
    
    if 'sri lanka' in destination.lower():
        destination_clean = "Sri Lanka"
    elif 'maldives' in destination.lower():
        destination_clean = "Maldives"
    
#     if destination_clean not in ["Sri Lanka", "Maldives"]:
#         return """I specialize in two amazing destinations:

# **Sri Lanka** - Cultural diversity, beautiful beaches, and wildlife
# **Maldives** - Luxury overwater villas and pristine atolls

# Which of these tropical paradises would you like to explore?"""
    
    reservation_state['location'] = destination_clean
    reservation_state['step'] = 'property_selection'
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
    """Use intelligent property selection with clarifying questions when needed"""
    from models import get_llm
    
    sync_from_session_state()
    reservation_state = get_reservation_state()
    
    if reservation_state['step'] != 'property_selection':
        return "Please select your destination first."
    
    location = reservation_state.get('location')
    
    # Load hotel data
    try:
        metadata_path = os.path.join(os.path.dirname(__file__), 'data', 'metadata.json')
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        hotels_data = metadata.get('HotelsAndResorts', [])
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return "I'm sorry, I encountered an error loading hotel information. Please try again."
    
    # Filter hotels by location
    filtered_hotels = filter_hotels_by_location_and_type(hotels_data, location)
    
    if not filtered_hotels:
        return f"I'm sorry, no properties are available for {location} at the moment."
    
    # # PHASE 1: Intelligent Matching Analysis
    # matching_result = analyze_property_matches(filtered_hotels, location, user_preferences)
    # # print(f"ANALYSING RESULTS: {matching_result}")
    # if matching_result['status'] == 'single_match':
    #     # Perfect! Only one property matches - recommend it immediately
    #     return recommend_single_property(matching_result['property'], matching_result['reasons'], reservation_state)
    
    # elif matching_result['status'] == 'multiple_matches':
    #     print(f"ANALYSING MULTIPLE RESULTS: {len(matching_result['matching_properties'])}")
    #     # Multiple properties match - ask clarifying question
    #     return ask_clarifying_question(
    #         matching_result['matching_properties'],
    #         matching_result['missing_criteria'],
    #         user_preferences,
    #         reservation_state
    #     )
    
    # elif matching_result['status'] == 'no_match':
    #     # No exact matches - show alternatives with explanation
    #     return suggest_alternatives(filtered_hotels, matching_result['reason'], reservation_state)
    
    # else:
    #     # Fallback to standard LLM selection
    return perform_llm_selection(filtered_hotels, location, user_preferences, reservation_state)


# def analyze_property_matches(hotels, location, user_preferences):
#     """
#     Use LLM to analyze which properties match user preferences and determine next steps.
#     Returns: {
#         'status': 'single_match' | 'multiple_matches' | 'no_match',
#         'property': hotel_dict (if single match),
#         'matching_properties': [hotels] (if multiple matches),
#         'missing_criteria': str (what info is needed),
#         'reasons': [str] (why this/these match)
#     }
#     """
#     print(f"Analyzing Properties")
#     from models import get_llm
#     # print(f"Analyzing Hotels {hotels}")
#     # Prepare hotel information for LLM
#     hotels_info = []
#     for i, hotel in enumerate(hotels, 1):
#         # room_types = hotel.get('RoomTypes', [])
#         # price_info = "Contact for pricing"
#         # if room_types:
#         #     # Get price range from metadata
#         #     metadata_path = os.path.join(os.path.dirname(__file__), 'data', 'metadata.json')
#         #     with open(metadata_path, 'r') as f:
#         #         metadata = json.load(f)
#         #     # price_mapping = metadata.get('PriceMapping', {})
            
#         #     # prices = []
#         #     # for room in room_types:
#         #     #     price_key = room.get('Price', '')
#         #     #     if price_key in price_mapping:
#         #     #         prices.append(price_mapping[price_key])
            
#         #     # if prices:
#         #     #     price_info = f"${min(prices)}-${max(prices)}/night"
        
#         hotel_info = f"""
# Property {i}: {hotel.get('Name')}
# Type: {hotel.get('Type')}
# Location: {hotel.get('Location')}
# Description: {hotel.get('UniqueDescription', '')}
# """
#         hotels_info.append(hotel_info)
    
#     # Create analysis prompt
#     analysis_prompt = f"""You are an expert hotel analyst. Analyze which properties match the user's preferences.
# Note that if some hotel's description says Luxury its not a budget option. Don't look at the price just look at the description only when making a decision
# USER'S DESTINATION: {location}
# USER'S PREFERENCES: "{user_preferences}"

# AVAILABLE PROPERTIES:
# {chr(10).join(hotels_info)}

# TASK: Determine matching status and next steps.

# RESPOND IN THIS EXACT JSON FORMAT:
# {{
#     "status": "single_match" OR "multiple_matches" OR "no_match",
#     "matching_property_numbers": [list of property numbers that match],
#     "missing_criteria": "What key information is missing to narrow down? (budget/location_specifics/experience_type/amenities)",
#     "reasoning": "Brief Explanation of why this property/properties was chosen. Write it in a professional and friendly tone. You can Start like you asked for .. Then we recommend this because(DONT EXPOSE ANY INTERNAL DATA LIKE IT IS DESCRIBED AS ...)  .. ")"
# }}

# RULES:
# 1. "single_match": Only if ONE property clearly matches all criteria
# 2. "multiple_matches": If 2+ properties match equally well
# 3. "no_match": If no properties match the stated preferences
# 4. Focus on:  location type (beach/city/cultural), experience type (luxury/family/business)
# 5.Note that if some hotel's description says Luxury its not a budget option. Don't look at the price just look at the description only when making a decision
# 6. If user mentions specific location (e.g., "Colombo", "Bentota") and only one property is there, it's a single match
# 7. If user mentions unique characteristic that only one property has, it's a single match

# RESPOND ONLY WITH VALID JSON, NO OTHER TEXT."""

#     try:
#         llm = get_llm()
#         response = llm.invoke(analysis_prompt)
#         response_text = response.content if hasattr(response, 'content') else str(response)
#         print(f"LLM response {response_text}")
#         # Parse JSON response
#         # Extract JSON from response (handle markdown code blocks)
#         json_start = response_text.find('{')
#         json_end = response_text.rfind('}') + 1
#         json_str = response_text[json_start:json_end]
        
#         analysis = json.loads(json_str)
        
#         # Build result based on analysis
#         result = {
#             'status': analysis.get('status', 'multiple_matches'),
#             'reason': analysis.get('reasoning', '')
#         }
        
#         matching_numbers = analysis.get('matching_property_numbers', [])
        
#         if result['status'] == 'single_match' and len(matching_numbers) == 1:
#             property_idx = matching_numbers[0] - 1
#             result['property'] = hotels[property_idx]
#             result['reasons'] = [analysis.get('reasoning', '')]
            
#         elif result['status'] == 'multiple_matches' and len(matching_numbers) > 1:
#             result['matching_properties'] = [hotels[i-1] for i in matching_numbers]
#             result['missing_criteria'] = analysis.get('missing_criteria', 'budget and preferences')
            
#         return result
        
#     except Exception as e:
#         print(f"Error in property analysis: {e}")
#         # Fallback: treat as multiple matches
#         # return {
#         #     'status': 'multiple_matches',
#         #     'matching_properties': hotels,
#         #     'missing_criteria': 'your preferences',
#         #     'reason': 'Unable to analyze automatically'
#         # }


# def recommend_single_property(hotel, reasons, reservation_state):
#     """Recommend a single property that matches all criteria"""
#     reservation_state['recommended_property'] = hotel['Name']
#     reservation_state['recommended_property_data'] = hotel
#     reservation_state['step'] = 'property_confirmation'
#     sync_to_session_state()
    
#     return f"""Perfect match! Based on your preferences, I have the ideal property for you:

# **{hotel['Name']}**
#  {hotel.get('Location', '')}

# {hotel.get('UniqueDescription', '')}

#  **Why this is perfect for you:**
# {chr(10).join(['• ' + r for r in reasons])}

# """


# def ask_clarifying_question(matching_properties, missing_criteria, original_preferences, reservation_state):
#     """Ask intelligent clarifying questions to narrow down choices"""
#     from models import get_llm
#     print(f"Start processing clarifying questions....")
#     # Prepare property summaries
#     properties_summary = []
#     for hotel in matching_properties:
#         properties_summary.append(f"• {hotel['Name']} - {hotel.get('Location', '')}")
    
#     # Use LLM to generate natural clarifying question
#     clarification_prompt = f"""You are a friendly hotel concierge. The user said: "{original_preferences}"

# This matches {len(matching_properties)} properties:
# {chr(10).join(properties_summary)}

# The key missing information is: {missing_criteria}

# Generate a friendly, natural question to help narrow down the choice. The question should:
# 1. First mention that these are properties that match your preference (include their names)
# 2. Be conversational and warm
# 3. Present 2-3 clear options based on the missing criteria
# 4. Help the user decide between these properties
# 5. Not overwhelm with too much information

# RESPOND WITH JUST THE QUESTION, NO JSON OR EXTRA TEXT."""

#     try:
#         llm = get_llm()
#         response = llm.invoke(clarification_prompt)
#         clarifying_question = response.content if hasattr(response, 'content') else str(response)
        
#         # Store state for follow-up
#         reservation_state['pending_properties'] = [h['Name'] for h in matching_properties]
#         reservation_state['step'] = 'property_selection'  # Stay in selection
#         sync_to_session_state()
#         print(f"Clarifying Question: {clarifying_question}")
#         return clarifying_question
        
#     except Exception as e:
#         print(f"Error generating clarifying question: {e}")
#         # Fallback question
# #         return f"""I found {len(matching_properties)} properties that match your preferences:

# # {chr(10).join(properties_summary)}

# # To help me recommend the best one, could you tell me:
# # • What's your preferred budget range per night?
# # • Are you looking for luxury or value-focused experience?"""


def calculate_total_cost(reservation_state):
    """Calculate the total cost based on room rate, duration, guests, children, and meal plan"""
    
    # Get reservation details
    duration = reservation_state.get('duration', 1)
    guests = reservation_state.get('guests', 1)
    children = reservation_state.get('children', 0)
    rooms_needed = reservation_state.get('rooms_needed', 1)
    meal_type = reservation_state.get('meal_type', 'Room Only')
    selected_room_data = reservation_state.get('selected_room_data', {})
    
    # Get room rate per night
    room_rate_per_night = selected_room_data.get('base_rate_per_night', 200)  # Default fallback
    
    # Calculate base room cost
    base_room_cost = room_rate_per_night * duration * rooms_needed
    
    # Define meal plan costs per person per day
    meal_costs = {
        'room only': 0,
        'breakfast included': 25,
        'half board': 50,
        'full board': 75,
        'all inclusive': 120
    }
    
    # Get meal cost per person per day
    meal_cost_per_day = meal_costs.get(meal_type.lower(), 0)
    
    # Calculate total meal costs
    total_people = guests + children
    total_meal_cost = meal_cost_per_day * total_people * duration
    
    # Calculate total cost
    total_cost = base_room_cost + total_meal_cost
    
    return {
        'total_cost': total_cost,
        'breakdown': {
            'room_cost': base_room_cost,
            'meal_cost': total_meal_cost,
            'room_rate_per_night': room_rate_per_night,
            'meal_cost_per_person_per_day': meal_cost_per_day,
            'duration': duration,
            'guests': guests,
            'children': children,
            'rooms': rooms_needed
        }
    }


def suggest_alternatives(all_hotels, reason, reservation_state):
    """Suggest alternatives when no exact match is found"""
    
    alternatives_text = f"""I understand you're looking for something specific. {reason}

Here are all our available properties that might interest you:

"""
    
    for i, hotel in enumerate(all_hotels, 1):
        alternatives_text += f"""**{i}. {hotel.get('Name')}**
📍 {hotel.get('Location', '')}
{hotel.get('UniqueDescription', '')}

"""
    
    alternatives_text += """Please tell me more about what you're looking for, and I'll find the perfect match! You can mention:
• Budget preferences (luxury/mid-range/budget)
• Location specifics (beach/city/cultural sites)
• Experience type (romance/family/business/adventure)"""
    
    reservation_state['step'] = 'property_selection'
    sync_to_session_state()
    
    return alternatives_text



def perform_llm_selection(location_hotels, location, user_preferences, reservation_state):
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
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Parse JSON response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        json_str = response_text[json_start:json_end]
        
        analysis = json.loads(json_str)
        selected_hotel_names = analysis.get('recommended_hotels', [])
        reasoning = analysis.get('reasoning', '')
        individual_reasons = analysis.get('individual_reasons', {})
        
        # Find matching hotel objects
        matching_hotels = []
        for hotel_name in selected_hotel_names:
            for hotel in location_hotels:
                if hotel_name.lower() in hotel.get('Name', '').lower() or hotel.get('Name', '').lower() in hotel_name.lower():
                    matching_hotels.append(hotel)
                    break
        
        # Fallback if no matches found
        if not matching_hotels:
            matching_hotels = [location_hotels[0]]
        
        # Store all recommendations in the same format - always use property_confirmation step
        if len(matching_hotels) == 1:
            # Single recommendation
            selected_hotel = matching_hotels[0]
            hotel_name = selected_hotel['Name']
            reasons = individual_reasons.get(hotel_name, ["🏨 Perfectly matches your preferences", "✨ Excellent choice for your getaway"])
            
            reservation_state['recommended_property'] = hotel_name
            reservation_state['recommended_property_data'] = selected_hotel
            reservation_state['recommended_hotels'] = matching_hotels  # Store for alternatives
            reservation_state['step'] = 'property_confirmation'
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
            reservation_state['recommended_hotels'] = matching_hotels
            reservation_state['step'] = 'property_selection'  # Keep in selection mode
            sync_to_session_state()
            
            response_text = f"""🏨 **Excellent options!** I found {len(matching_hotels)} properties that match your preferences:

{reasoning}

"""
            
            for i, hotel in enumerate(matching_hotels, 1):
                hotel_name = hotel['Name']
                reasons = individual_reasons.get(hotel_name, ["Great match for your preferences"])
                
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
        reservation_state['recommended_property'] = selected_hotel['Name']
        reservation_state['recommended_property_data'] = selected_hotel
        reservation_state['recommended_hotels'] = [selected_hotel]
        reservation_state['step'] = 'property_confirmation'
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
    
    if reservation_state['step'] not in ['property_confirmation', 'property_selection']:
        return "Please wait for a property recommendation first."
    
    location = reservation_state.get('location')
    if not location:
        return "Please select your destination first."
    
    try:
        # Load hotel data
        metadata_path = os.path.join(os.path.dirname(__file__), 'data', 'metadata.json')
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        hotels_data = metadata.get('HotelsAndResorts', [])
        price_mapping = metadata.get('PriceMapping', {})
        
        # Filter by location using the existing function
        location_hotels = filter_hotels_by_location_and_type(hotels_data, location)
        
        if not location_hotels:
            return f"I'm sorry, no properties are available for {location} at the moment."
        
        # Store all location hotels for future selection
        reservation_state['all_location_hotels'] = location_hotels
        reservation_state['step'] = 'property_selection'  # Set to selection mode
        sync_to_session_state()
        
        # Create alternatives list
        alternatives_text = f"Here are all our available properties in {location}:\n\n"
        
        for i, hotel in enumerate(location_hotels, 1):
            room_types = hotel.get('RoomTypes', [])
            if room_types:
                prices = [price_mapping.get(room.get('Price', ''), 0) for room in room_types]
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
def confirm_property_selection(selection_type: str, hotel_identifier: str = "") -> str:
    """
    Handle user's response to property recommendation OR selection from alternatives list.
    
    Args:
        selection_type (str): Type of user action - must be one of:
            - "confirm": User wants to book the recommended property
            - "select_by_name": User selects a specific hotel by name
            - "select_by_number": User selects a hotel by number from list
            - "details": User wants more information about a property
            
        hotel_identifier (str): Context-dependent identifier:
            - For "confirm": pass "confirmed" (value ignored, just confirmation intent)
            - For "select_by_name": exact hotel name (e.g., "Cinnamon Grand Colombo")
            - For "select_by_number": number as string (e.g., "1", "2", "3")
            - For "details": hotel name OR number for details request
    
    Returns:
        str: Response message with booking confirmation, hotel details, or error message
        
    Usage Examples:
        # User confirms recommended property: "Yes, I'll book it"
        confirm_property_selection("confirm", "confirmed")
        
        # User selects by number: "I want option 2"  
        confirm_property_selection("select_by_number", "2")
        
        # User selects by name: "I want to book Cinnamon Grand"
        confirm_property_selection("select_by_name", "Cinnamon Grand")
        
        # User asks for details: "Tell me more about hotel 1"
        confirm_property_selection("details", "1")
        
        # User asks for details by name: "What about Cinnamon Lakeside?"
        confirm_property_selection("details", "Cinnamon Lakeside")
    
    Note: 
        The LLM should interpret user intent and map it to the appropriate parameters.
        No matter how the user phrases their request, standardize it to these clear parameters.
    """
    sync_from_session_state()
    reservation_state = get_reservation_state()
    
    if reservation_state['step'] not in ['property_confirmation', 'property_selection']:
        return "Please wait for a property recommendation first."
    
    recommended_hotels = reservation_state.get('recommended_hotels', [])
    all_location_hotels = reservation_state.get('all_location_hotels', [])
    
    # Validate input parameters
    valid_selection_types = ["confirm", "select_by_name", "select_by_number", "details"]
    if selection_type not in valid_selection_types:
        return f"Invalid selection type. Must be one of: {', '.join(valid_selection_types)}"
    
    # HANDLE CONFIRMATION (for recommended properties)
    if selection_type == "confirm":
        if reservation_state['step'] == 'property_confirmation':
            recommended_property_data = reservation_state.get('recommended_property_data')
            if recommended_property_data:
                return proceed_with_booking(recommended_property_data, reservation_state)
            else:
                return "I don't have a current recommendation. Please start the property selection again."
        else:
            return "No property recommendation to confirm. Please make a selection first."
    
    # HANDLE SELECTION BY NUMBER
    elif selection_type == "select_by_number":
        try:
            choice_num = int(hotel_identifier)
        except ValueError:
            return "Invalid number format. Please provide a valid number."
        
        # From alternatives list
        if all_location_hotels and reservation_state['step'] == 'property_selection':
            if 1 <= choice_num <= len(all_location_hotels):
                selected_hotel = all_location_hotels[choice_num - 1]
                return proceed_with_booking(selected_hotel, reservation_state)
            else:
                return f"Invalid selection. Please choose a number between 1 and {len(all_location_hotels)}."
        
        # From multiple recommendations
        elif len(recommended_hotels) > 1:
            if 1 <= choice_num <= len(recommended_hotels):
                selected_hotel = recommended_hotels[choice_num - 1]
                return proceed_with_booking(selected_hotel, reservation_state)
            else:
                return f"Invalid selection. Please choose a number between 1 and {len(recommended_hotels)}."
        
        else:
            return "No numbered list available. Please select by hotel name instead."
    
    # HANDLE SELECTION BY NAME
    elif selection_type == "select_by_name":
        hotel_name_lower = hotel_identifier.lower()
        
        # Search in alternatives list first
        if all_location_hotels and reservation_state['step'] == 'property_selection':
            for hotel in all_location_hotels:
                if hotel_name_lower in hotel.get('Name', '').lower() or hotel.get('Name', '').lower() in hotel_name_lower:
                    return proceed_with_booking(hotel, reservation_state)
        
        # Search in recommended hotels
        elif recommended_hotels:
            for hotel in recommended_hotels:
                if hotel_name_lower in hotel.get('Name', '').lower() or hotel.get('Name', '').lower() in hotel_name_lower:
                    return proceed_with_booking(hotel, reservation_state)
        
        # If not found
        available_hotels = all_location_hotels or recommended_hotels
        if available_hotels:
            hotel_list = ", ".join([hotel.get('Name', '') for hotel in available_hotels])
            return f"Hotel '{hotel_identifier}' not found. Available options: {hotel_list}"
        else:
            return "No hotels available for selection. Please start the process again."
    
    # HANDLE DETAILS REQUEST
    elif selection_type == "details":
        target_hotel = None
        
        # If hotel_identifier is a number, get hotel by index
        try:
            choice_num = int(hotel_identifier)
            available_list = all_location_hotels or recommended_hotels
            if available_list and 1 <= choice_num <= len(available_list):
                target_hotel = available_list[choice_num - 1]
        except ValueError:
            # If not a number, search by name
            hotel_name_lower = hotel_identifier.lower()
            available_list = all_location_hotels or recommended_hotels or [reservation_state.get('recommended_property_data')]
            
            for hotel in available_list:
                if hotel and (hotel_name_lower in hotel.get('Name', '').lower() or hotel.get('Name', '').lower() in hotel_name_lower):
                    target_hotel = hotel
                    break
        
        # Return details if hotel found
        if target_hotel:
            return f"""**{target_hotel['Name']}** - Detailed Information:

📍 **Location:** {target_hotel.get('Location', '')}
🏨 **Type:** {target_hotel.get('Type', '')}

**Description:**
{target_hotel.get('UniqueDescription', '')}

**Available Room Types:**
{chr(10).join(['• ' + room.get('RoomType', '') for room in target_hotel.get('RoomTypes', [])[:3]])}

Would you like to book this property?"""
        else:
            return f"Could not find details for '{hotel_identifier}'. Please check the hotel name or number."
    
    # Fallback
    return "Unable to process your selection. Please try again with valid parameters."


def proceed_with_booking(selected_hotel, reservation_state):
    """Helper function to proceed with booking for a selected hotel"""
    reservation_state['property'] = selected_hotel['Name']
    reservation_state['recommended_property'] = selected_hotel['Name']
    reservation_state['recommended_property_data'] = selected_hotel
    reservation_state['step'] = 'booking_details'
    # Clear alternatives list since selection is made
    reservation_state['all_location_hotels'] = []
    sync_to_session_state()
    
    return f"""Excellent choice! 🎉 **{selected_hotel['Name']}** it is!

Now let's plan your perfect stay. I need to know:

📅 **Travel Dates** - When would you like to check in and check out?
👥 **Guests** - How many adults and children?  
🛏️ **Rooms** - How many rooms do you need?
💰 **Budget** - What's your preferred budget range per night?

You can tell me all at once like:
*"January 15-20, 2025 for 2 adults and 1 child, 1 room, budget $300-500 per night"*

Or let's start with your travel dates - when would you like to visit?"""

@tool
def set_booking_details(booking_info: str) -> str:
    """Collect check-in/out dates, number of guests, children, and budget range"""
    sync_from_session_state()
    reservation_state = get_reservation_state()
    
    if reservation_state['step'] != 'booking_details':
        return "Please select your property first."
    print(f"Booking info {booking_info}")
    # Parse booking information from user input
    parsed_info = parse_booking_details(booking_info)
    print(f"Parsed Info {parsed_info}")
    # Update reservation state with parsed information
    if parsed_info['check_in']:
        reservation_state['check_in'] = parsed_info['check_in']
    if parsed_info['check_out']:
        reservation_state['check_out'] = parsed_info['check_out']
    if parsed_info['guests']:
        reservation_state['guests'] = parsed_info['guests']
    if parsed_info['children'] is not None:
        reservation_state['children'] = parsed_info['children']
    if parsed_info['rooms']:
        reservation_state['rooms_needed'] = parsed_info['rooms']
    if parsed_info['budget_range']:
        reservation_state['budget_range'] = parsed_info['budget_range']
    
    # Calculate duration if both dates are available
    if reservation_state['check_in'] and reservation_state['check_out']:
        check_in_date = datetime.strptime(reservation_state['check_in'], '%Y-%m-%d')
        check_out_date = datetime.strptime(reservation_state['check_out'], '%Y-%m-%d')
        reservation_state['duration'] = (check_out_date - check_in_date).days
    
    # Check if we have all required information
    required_fields = ['check_in', 'check_out', 'guests', 'budget_range']
    missing_fields = [field for field in required_fields if not reservation_state.get(field)]
    
    if missing_fields:
        missing_text = ", ".join(missing_fields)
        return f"I still need: {missing_text}. Please provide this information."
    
    # All information collected, proceed to availability checking
    reservation_state['step'] = 'availability_check'
    sync_to_session_state()
    
    summary = f"""Perfect! Here's what I have:

📅 **Dates:** {reservation_state['check_in']} to {reservation_state['check_out']} ({reservation_state['duration']} nights)
👥 **Guests:** {reservation_state['guests']} adults"""
    
    if reservation_state['children'] > 0:
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

@tool
def check_availability_and_show_rooms(confirmation: str = "proceed") -> str:
    """Check room availability and show options within the user's budget"""
    sync_from_session_state()
    reservation_state = get_reservation_state()
    
    if reservation_state['step'] != 'availability_check':
        return "Please provide your booking details first."
    
    property_name = reservation_state.get('property')
    if not property_name:
        return "Please select a property first."
    
    try:
        # Check availability using the hotel data manager
        available_rooms = check_room_availability(
            property_name=property_name,
            check_in=reservation_state['check_in'],
            check_out=reservation_state['check_out'],
            rooms_needed=reservation_state['rooms_needed'],
            budget_min=reservation_state['budget_range'][0],
            budget_max=reservation_state['budget_range'][1]
        )
        print(f"DEBUG:Available rooms: {available_rooms}")
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
        
        reservation_state['step'] = 'room_selection'
        reservation_state['available_rooms'] = available_rooms  # Store for later use
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
    
    if reservation_state['step'] != 'room_selection':
        return "Please check room availability first."
    
    # Find the selected room from available rooms
    available_rooms = reservation_state.get('available_rooms', [])
    selected_room = None
    
    # Try to match by number first
    import re
    number_match = re.search(r'\b(\d+)\b', room_choice)
    if number_match:
        choice_num = int(number_match.group(1))
        if 1 <= choice_num <= len(available_rooms):
            selected_room = available_rooms[choice_num - 1]
    
    # If not found by number, try to match by room type name
    if not selected_room:
        for room in available_rooms:
            if room_choice.lower() in room.get('room_type', '').lower():
                selected_room = room
                break
    
    # Fallback to first room if no match
    if not selected_room and available_rooms:
        selected_room = available_rooms[0]
    
    if selected_room:
        reservation_state['room_type'] = selected_room['room_type']
        reservation_state['selected_room_data'] = selected_room  # Store complete room data
        reservation_state['step'] = 'meal_selection'
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
    
    if reservation_state['step'] != 'meal_selection':
        return "Please select your room type first."
    
    reservation_state['meal_type'] = meal_choice
    reservation_state['step'] = 'final_confirmation'
    
    # Calculate total cost using proper calculation
    cost_details = calculate_total_cost(reservation_state)
    reservation_state['total_cost'] = cost_details['total_cost']
    reservation_state['cost_breakdown'] = cost_details['breakdown']
    
    sync_to_session_state()
    
    # Create detailed cost breakdown
    breakdown = cost_details['breakdown']
    total_people = breakdown['guests'] + breakdown['children']
    
    cost_summary = f"""Perfect! 🌟 Your **{meal_choice}** meal plan is confirmed.

📋 **Reservation Summary:**

🏨 **Hotel:** {reservation_state.get('property')}

📅 **Dates:** {reservation_state.get('check_in')} to {reservation_state.get('check_out')} ({breakdown['duration']} nights)

👥 **Guests:** {breakdown['guests']} adults"""
    
    if breakdown['children'] > 0:
        cost_summary += f", {breakdown['children']} children"
    
    cost_summary += f"""
�🛏️ **Rooms:** {breakdown['rooms']} x {reservation_state.get('room_type')}

🍽️ **Meals:** {meal_choice}

💰 **Cost Breakdown:**

 🛏️ **Room Charges:**  \n\n                          
 ${breakdown['room_rate_per_night']}/night × {breakdown['duration']} nights × {breakdown['rooms']} room(s) 
 = ${breakdown['room_cost']:,.2f}    \n\n """

    if breakdown['meal_cost'] > 0:
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
    
    if reservation_state['step'] != 'final_confirmation':
        return "Please complete all booking steps first."
    
    if 'yes' in confirmation.lower() or 'confirm' in confirmation.lower():
        # Generate booking reference
        import random
        booking_ref = f"CN{random.randint(100000, 999999)}"
        
        reservation_state['confirmation_details'] = {
            'booking_reference': booking_ref,
            'confirmed_at': datetime.now().isoformat()
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

def parse_booking_details(booking_info: str) -> dict:
    """Parse user booking information into structured data"""
    import re
    from datetime import datetime, timedelta
    
    info = booking_info.lower()
    original_info = booking_info  # Keep original case for dates
    parsed = {
        'check_in': None,
        'check_out': None,
        'guests': None,
        'children': None,
        'rooms': None,
        'budget_range': None
    }
    
    # Parse check-in date (various formats)
    checkin_patterns = [
        r'check-in[:\s]+(\d{4}-\d{2}-\d{2})',  # check-in 2025-10-09
        r'checkin[:\s]+(\d{4}-\d{2}-\d{2})',   # checkin 2025-10-09
        r'(\d{4}-\d{2}-\d{2})\s*(?:to|,|\s+check)',  # 2025-10-09 to/,/check
    ]
    
    for pattern in checkin_patterns:
        match = re.search(pattern, original_info, re.IGNORECASE)
        if match:
            parsed['check_in'] = match.group(1)
            break
    
    # Parse check-out date (various formats)
    checkout_patterns = [
        r'check-out[:\s]+(\d{4}-\d{2}-\d{2})',  # check-out 2025-10-15
        r'checkout[:\s]+(\d{4}-\d{2}-\d{2})',   # checkout 2025-10-15
        r'(?:to|,)\s*(\d{4}-\d{2}-\d{2})',      # to 2025-10-15
        r'check-out\s+(\d{4}-\d{2}-\d{2})',     # check-out 2025-10-15
    ]
    
    for pattern in checkout_patterns:
        match = re.search(pattern, original_info, re.IGNORECASE)
        if match:
            parsed['check_out'] = match.group(1)
            break
    
    # Parse guest count
    guest_matches = re.findall(r'(\d+)\s*(?:adult|guest|people|person)', info)
    if guest_matches:
        parsed['guests'] = int(guest_matches[0])
    
    # Parse children count
    children_matches = re.findall(r'(\d+)\s*(?:child|children|kid)', info)
    if children_matches:
        parsed['children'] = int(children_matches[0])
    
    # Parse room count
    room_matches = re.findall(r'(\d+)\s*room', info)
    if room_matches:
        parsed['rooms'] = int(room_matches[0])
    
    # Parse budget range - improved pattern to avoid matching dates
    budget_patterns = [
        r'budget\s+\$?(\d+)[-\s]*(?:to|-|\$)\s*\$?(\d+)',  # budget $100-$500
        r'\$(\d{2,4})[-\s]*(?:to|-)\s*\$(\d{2,4})',        # $100-$500 (2-4 digits to avoid dates)
        r'budget\s+\$?(\d+)\s*[-]\s*\$?(\d+)',             # budget $100-$500
    ]
    
    for pattern in budget_patterns:
        budget_matches = re.findall(pattern, info)
        if budget_matches:
            min_budget, max_budget = budget_matches[0]
            # Only accept reasonable budget ranges (not dates)
            min_val, max_val = int(min_budget), int(max_budget)
            if min_val < 2000 and max_val < 2000 and min_val < max_val:
                parsed['budget_range'] = [min_val, max_val]
                break
    
    return parsed