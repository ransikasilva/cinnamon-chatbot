from datetime import datetime, timedelta
from typing import Dict, List, Optional
from langchain_core.tools import tool
import json
from data_utils import check_room_availability
import streamlit as st

# Global reservation state that syncs with session state
_global_reservation_state = {
    'step': None,
    'location': None,           # Sri Lanka or Maldives
    'property_type': None,      # coastal, city, cultural, budget, premium
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

**Sri Lanka** - Beautiful island with diverse experiences
   • Pristine beaches in Bentota and Beruwala
   • Vibrant city life in Colombo
   • Cultural heritage and wildlife experiences
   • Perfect for families, couples, and business travelers

**Maldives** - Tropical paradise with luxury resorts
   • Crystal clear waters and overwater villas
   • World-class diving and snorkeling
   • Ultimate relaxation and romance
   • All-inclusive luxury experiences

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
    
    if destination_clean not in ["Sri Lanka", "Maldives"]:
        return """I specialize in two amazing destinations:

**Sri Lanka** - Cultural diversity, beautiful beaches, and wildlife
**Maldives** - Luxury overwater villas and pristine atolls

Which of these tropical paradises would you like to explore?"""
    
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
    """Use intelligent property selection that handles multiple matches by asking for clarification on budget and location preferences"""
    from models import get_llm
    
    sync_from_session_state()
    reservation_state = get_reservation_state()
    
    if reservation_state['step'] != 'property_selection':
        return "Please select your destination first."
    
    location = reservation_state.get('location')
    
    # Load detailed metadata
    import json
    import os
    
    try:
        metadata_path = os.path.join(os.path.dirname(__file__), 'data', 'metadata.json')
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        hotels_data = metadata.get('HotelsAndResorts', [])

    except Exception as e:
        print(f"Error loading metadata: {e}")
        return f"I'm sorry, I encountered an error loading hotel information. Please try again."
    

    # Filter hotels based on location and type
    filtered_hotels = filter_hotels_by_location_and_type(hotels_data, location)
    
    if not filtered_hotels:
        return f"I'm sorry, no properties are available for {location} at the moment. Please try a different destination."

    # Use LLM selection with filtered properties
    return perform_llm_selection(filtered_hotels, location, user_preferences, reservation_state)





def perform_llm_selection(location_hotels, location,user_preferences, reservation_state):
    """Perform standard LLM selection when no specific narrowing is needed"""
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
    
    # Create LLM prompt for intelligent selection
    selection_prompt = f"""You are an expert hotel concierge. Select the MOST APPROPRIATE hotel based on user preferences.

USER'S DESTINATION: {location}
USER'S PREFERENCES: "{user_preferences}"

AVAILABLE HOTELS:
{chr(10).join(hotels_info)}

INSTRUCTIONS:
1. Analyze preferences carefully (budget, experience type, activities, style)
2. Match against each hotel's characteristics
3. Select the ONE best match
4. Provide compelling reasons

RESPOND IN THIS EXACT FORMAT:
SELECTED_HOTEL: [Hotel Name]
REASONS:
• [Reason 1 with emoji]
• [Reason 2 with emoji]"""

    try:
        llm = get_llm()
        response = llm.invoke(selection_prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Parse LLM response
        selected_hotel_name = None
        selection_reasons = []
        
        lines = response_text.strip().split('\n')
        parsing_reasons = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('SELECTED_HOTEL:'):
                selected_hotel_name = line.replace('SELECTED_HOTEL:', '').strip()
            elif line.startswith('REASONS:'):
                parsing_reasons = True
            elif parsing_reasons and line.startswith('•'):
                selection_reasons.append(line)
        
        # Find the selected hotel
        selected_hotel = None
        for hotel in location_hotels:
            if selected_hotel_name and selected_hotel_name.lower() in hotel.get('Name', '').lower():
                selected_hotel = hotel
                break
        
        if not selected_hotel:
            selected_hotel = location_hotels[0]
            selection_reasons = ["🏨 Recommended based on your preferences", "✨ Excellent reviews and amenities"]
        
        # Store recommendation
        reservation_state['recommended_property'] = selected_hotel['Name']
        reservation_state['recommended_property_data'] = selected_hotel
        reservation_state['step'] = 'property_confirmation'
        sync_to_session_state()
        
        return f"""🎉 **Here's my recommendation!** Based on your preferences:

**{selected_hotel['Name']}**
📍 {selected_hotel.get('Location', '')}

{selected_hotel.get('UniqueDescription', '')}

✨ **Why this property is perfect for you:**
{chr(10).join(selection_reasons)}

**What would you like to do?**
• Say *"Yes, let's book this"* to continue with this recommendation
• Say *"Show me alternatives"* to see other options"""
        
    except Exception as e:
        print(f"Error in LLM selection: {e}")
        # Fallback to first available hotel
        selected_hotel = location_hotels[0]
        reservation_state['recommended_property'] = selected_hotel['Name']
        reservation_state['recommended_property_data'] = selected_hotel
        reservation_state['step'] = 'property_confirmation'
        sync_to_session_state()
        
        return f"""🎉 I recommend **{selected_hotel['Name']}** for your {location} getaway!

📍 {selected_hotel.get('Location', '')}
{selected_hotel.get('UniqueDescription', '')}

**What would you like to do?**
• Say *"Yes, let's book this"* to continue with this recommendation  
• Say *"Show me alternatives"* to see other options"""


@tool
def confirm_property_selection(user_response: str) -> str:
    """Handle user's response to property recommendation - either confirm or request alternatives"""
    sync_from_session_state()
    reservation_state = get_reservation_state()
    
    if reservation_state['step'] != 'property_confirmation':
        return "Please wait for a property recommendation first."
    
    user_response_lower = user_response.lower()
    
    # Check if user wants to proceed with the recommendation
    if any(phrase in user_response_lower for phrase in [
        'yes', 'perfect', 'proceed', 'book this', 'looks good', 'great', 
        'that works', 'sounds perfect', 'i like it', 'go ahead'
    ]):
        # User accepts the recommendation
        recommended_property = reservation_state.get('recommended_property')
        if recommended_property:
            reservation_state['property'] = recommended_property
            reservation_state['step'] = 'booking_details'
            sync_to_session_state()
            
            return f"""Excellent choice! 🎉 **{recommended_property}** it is!

Now let's plan your perfect stay. I need to know:

📅 **Travel Dates** - When would you like to check in and check out?
👥 **Guests** - How many adults and children?  
🛏️ **Rooms** - How many rooms do you need?
💰 **Budget** - What's your preferred budget range per night?

You can tell me all at once like:
*"January 15-20, 2025 for 2 adults and 1 child, 1 room, budget $300-500 per night"*

Or let's start with your travel dates - when would you like to visit?"""
        
    # Check if user wants alternatives or has different preferences
    elif any(phrase in user_response_lower for phrase in [
        'alternatives', 'different', 'other options', 'something else', 
        'show me more', 'not quite', 'maybe something', 'other hotels'
    ]):
        # Load metadata to show alternatives
        import json
        import os
        
        try:
            metadata_path = os.path.join(os.path.dirname(__file__), 'data', 'metadata.json')
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            hotels_data = metadata.get('HotelsAndResorts', [])
            price_mapping = metadata.get('PriceMapping', {})
            
            # Filter by location using the new function
            location = reservation_state.get('location')
            location_hotels = filter_hotels_by_location_and_type(hotels_data, location)
            
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

Or describe what you'd like differently from my first recommendation!"""
            
            reservation_state['step'] = 'property_selection'  # Go back to selection
            sync_to_session_state()
            return alternatives_text
            
        except Exception as e:
            reservation_state['step'] = 'property_selection'
            sync_to_session_state()
            return """Let me help you find something different! Please tell me more about what you're looking for:

• What type of experience do you want?
• Any specific location preferences?
• Budget considerations?
• Special amenities or features?

I'll find you the perfect match based on your preferences!"""
    
    else:
        # User response is unclear, ask for clarification
        return """I want to make sure I understand correctly! 

Would you like to:
• **Continue with the recommendation** - Say "Yes, let's book this" 
• **See other options** - Say "Show me alternatives"
• **Tell me more** about what you're specifically looking for

What would you prefer?"""

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
    
    # This would integrate with the actual room selection logic
    reservation_state['room_type'] = room_choice
    reservation_state['step'] = 'meal_selection'
    sync_to_session_state()
    
    return f"""Excellent choice! 🎉 You've selected: **{room_choice}**

Now, let's choose your meal plan. What dining experience would you prefer?

🍽️ **Available Meal Plans:**
• **Room Only** - Maximum flexibility to explore local dining
• **Breakfast Included** - Start each day with a delicious breakfast  
• **Half Board** - Breakfast and dinner included
• **Full Board** - All meals included
• **All Inclusive** - Meals, drinks, and activities included

What sounds perfect for your vacation?"""

@tool
def select_meal_plan(meal_choice: str) -> str:
    """Handle meal plan selection and calculate total cost"""
    sync_from_session_state()
    reservation_state = get_reservation_state()
    
    if reservation_state['step'] != 'meal_selection':
        return "Please select your room type first."
    
    reservation_state['meal_type'] = meal_choice
    reservation_state['step'] = 'final_confirmation'
    
    # Calculate total cost (simplified)
    base_cost = 300 * reservation_state.get('duration', 1)  # Simplified calculation
    reservation_state['total_cost'] = base_cost
    
    sync_to_session_state()
    
    return f"""Perfect! 🌟 Your **{meal_choice}** meal plan is confirmed.

📋 **Reservation Summary:**
🏨 **Hotel:** {reservation_state.get('property')}
📅 **Dates:** {reservation_state.get('check_in')} to {reservation_state.get('check_out')}
🛏️ **Room:** {reservation_state.get('room_type')}
🍽️ **Meals:** {meal_choice}
💰 **Estimated Total:** ${reservation_state.get('total_cost')}

Everything looks perfect! Shall I proceed with the final booking confirmation?"""

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