"""
User Flow Handlers for Cinnamon Hotels Chatbot
Handles Type 1 (New Booking), Type 2 (Explorer), Type 3 (Edit Booking)
"""

from datetime import datetime
from data import HOTELS, get_hotel_by_id, get_activities_for_hotel

# Shared function to return all available hotels
def get_all_hotels_carousel():
    """Returns a carousel with all available Cinnamon hotels"""
    return {
        'type': 'hotel_carousel',
        'response': 'Here are all our available properties. Click on any hotel to book:',
        'hotels': [
            {
                'id': '42169',
                'name': 'Cinnamon Grand Colombo',
                'location': 'Colombo 3, Sri Lanka',
                'description': 'Luxury urban hotel in the heart of Colombo',
                'image': '/hotels/grand.jpg',
                'highlights': ['City Center', 'Business Hub', 'Fine Dining', 'Rooftop Bar']
            },
            {
                'id': '42170',
                'name': 'Cinnamon Lakeside Colombo',
                'location': 'Colombo 2, Sri Lanka',
                'description': 'Serene lakeside retreat in the city',
                'image': '/hotels/lakeside.jpg',
                'highlights': ['Lake View', 'Spa & Wellness', 'Cultural Sites', 'Shopping']
            },
            {
                'id': '42175',
                'name': 'Cinnamon Bey Beruwala',
                'location': 'Beruwala Beach, Sri Lanka',
                'description': 'Beachfront paradise on the golden coast',
                'image': '/hotels/beruwala.jpg',
                'highlights': ['Beach Access', 'Water Sports', 'Ayurveda Spa', 'Seafood']
            },
            {
                'id': '42174',
                'name': 'Cinnamon Life',
                'location': 'Union Place, Colombo',
                'description': 'Modern lifestyle hotel with entertainment',
                'image': '/hotels/life.jpg',
                'highlights': ['Shopping Mall', 'Entertainment', 'Modern Luxury', 'City Life']
            },
            {
                'id': '42171',
                'name': 'Cinnamon Wild Yala',
                'location': 'Yala National Park',
                'description': 'Wildlife safari lodge near Yala',
                'image': '/hotels/yala.jpg',
                'highlights': ['Safari Tours', 'Wildlife', 'Nature', 'Adventure']
            }
        ]
    }

# Type 1: New Booking User Flow
def handle_new_booking_flow(message):
    """
    Type 1: User wants to book a hotel
    Flow: Show hotel carousel -> User selects -> booking form
    """
    message_lower = message.lower()

    # Check for specific hotel booking (Cinnamon Grand)
    if any(word in message_lower for word in ['cinnamon grand', 'grand colombo']):
        return {
            'type': 'text',
            'response': 'Excellent choice! Cinnamon Grand Colombo is our premium city hotel. Please fill in your booking details:',
            'show_booking_form': True
        }

    # Check for general booking intent or greeting - show all hotels
    if any(phrase in message_lower for phrase in ['i need to book a hotel', 'i need to book', 'book a hotel', 'show me hotels', 'available hotels', 'book', 'reservation', 'reserve', 'stay', 'hi', 'hello', 'hey']):
        return get_all_hotels_carousel()

    # Default response - show all hotels
    return get_all_hotels_carousel()


# Type 2: Explorer User Flow
def handle_explorer_flow(message):
    """
    Type 2: User wants to explore Sri Lanka and get recommendations
    Flow: User says "just landed" -> Welcome -> Ask preferences -> Show hotel carousel
    """
    message_lower = message.lower()

    # Check for booking intent - show all hotels
    if any(phrase in message_lower for phrase in ['i need to book a hotel', 'i need to book', 'book a hotel', 'show me hotels', 'available hotels', 'book', 'reservation', 'reserve']):
        return get_all_hotels_carousel()

    # Welcome message for "just landed" or initial greeting
    if any(phrase in message_lower for phrase in ['just landed', 'landed in sri lanka', 'arrived in sri lanka', 'hi', 'hello', 'hey']):
        return {
            'type': 'text',
            'response': 'AYUBOWAN! Welcome to Sri Lanka! 🌴 I\'m thrilled to help you explore our beautiful island. You can explore our hotels on the map or tell me - what kind of experience are you looking for? Beaches, cultural sites, wildlife, or a mix of everything?',
            'show_map_button': True
        }

    # Beach interest
    if any(word in message_lower for word in ['beach', 'sea', 'ocean', 'surf', 'swim']):
        return {
            'type': 'hotel_carousel',
            'response': 'Perfect! For beaches, here are our stunning coastal properties. Click on any hotel to book:',
            'hotels': [
                {
                    'id': '42175',
                    'name': 'Cinnamon Bey Beruwala',
                    'location': 'Beruwala, Sri Lanka',
                    'description': 'A stunning beachfront resort perfect for beach lovers',
                    'image': '/hotels/beruwala.jpg',
                    'highlights': ['Pristine beaches', 'Water sports', 'Beach BBQ nights', 'Infinity pool']
                },
                {
                    'id': '42171',
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
                    'id': '42175',
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
                    'id': '42171',
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

    # Check for booking intent - show all hotels
    if any(phrase in message_lower for phrase in ['i need to book a hotel', 'i need to book', 'book a hotel', 'show me hotels', 'available hotels', 'new booking']):
        return get_all_hotels_carousel()

    # Check for booking reference pattern (CLB-1234, CGD-5678, etc)
    has_booking_ref = any(word in message_lower for word in ['clb-', 'cgd-', 'cb-', 'cc-'])

    # Date change request - check this first before other logic
    if any(word in message_lower for word in ['checkout', 'check-out', 'check out']) and any(word in message_lower for word in ['20th', '18th', '19th', '21st', '22nd', 'change', 'update']):
        if '20th' in message_lower:
            return {
                'type': 'booking_details',
                'response': 'Perfect! I have updated your booking:',
                'booking_data': {
                    'bookingRef': 'CLB-4821',
                    'hotel': 'Cinnamon Grand Colombo',
                    'checkIn': 'November 15, 2025',
                    'checkOut': 'November 20, 2025',
                    'guests': '2 Adults',
                    'room': 'Deluxe Room',
                    'isUpdated': True
                },
                'show_confirmation_button': True,
                'additional_message': 'No extra charges apply. Please confirm your changes to complete the modification.'
            }
        else:
            return {
                'type': 'text',
                'response': 'What would you like the new check-out date to be?'
            }

    # Check-in date changes
    if any(word in message_lower for word in ['checkin', 'check-in', 'check in']) and any(word in message_lower for word in ['change', 'update', 'modify']):
        return {
            'type': 'text',
            'response': 'What would you like the new check-in date to be?'
        }

    # If just booking reference provided (like "CLB-4821")
    if has_booking_ref and not any(word in message_lower for word in ['change', 'edit', 'modify', 'checkout', 'checkin', 'guest', 'room']):
        return {
            'type': 'booking_details',
            'response': 'Thank you! I found your booking:',
            'booking_data': {
                'bookingRef': 'CLB-4821',
                'hotel': 'Cinnamon Grand Colombo',
                'checkIn': 'November 15, 2025',
                'checkOut': 'November 18, 2025',
                'guests': '2 Adults',
                'room': 'Deluxe Room',
                'isUpdated': False
            }
        }

    # If user wants to change/edit/modify
    if 'change' in message_lower or 'edit' in message_lower or 'modify' in message_lower:
        if has_booking_ref:
            return {
                'type': 'text',
                'response': 'Thank you! What would you like to change? Check-in date, check-out date, number of guests, or room type?'
            }
        else:
            return {
                'type': 'text',
                'response': 'I can help! Just share your booking reference number with me (e.g., CLB-4821).'
            }

    # Guest count changes
    if any(word in message_lower for word in ['guest', 'people', 'person', 'adult', 'child']):
        return {
            'type': 'text',
            'response': 'How many guests will be staying? Please specify adults and children if applicable.'
        }

    # Room type changes
    if any(word in message_lower for word in ['room', 'suite', 'upgrade', 'downgrade']):
        return {
            'type': 'text',
            'response': 'What type of room would you like to change to? We have Deluxe Rooms, Suites, and Premium Rooms available.'
        }

    # Confirmation - when user confirms the changes
    if any(word in message_lower for word in ['confirm', 'yes', 'ok', 'okay', 'correct', 'proceed']):
        # Generate reservation URL with updated details
        # Hotel: 42169 (Cinnamon Grand Colombo)
        # Check-in: November 15, 2025 -> 2025-11-15
        # Check-out: November 20, 2025 -> 2025-11-20 (updated from 18th)
        # Guests: 2 Adults -> adult=1,1&child=1,0
        # Rooms: 1
        reservation_url = 'https://reservations.cinnamonhotels.com/?adult=1%2C1&arrive=2025-11-15&chain=31106&child=1%2C0&childages=%2C&currency=USD&depart=2025-11-20&hotel=42169&level=chain&locale=en-US&productcurrency=USD&rooms=1&segment=BB'

        return {
            'type': 'text',
            'response': 'Excellent! Your booking has been successfully updated. Click below to complete your reservation with the new details.',
            'reservation_url': reservation_url
        }

    # When user says no more changes
    if any(word in message_lower for word in ['no', 'that\'s all', 'nothing else', 'done', 'good']):
        return {
            'type': 'text',
            'response': 'All set! If you need anything else, I\'m here to help. Have a wonderful stay!'
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
