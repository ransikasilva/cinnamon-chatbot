"""
Conversation Handler for Cinnamon Hotels Chatbot
Handles multi-turn conversations, scenario detection, and structured responses
"""

from data import (
    HOTELS, ROOMS, ACTIVITIES, TRANSPORTATION, PROMOTIONS,
    MEAL_PLANS, PACKAGES, SCENARIOS,
    get_hotel_by_id, get_rooms_for_hotel, get_activities_for_hotel,
    calculate_route_cost, apply_promotion, search_hotels_by_criteria
)
import re


class ConversationState:
    """Manages conversation state for multi-turn interactions"""

    def __init__(self):
        self.context = {}
        self.scenario = None
        self.step = 0
        self.collected_info = {}

    def update(self, key, value):
        """Update conversation context"""
        self.collected_info[key] = value

    def get(self, key):
        """Get value from conversation context"""
        return self.collected_info.get(key)

    def reset(self):
        """Reset conversation state"""
        self.context = {}
        self.scenario = None
        self.step = 0
        self.collected_info = {}


class ScenarioDetector:
    """Detects which scenario the user is asking about"""

    @staticmethod
    def detect_scenario(message):
        """
        Analyze user message and detect scenario type
        Returns: scenario_type, confidence, extracted_data
        """
        message_lower = message.lower()

        # Scenario 1: Sea View Booking with Alternatives
        if ScenarioDetector._is_sea_view_booking(message_lower):
            return {
                "type": "sea_view_booking",
                "confidence": "high",
                "data": ScenarioDetector._extract_booking_details(message)
            }

        # Scenario 2: Family Trip with Budget
        if ScenarioDetector._is_family_trip(message_lower):
            return {
                "type": "family_trip",
                "confidence": "high",
                "data": ScenarioDetector._extract_family_details(message)
            }

        # Scenario 3: Full Trip Planning
        if ScenarioDetector._is_full_trip_planning(message_lower):
            return {
                "type": "full_trip_planning",
                "confidence": "high",
                "data": ScenarioDetector._extract_trip_details(message)
            }

        # General room inquiry
        if any(word in message_lower for word in ['room', 'booking', 'reserve', 'book', 'stay']):
            return {
                "type": "general_inquiry",
                "confidence": "medium",
                "data": {}
            }

        return {
            "type": "unknown",
            "confidence": "low",
            "data": {}
        }

    @staticmethod
    def _is_sea_view_booking(message):
        """Check if message is about sea view booking"""
        sea_view_keywords = ['sea view', 'ocean view', 'seaview']
        hotel_keywords = ['cinnamon grand', 'colombo', 'grand']

        has_sea_view = any(kw in message for kw in sea_view_keywords)
        has_hotel = any(kw in message for kw in hotel_keywords)
        has_booking = any(kw in message for kw in ['book', 'reserve', 'room', 'stay'])

        return has_sea_view or (has_hotel and has_booking)

    @staticmethod
    def _is_family_trip(message):
        """Check if message is about family trip"""
        family_keywords = ['family', 'kids', 'children', 'mother', 'father', 'parents']
        budget_keywords = ['budget', 'cost', 'price', 'spend', '$', 'usd']
        location_keywords = ['south', 'beach', 'beruwala', 'bey']

        has_family = any(kw in message for kw in family_keywords)
        has_budget = any(kw in message for kw in budget_keywords)
        has_location = any(kw in message for kw in location_keywords)

        return (has_family and has_budget) or (has_family and has_location)

    @staticmethod
    def _is_full_trip_planning(message):
        """Check if message is about full trip planning"""
        planning_keywords = ['plan', 'itinerary', 'trip', 'tour', 'journey', 'travel']
        duration_keywords = ['day', 'week', 'night']
        multi_location = ['sri lanka', 'around', 'multiple', 'all', 'tour']

        has_planning = any(kw in message for kw in planning_keywords)
        has_duration = any(kw in message for kw in duration_keywords)
        has_multi = any(kw in message for kw in multi_location)

        return (has_planning and has_duration) or (has_planning and has_multi)

    @staticmethod
    def _extract_booking_details(message):
        """Extract booking details from message"""
        data = {}

        # Extract nights
        nights_match = re.search(r'(\d+)\s*night', message.lower())
        if nights_match:
            data['nights'] = int(nights_match.group(1))

        # Extract guests
        guests_match = re.search(r'(\d+)\s*(?:people|person|guest|adult)', message.lower())
        if guests_match:
            data['guests'] = int(guests_match.group(1))

        # Extract hotel name
        if 'grand' in message.lower() or 'colombo' in message.lower():
            data['hotel_preference'] = 'CGD01'

        return data

    @staticmethod
    def _extract_family_details(message):
        """Extract family trip details from message"""
        data = {}

        # Extract kids count FIRST (before budget to avoid confusion)
        kids_match = re.search(r'(\d+)\s*(?:kid|child)', message.lower())
        if kids_match:
            data['kids'] = int(kids_match.group(1))

        # Extract nights
        nights_match = re.search(r'(\d+)\s*night', message.lower())
        if nights_match:
            data['nights'] = int(nights_match.group(1))

        # Extract budget - look for numbers >= 100 that aren't kids/nights
        all_numbers = re.findall(r'\d+', message)
        for num in all_numbers:
            num_int = int(num)
            if num_int >= 100 and num_int != data.get('kids') and num_int != data.get('nights'):
                data['budget'] = num_int
                break

        # Debug print
        print(f"DEBUG: Extracted family details: {data}")

        return data

    @staticmethod
    def _extract_trip_details(message):
        """Extract full trip planning details from message"""
        data = {}

        # Extract duration
        days_match = re.search(r'(\d+)\s*day', message.lower())
        if days_match:
            data['days'] = int(days_match.group(1))

        # Extract budget
        budget_match = re.search(r'\$?(\d+)', message)
        if budget_match:
            data['budget'] = int(budget_match.group(1))

        return data


class ResponseBuilder:
    """Builds structured responses for different scenarios"""

    @staticmethod
    def build_sea_view_response(data):
        """Build response for sea view booking scenario"""
        hotel = get_hotel_by_id("CGD01")
        rooms = get_rooms_for_hotel("CGD01")

        nights = data.get('nights', 3)
        guests = data.get('guests', 2)

        # Find sea view rooms
        sea_view_rooms = [r for r in rooms if 'sea view' in r['type'].lower()]

        response = {
            "type": "sea_view_booking",
            "message": f"Great choice! I found available sea view rooms at {hotel['name']} for {nights} nights for {guests} guests.",
            "hotel": hotel,
            "rooms": sea_view_rooms,
            "nights": nights,
            "guests": guests,
            "total_prices": [
                {
                    "room_type": room['type'],
                    "price_per_night": room['price'],
                    "total": room['price'] * nights,
                    "availability": room['availability']
                }
                for room in sea_view_rooms
            ],
            "alternatives": ResponseBuilder._get_alternative_hotels("CGD01", nights)
        }

        return response

    @staticmethod
    def build_family_trip_response(data):
        """Build response for family trip scenario"""
        budget = data.get('budget', 700)
        nights = data.get('nights', 3)
        kids = data.get('kids', 2)

        print(f"DEBUG build_family_trip_response: budget={budget}, nights={nights}, kids={kids}")

        # Find family-friendly hotels
        beach_hotels = search_hotels_by_criteria(region="Beach")
        print(f"DEBUG: Found {len(beach_hotels)} beach hotels")

        response_data = []
        for hotel in beach_hotels:
            rooms = get_rooms_for_hotel(hotel['id'])
            activities = get_activities_for_hotel(hotel['id'])
            print(f"DEBUG: Hotel {hotel['name']} has {len(rooms)} rooms")

            for room in rooms:
                room_total = room['price'] * nights
                print(f"DEBUG: Room {room['type']} - price per night: ${room['price']}, total: ${room_total}")

                # Check if fits budget
                if room_total <= budget * 0.85:  # Leave room for meals
                    meal_cost = MEAL_PLANS['breakfast']['price_per_day'] * nights * (2 + kids)
                    total_cost = room_total + meal_cost
                    print(f"DEBUG: Meal cost: ${meal_cost}, Total cost: ${total_cost}, Budget: ${budget}")

                    if total_cost <= budget:
                        print(f"DEBUG: [OK] Room fits budget!")
                        response_data.append({
                            "hotel": hotel,
                            "room": room,
                            "nights": nights,
                            "room_total": room_total,
                            "meal_plan": "breakfast",
                            "meal_cost": meal_cost,
                            "total_cost": total_cost,
                            "activities": activities,
                            "within_budget": True,
                            "savings": budget - total_cost
                        })
                    else:
                        print(f"DEBUG: [X] Total cost ${total_cost} exceeds budget ${budget}")
                else:
                    print(f"DEBUG: [X] Room total ${room_total} exceeds 85% of budget ${budget * 0.85}")

        print(f"DEBUG: Total options found: {len(response_data)}")

        # Sort by best value
        response_data.sort(key=lambda x: x['savings'], reverse=True)

        return {
            "type": "family_trip",
            "message": f"I found perfect family-friendly options for {nights} nights within your ${budget} budget!",
            "budget": budget,
            "nights": nights,
            "kids": kids,
            "options": response_data[:3],  # Top 3 options
            "packages": ResponseBuilder._get_family_packages()
        }

    @staticmethod
    def build_full_trip_response(data):
        """Build response for full trip planning scenario"""
        days = data.get('days', 10)
        budget = data.get('budget', 3000)

        # Create sample itinerary
        itinerary = [
            {
                "day_range": "1-2",
                "hotel_id": "CGD01",
                "hotel": get_hotel_by_id("CGD01"),
                "nights": 2,
                "room": get_rooms_for_hotel("CGD01")[2],  # Deluxe River View
                "activities": []
            },
            {
                "day_range": "3-5",
                "hotel_id": "CC001",
                "hotel": get_hotel_by_id("CC001"),
                "nights": 3,
                "room": get_rooms_for_hotel("CC001")[0],
                "activities": get_activities_for_hotel("CC001")
            },
            {
                "day_range": "6-8",
                "hotel_id": "CLH001",
                "hotel": get_hotel_by_id("CLH001"),
                "nights": 3,
                "room": get_rooms_for_hotel("CLH001")[0],
                "activities": get_activities_for_hotel("CLH001")
            },
            {
                "day_range": "9-10",
                "hotel_id": "CB001",
                "hotel": get_hotel_by_id("CB001"),
                "nights": 2,
                "room": get_rooms_for_hotel("CB001")[0],
                "activities": get_activities_for_hotel("CB001")
            }
        ]

        # Calculate costs
        accommodation_cost = sum(leg['room']['price'] * leg['nights'] for leg in itinerary)

        # Transportation route
        route = ["Airport", "Cinnamon Grand Colombo", "Cinnamon Citadel Kandy",
                 "Cinnamon Lodge Habarana", "Cinnamon Bey Beruwala", "Airport"]
        transport_costs = calculate_route_cost(route)

        # Activities cost (2 activities per location)
        activities_cost = 0
        for leg in itinerary:
            if leg['activities']:
                activities_cost += sum(act['price'] for act in leg['activities'][:2])

        # Meals
        meals_cost = MEAL_PLANS['half_board']['price_per_day'] * days

        total_cost = accommodation_cost + transport_costs['total_cost'] + activities_cost + meals_cost

        # Apply multi-property discount
        discount_info = apply_promotion(accommodation_cost, "Multi-Property")
        final_total = total_cost - discount_info['discount']

        return {
            "type": "full_trip_planning",
            "message": f"I've created a comprehensive {days}-day Sri Lanka journey for you!",
            "days": days,
            "budget": budget,
            "itinerary": itinerary,
            "route": route,
            "cost_breakdown": {
                "accommodation": accommodation_cost,
                "transportation": transport_costs['total_cost'],
                "activities": activities_cost,
                "meals": meals_cost,
                "subtotal": total_cost,
                "discount": discount_info['discount'],
                "total": final_total
            },
            "within_budget": final_total <= budget,
            "transportation_details": {
                "total_distance": transport_costs['total_distance'],
                "total_cost": transport_costs['total_cost']
            },
            "promotions_applied": ["Multi-Property - 10% off accommodation"]
        }

    @staticmethod
    def _get_alternative_hotels(current_hotel_id, nights):
        """Get alternative hotel suggestions"""
        alternatives = []

        for hotel_id, hotel in HOTELS.items():
            if hotel_id != current_hotel_id:
                rooms = get_rooms_for_hotel(hotel_id)
                if rooms:
                    cheapest_room = min(rooms, key=lambda x: x['price'])
                    alternatives.append({
                        "hotel": hotel,
                        "room": cheapest_room,
                        "total_cost": cheapest_room['price'] * nights
                    })

        return sorted(alternatives, key=lambda x: x['total_cost'])[:2]

    @staticmethod
    def _get_family_packages():
        """Get family-friendly packages"""
        return [pkg for pkg in PACKAGES.values() if 'family' in pkg['name'].lower()]


def process_message(message, conversation_state=None):
    """
    Main function to process user message and generate structured response
    """
    if conversation_state is None:
        conversation_state = ConversationState()

    # Detect scenario
    detection = ScenarioDetector.detect_scenario(message)

    # Build appropriate response
    if detection['type'] == 'sea_view_booking':
        response = ResponseBuilder.build_sea_view_response(detection['data'])
    elif detection['type'] == 'family_trip':
        response = ResponseBuilder.build_family_trip_response(detection['data'])
    elif detection['type'] == 'full_trip_planning':
        response = ResponseBuilder.build_full_trip_response(detection['data'])
    else:
        # Default response for general inquiries
        response = {
            "type": "general",
            "message": "I'd be happy to help you plan your stay! Could you tell me more about what you're looking for? For example:\n\n• Specific hotel or room type\n• Budget and duration\n• Number of guests\n• Preferred activities",
            "quick_suggestions": [
                "Show me sea view rooms at Cinnamon Grand",
                "I need a family trip package",
                "Plan a 10-day Sri Lanka tour"
            ]
        }

    return response
