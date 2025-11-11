"""
User Flow Handlers for Cinnamon Hotels Chatbot
Handles Type 1 (New Booking), Type 2 (Explorer), Type 3 (Edit Booking)
"""

from datetime import datetime
from data import HOTELS, get_hotel_by_id, get_activities_for_hotel

# Type 1: New Booking User Flow
def handle_new_booking_flow(message):
    """
    Type 1: User wants to book a hotel
    Flow: Greet -> Show booking form (handled in frontend)
    """
    message_lower = message.lower()

    # Check for booking intent
    if any(word in message_lower for word in ['book', 'reservation', 'reserve', 'stay']):
        return {
            'type': 'text',
            'response': 'Amazing! Please go ahead and share the details.',
            'show_booking_form': True
        }

    # Default response for new booking users
    return {
        'type': 'text',
        'response': 'Welcome to Cinnamon Hotels! I can help you book a hotel room. Which property interests you?'
    }


# Type 2: Explorer User Flow
def handle_explorer_flow(message):
    """
    Type 2: User wants to explore Sri Lanka and get recommendations
    Flow: Welcome -> Ask interests -> Recommend hotels -> Create itinerary
    """
    message_lower = message.lower()

    # Welcome message for new visitors
    if any(word in message_lower for word in ['hi', 'hello', 'hey', 'arrived', 'new', 'first time', 'explore']):
        return {
            'type': 'text',
            'response': 'AYUBOWAN! Welcome to Sri Lanka! I can help you explore the island. Are you more interested in cultural sites, food, shopping, beaches, or a mix of everything?',
            'show_map_button': True
        }

    # Beach interest
    if any(word in message_lower for word in ['beach', 'sea', 'ocean', 'surf', 'swim']):
        return {
            'type': 'hotel_carousel',
            'response': 'Perfect! For beaches, here are our stunning coastal properties. Click on any hotel to book:',
            'hotels': [
                {
                    'id': '42171',
                    'name': 'Cinnamon Bey Beruwala',
                    'location': 'Beruwala, Sri Lanka',
                    'description': 'A stunning beachfront resort perfect for beach lovers',
                    'image': '/hotels/beruwala.jpg',
                    'highlights': ['Pristine beaches', 'Water sports', 'Beach BBQ nights', 'Infinity pool']
                },
                {
                    'id': '42175',
                    'name': 'Cinnamon Wild Yala',
                    'location': 'Yala, Sri Lanka',
                    'description': 'Luxury safari and beach experience',
                    'image': '/hotels/yala.jpg',
                    'highlights': ['Private beach', 'Safari tours', 'Wildlife viewing', 'Nature walks']
                }
            ]
        }

    # Cultural interest
    if any(word in message_lower for word in ['cultur', 'temple', 'heritage', 'historic', 'tradition']):
        return {
            'type': 'hotel_carousel',
            'response': 'Wonderful! For cultural experiences, here are perfect properties near heritage sites:',
            'hotels': [
                {
                    'id': '42169',
                    'name': 'Cinnamon Grand Colombo',
                    'location': 'Colombo 3, Sri Lanka',
                    'description': 'Premium city hotel with cultural tour access',
                    'image': '/hotels/grand.jpg',
                    'highlights': ['City Center', 'Cultural tours', 'Fine Dining', 'Rooftop Bar']
                },
                {
                    'id': '42170',
                    'name': 'Cinnamon Lakeside Colombo',
                    'location': 'Colombo 2, Sri Lanka',
                    'description': 'Lakeside luxury with heritage site access',
                    'image': '/hotels/lakeside.jpg',
                    'highlights': ['Lake views', 'Temple tours', 'Spa', 'Local cuisine']
                }
            ]
        }

    # Food interest
    if any(word in message_lower for word in ['food', 'eat', 'dining', 'cuisine', 'restaurant']):
        return {
            'type': 'hotel_carousel',
            'response': 'Sri Lankan cuisine is amazing! Here are hotels with exceptional dining experiences:',
            'hotels': [
                {
                    'id': '42169',
                    'name': 'Cinnamon Grand Colombo',
                    'location': 'Colombo 3, Sri Lanka',
                    'description': 'Multiple award-winning restaurants',
                    'image': '/hotels/grand.jpg',
                    'highlights': ['Cloud Nine rooftop', '7 restaurants', 'International cuisine', 'Cocktail bars']
                },
                {
                    'id': '42174',
                    'name': 'Cinnamon Life',
                    'location': 'Colombo 1, Sri Lanka',
                    'description': 'Modern dining hub with diverse options',
                    'image': '/hotels/life.jpg',
                    'highlights': ['Contemporary dining', 'Fusion cuisine', 'Bar & lounge', 'City views']
                }
            ]
        }

    # Mix of everything
    if any(word in message_lower for word in ['mix', 'everything', 'all', 'variety', 'both']):
        return {
            'type': 'hotel_carousel',
            'response': 'Excellent choice! Here are my top recommendations for a complete Sri Lanka experience:',
            'hotels': [
                {
                    'id': '42169',
                    'name': 'Cinnamon Grand Colombo',
                    'location': 'Colombo 3, Sri Lanka',
                    'description': 'Premier city hotel for urban adventures',
                    'image': '/hotels/grand.jpg',
                    'highlights': ['City Center', 'Business Hub', 'Fine Dining', 'Rooftop Bar']
                },
                {
                    'id': '42170',
                    'name': 'Cinnamon Lakeside Colombo',
                    'location': 'Colombo 2, Sri Lanka',
                    'description': 'Lakeside luxury in the heart of the city',
                    'image': '/hotels/lakeside.jpg',
                    'highlights': ['Lake views', 'Urban oasis', 'Spa & wellness', 'Shopping nearby']
                },
                {
                    'id': '42171',
                    'name': 'Cinnamon Bey Beruwala',
                    'location': 'Beruwala, Sri Lanka',
                    'description': 'Beachfront paradise with water activities',
                    'image': '/hotels/beruwala.jpg',
                    'highlights': ['Beach access', 'Water sports', 'All-inclusive', 'Family-friendly']
                },
                {
                    'id': '42174',
                    'name': 'Cinnamon Life',
                    'location': 'Colombo 1, Sri Lanka',
                    'description': 'Modern integrated resort experience',
                    'image': '/hotels/life.jpg',
                    'highlights': ['Luxury living', 'Entertainment', 'Multiple dining', 'Shopping mall']
                },
                {
                    'id': '42175',
                    'name': 'Cinnamon Wild Yala',
                    'location': 'Yala, Sri Lanka',
                    'description': 'Unique safari and beach combination',
                    'image': '/hotels/yala.jpg',
                    'highlights': ['Safari tours', 'Wildlife', 'Beach', 'Nature trails']
                }
            ]
        }

    # Itinerary request
    if any(word in message_lower for word in ['itinerary', 'plan', 'schedule', 'day', 'trip']):
        return create_simple_itinerary(message)

    # Default explorer response
    return {
        'type': 'text',
        'response': 'I\'d love to help you explore Sri Lanka! Tell me what interests you - beaches, culture, food, shopping, or a bit of everything?',
        'show_map_button': True
    }


def create_simple_itinerary(message):
    """Create a simple one-day itinerary"""
    return {
        'type': 'structured',
        'data': {
            'type': 'itinerary',
            'message': 'Here\'s a suggested one-day plan for you:',
            'schedule': {
                'morning': {
                    'time': '8:00 AM - 12:00 PM',
                    'activities': [
                        'Breakfast at hotel',
                        'Visit nearby cultural sites',
                        'Explore local markets'
                    ]
                },
                'lunch': {
                    'time': '12:00 PM - 2:00 PM',
                    'activities': [
                        'Traditional Sri Lankan lunch',
                        'Try local specialties like rice & curry'
                    ]
                },
                'evening': {
                    'time': '4:00 PM - 8:00 PM',
                    'activities': [
                        'Beach sunset or scenic viewpoint',
                        'Dinner at hotel restaurant',
                        'Relax and unwind'
                    ]
                }
            },
            'closing': 'Do let me know what you think! Would you like to book any of these hotels?'
        }
    }


# Type 3: Edit Booking User Flow
def handle_edit_booking_flow(message):
    """
    Type 3: User wants to edit an existing reservation
    Flow: Greet -> Ask for booking ID -> Confirm changes -> Update
    """
    message_lower = message.lower()

    # Check for booking reference
    has_booking_ref = any(word in message_lower for word in ['clb-', 'cgd-', 'cb-', 'cc-', 'reference', 'booking id'])

    if 'change' in message_lower or 'edit' in message_lower or 'modify' in message_lower:
        if has_booking_ref:
            # Extract mock booking reference
            return {
                'type': 'text',
                'response': 'That\'s a good choice! Share me your booking ID please.'
            }
        else:
            return {
                'type': 'text',
                'response': 'I can help! Just share your booking reference number with me (e.g., CLB-4821).'
            }

    # If booking reference provided
    if has_booking_ref:
        return {
            'type': 'text',
            'response': 'Thank you! What would you like to change? Check-in date, check-out date, number of guests, or room type?'
        }

    # Date change request
    if any(word in message_lower for word in ['date', 'check-in', 'check-out', '20th', '18th']):
        # Extract date if possible
        if '20th' in message_lower:
            return {
                'type': 'text',
                'response': 'Perfect! I have updated your booking to check-out on the 20th instead of the 18th. No extra charges apply. Anything else you\'d like to adjust?'
            }
        return {
            'type': 'text',
            'response': 'What would you like the new check-out date to be?'
        }

    # Confirmation
    if any(word in message_lower for word in ['no', 'that\'s all', 'nothing else', 'done', 'good']):
        return {
            'type': 'text',
            'response': 'All good now, enjoy! 🎉 If you need anything else, I\'m here to help.'
        }

    # Default edit booking response
    return {
        'type': 'text',
        'response': 'Hi! I can help you modify your booking. Do you have your booking reference number?'
    }


def get_user_flow_response(message, user_type):
    """
    Route message to appropriate user flow handler
    """
    if user_type == 'new_booking':
        return handle_new_booking_flow(message)
    elif user_type == 'explorer':
        return handle_explorer_flow(message)
    elif user_type == 'edit_booking':
        return handle_edit_booking_flow(message)
    else:
        # Default response
        return {
            'type': 'text',
            'response': 'Hello! How can I assist you today with Cinnamon Hotels?'
        }
