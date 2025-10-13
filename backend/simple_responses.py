"""
Simple message-response mapping for Cinnamon Hotels Chatbot
Based on provided scenarios
"""

# Scenario 1: Sea View Room Booking
SEA_VIEW_RESPONSES = {
    "I want to book Cinnamon Grand for 3 nights in October.": {
        "response": "Thank you! Just a quick note — Cinnamon Grand is not beachfront, but Cinnamon Lakeside and Cinnamon Bey Beruwala have stunning sea views. Would you like me to check availability there?",
        "type": "text"
    },
    "Yes, check both please.": {
        "type": "structured",
        "message": "Cinnamon Lakeside: $180/night (Deluxe Lake View Room). Cinnamon Bey Beruwala: $210/night (Superior Ocean View Room). Both have breakfast included. Which one would you prefer?",
        "response_type": "room_comparison",
        "options": [
            {
                "hotel": {
                    "id": "CL001",
                    "name": "Cinnamon Lakeside",
                    "region": "Colombo",
                    "type": "Lakeside Resort",
                    "stars": 5,
                    "amenities": ["Lake View", "Breakfast Included", "Spa", "Pool"],
                    "description": "Luxury lakeside resort with stunning views"
                },
                "room": {
                    "type": "Deluxe Lake View Room",
                    "price": 180,
                    "availability": "Available"
                },
                "nights": 3,
                "total": 540
            },
            {
                "hotel": {
                    "id": "CBB01",
                    "name": "Cinnamon Bey Beruwala",
                    "region": "Beruwala",
                    "type": "Beach Resort",
                    "stars": 5,
                    "amenities": ["Ocean View", "Breakfast Included", "Spa", "Pool", "Beach Access"],
                    "description": "Stunning beachfront resort with ocean views"
                },
                "room": {
                    "type": "Superior Ocean View Room",
                    "price": 210,
                    "availability": "Available"
                },
                "nights": 3,
                "total": 630
            }
        ]
    },
    "I'll take Cinnamon Bey Beruwala.": {
        "response": "Perfect choice! Would you like to confirm the booking for 3 nights in October?",
        "type": "text"
    },
    "Yes, please.": {
        "response": "All set! I've reserved your Ocean View Room at Cinnamon Bey Beruwala for 3 nights in October. You'll receive your confirmation email shortly.",
        "type": "text"
    }
}

# Scenario 2: Family Trip Down South
FAMILY_TRIP_RESPONSES = {
    "Yes, I want to go down south with my family, and our budget is around $700.": {
        "response": "That's great! How many nights would you like to stay, and how many guests?",
        "type": "text"
    },
    "4 nights, 2 adults, 2 kids.": {
        "response": "With that budget, I recommend Cinnamon Bentota Beach — 4 nights at $160/night for a Family Room, including breakfast and access to the Kids' Club. Shall I check availability?",
        "type": "text"
    },
    "Yes, check availability.": {
        "response": "It's available! Total is $640 for 4 nights. Would you like to confirm?",
        "type": "text"
    },
    "Yes, please confirm the booking.": {
        "response": "Done! Your family getaway at Cinnamon Bentota Beach is confirmed. You'll receive the booking email shortly.",
        "type": "text"
    }
}

# Scenario 3: Solo Traveler Trip Planning
SOLO_TRIP_RESPONSES = {
    "Yes, I'm new to Sri Lanka and planning a 10-day trip.": {
        "response": "That sounds exciting! Would you like a mix of culture, nature, and beach experiences?",
        "type": "text",
        "show_map_button": True
    },
    "Yes, I'd love that.": {
        "type": "structured",
        "message": "Here's a perfect itinerary: Colombo (2 nights at Cinnamon Red), Kandy (3 nights at Cinnamon Citadel), and Hikkaduwa (5 nights at Hikka Tranz). Shall I share an estimated cost?",
        "response_type": "itinerary",
        "itinerary": [
            {
                "day_range": "1-2",
                "hotel": {
                    "id": "CR001",
                    "name": "Cinnamon Red",
                    "region": "Colombo",
                    "type": "City Hotel",
                    "stars": 4,
                    "amenities": ["Rooftop Pool", "City Views", "Restaurant"],
                    "description": "Modern city hotel perfect for exploring Colombo"
                },
                "room": {"type": "Standard Room", "price": 120, "availability": "Available"},
                "nights": 2
            },
            {
                "day_range": "3-5",
                "hotel": {
                    "id": "CC001",
                    "name": "Cinnamon Citadel Kandy",
                    "region": "Kandy",
                    "type": "River Resort",
                    "stars": 4,
                    "amenities": ["River View", "Ayurveda Spa", "Cultural Shows"],
                    "description": "Serene riverside resort near cultural attractions"
                },
                "room": {"type": "Deluxe Chalet", "price": 130, "availability": "Available"},
                "nights": 3,
                "activities": [
                    {"activity": "Temple of the Tooth Tour", "duration": "2 hrs", "best_time": "Morning", "price": 50}
                ]
            },
            {
                "day_range": "6-10",
                "hotel": {
                    "id": "HT001",
                    "name": "Hikka Tranz",
                    "region": "Hikkaduwa",
                    "type": "Beach Resort",
                    "stars": 4,
                    "amenities": ["Beach Access", "Water Sports", "Pool"],
                    "description": "Beautiful beachfront resort with water activities"
                },
                "room": {"type": "Ocean View Room", "price": 110, "availability": "Available"},
                "nights": 5,
                "activities": [
                    {"activity": "Snorkeling", "duration": "2 hrs", "best_time": "Morning", "price": 40},
                    {"activity": "Beach Relaxation", "duration": "All day", "best_time": "Anytime", "price": 0}
                ]
            }
        ]
    },
    "Yes, please.": {
        "response": "Approx. total: $1,250 (includes breakfast, transfers optional). Would you like to proceed with booking or adjust the itinerary?",
        "type": "text"
    },
    "Proceed with booking.": {
        "response": "Perfect! Your 10-day Sri Lanka adventure is confirmed. You'll get your itinerary and hotel details via email soon.",
        "type": "text"
    }
}

# Combine all responses
ALL_RESPONSES = {}
ALL_RESPONSES.update(SEA_VIEW_RESPONSES)
ALL_RESPONSES.update(FAMILY_TRIP_RESPONSES)
ALL_RESPONSES.update(SOLO_TRIP_RESPONSES)

# Greeting responses based on context
GREETING_RESPONSES = {
    "default": "Hello! Welcome to Cinnamon Hotels. How can I assist you today?",
    "family": "Hi there! Are you planning a family vacation with Cinnamon Hotels?",
    "solo": "Welcome to Cinnamon Hotels! Are you planning a solo trip in Sri Lanka?"
}

# For random greeting selection
DEFAULT_GREETINGS = [
    "Hello! Welcome to Cinnamon Hotels. How can I assist you today?",
    "Hi there! Are you planning a family vacation with Cinnamon Hotels?",
    "Welcome to Cinnamon Hotels! Are you planning a solo trip in Sri Lanka?"
]


def get_response(user_message):
    """
    Get bot response for user message
    Simple exact match lookup
    """
    # Normalize apostrophes (handle different apostrophe characters)
    user_message_normalized = user_message.replace("'", "'").replace("'", "'").replace("`", "'")

    print(f"DEBUG get_response: Received message: {repr(user_message)}")
    print(f"DEBUG get_response: Normalized message: {repr(user_message_normalized)}")
    print(f"DEBUG get_response: Total responses in ALL_RESPONSES: {len(ALL_RESPONSES)}")

    # Check for exact match
    if user_message_normalized in ALL_RESPONSES:
        print(f"DEBUG get_response: Found EXACT match")
        return ALL_RESPONSES[user_message_normalized]

    # Check for partial match (case-insensitive)
    user_lower = user_message_normalized.lower()
    print(f"DEBUG get_response: Checking partial matches with: {repr(user_lower)}")
    for key, value in ALL_RESPONSES.items():
        if key.lower() in user_lower or user_lower in key.lower():
            print(f"DEBUG get_response: Found PARTIAL match with key: {repr(key)}")
            return value

    # Default response
    print(f"DEBUG get_response: No match found, returning default")
    return {
        "response": "I'm here to help! Could you please provide more details about your booking or trip planning needs?",
        "type": "text"
    }
