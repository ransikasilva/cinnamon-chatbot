from langchain_core.tools import tool


@tool
def get_hotel_info(query: str = None) -> str:
    """Get information about our hotels and properties."""
    try:
        properties = []
        
        info_text = "🏨 **Welcome to Cinnamon Hotels!** Here are our beautiful properties:\n\n"
        
        for prop in properties:
            info_text += f"**{prop['name']}**\n"
            info_text += f"📍 {prop['location']}\n"
            info_text += f"{prop['description']}\n"
            info_text += f"✨ Features: {', '.join(prop['features'])}\n\n"
        
        info_text += "Would you like to know more about a specific property or make a reservation?"
        return info_text
    except Exception as e:
        return "I can tell you about our two beautiful properties: Cinnamon Bey Beruwala (beachfront resort) and Cinnamon Lakeside Colombo (city hotel). Which would you like to know more about?"


@tool 
def handle_general_query(question: str) -> str:
    """Handle general questions about hotels, services, policies, etc."""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['policy', 'cancel', 'refund']):
        return """📋 **Hotel Policies:**

**Cancellation Policy:**
- Free cancellation up to 24 hours before check-in
- Late cancellations may incur charges

**Check-in/Check-out:**
- Check-in: 3:00 PM
- Check-out: 12:00 PM
- Early check-in/late check-out subject to availability

**Payment & Deposits:**
- Major credit cards accepted
- Security deposit may be required at check-in

For specific policy questions, please contact us at reservations@cinnamonhotels.com"""

    elif any(word in question_lower for word in ['dining', 'restaurant', 'food']):
        return """🍽️ **Dining Options:**

**Cinnamon Bey Beruwala:**
- Multiple restaurants with ocean views
- International and local cuisine
- Pool bar and beach service
- All-inclusive packages available

**Cinnamon Lakeside Colombo:**
- Fine dining restaurant
- Casual café and bar
- Room service available
- Business lunch options

Would you like specific information about our dining experiences?"""

    elif any(word in question_lower for word in ['amenities', 'facilities', 'services']):
        return """🏨 **Hotel Amenities:**

**Common Features:**
- Free WiFi throughout
- 24/7 room service
- Concierge services
- Fitness center
- Business center

**Cinnamon Bey Beruwala:**
- Private beach access
- Swimming pools
- Spa services
- Water sports
- Kids' club

**Cinnamon Lakeside Colombo:**
- Executive lounge
- Meeting rooms
- City tour arrangements
- Airport transfers

What specific amenities are you interested in?"""

    else:
        return f"""Thank you for your question about: {question}

I'm here to help with:
🏨 Hotel information and amenities
📅 Making new reservations  
📝 Existing booking changes
🍽️ Dining and services
📋 Policies and procedures

Could you be more specific about what you'd like to know? Or would you like to make a reservation?"""
