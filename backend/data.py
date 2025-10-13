# Cinnamon Hotels - Complete Data Structure

# Hotels Master Data
HOTELS = {
    "CGD01": {
        "id": "CGD01",
        "name": "Cinnamon Grand Colombo",
        "region": "Colombo",
        "type": "City Hotel",
        "stars": 5,
        "rooms": 501,
        "amenities": ["Pool", "Spa", "Gym", "Cloud Nine Rooftop", "24h Concierge"],
        "location": {"lat": 6.9271, "lng": 79.8612},
        "description": "Luxury city hotel in the heart of Colombo with rooftop dining"
    },
    "CC001": {
        "id": "CC001",
        "name": "Cinnamon Citadel Kandy",
        "region": "Kandy",
        "type": "River Resort",
        "stars": 4,
        "rooms": 120,
        "amenities": ["River View Pool", "Ayurveda Spa", "Cultural Performances"],
        "location": {"lat": 7.2906, "lng": 80.6337},
        "description": "Serene riverside resort near cultural attractions"
    },
    "CLH001": {
        "id": "CLH001",
        "name": "Cinnamon Lodge Habarana",
        "region": "Habarana",
        "type": "Eco Wildlife Resort",
        "stars": 5,
        "rooms": 152,
        "amenities": ["Nature Trails", "Ayurveda Spa", "Wildlife Safari", "Cycling"],
        "location": {"lat": 8.0519, "lng": 80.7514},
        "description": "Eco-friendly resort perfect for wildlife adventures"
    },
    "CB001": {
        "id": "CB001",
        "name": "Cinnamon Bey Beruwala",
        "region": "Beach",
        "type": "Beach Resort",
        "stars": 5,
        "rooms": 200,
        "amenities": ["Beach Access", "Water Sports", "BBQ Nights", "Kids Club"],
        "location": {"lat": 6.4788, "lng": 79.9828},
        "description": "Beachfront paradise with water sports and family activities"
    }
}

# Room Types and Pricing
ROOMS = {
    "CGD01": [
        {"type": "Premium Sea View", "price": 220, "availability": "Available"},
        {"type": "Executive Sea View", "price": 280, "availability": "Available"},
        {"type": "Deluxe River View", "price": 140, "availability": "Available"}
    ],
    "CC001": [
        {"type": "Deluxe Chalet", "price": 180, "availability": "Available"}
    ],
    "CLH001": [
        {"type": "Deluxe Sea View", "price": 160, "availability": "Available"}
    ],
    "CB001": [
        {"type": "Standard Room", "price": 150, "availability": "Available"},
        {"type": "Deluxe Room", "price": 195, "availability": "Available"},
        {"type": "Family Suite", "price": 245, "availability": "Limited"}
    ]
}

# Activities by Hotel
ACTIVITIES = [
    {"hotel_id": "CLH001", "activity": "Sigiriya Rock Fortress", "duration": "4 hrs", "best_time": "Morning", "price": 80},
    {"hotel_id": "CLH001", "activity": "Minneriya Safari", "duration": "3 hrs", "best_time": "Afternoon", "price": 75},
    {"hotel_id": "CLH001", "activity": "Village Tour", "duration": "3 hrs", "best_time": "Morning", "price": 45},
    {"hotel_id": "CC001", "activity": "Temple of the Tooth Tour", "duration": "2 hrs", "best_time": "Morning", "price": 50},
    {"hotel_id": "CB001", "activity": "Beach BBQ Night", "duration": "3 hrs", "best_time": "Evening", "price": 35},
    {"hotel_id": "CB001", "activity": "Water Sports", "duration": "2 hrs", "best_time": "Morning", "price": 80}
]

# Transportation Routes
TRANSPORTATION = [
    {"from": "Airport", "to": "Cinnamon Grand Colombo", "distance_km": 35, "cost": 40},
    {"from": "Cinnamon Grand Colombo", "to": "Cinnamon Citadel Kandy", "distance_km": 130, "cost": 60},
    {"from": "Cinnamon Citadel Kandy", "to": "Cinnamon Lodge Habarana", "distance_km": 90, "cost": 45},
    {"from": "Cinnamon Lodge Habarana", "to": "Cinnamon Bey Beruwala", "distance_km": 230, "cost": 90},
    {"from": "Cinnamon Bey Beruwala", "to": "Airport", "distance_km": 90, "cost": 40}
]

# Promotion Types
PROMOTIONS = [
    {"type": "Early Bird", "eligibility": "Book 60+ days in advance", "percent": 15},
    {"type": "Loyalty Gold", "eligibility": "Gold tier members", "percent": 20},
    {"type": "Multi-Property", "eligibility": "Book 3+ properties", "percent": 10},
    {"type": "Extended Stay", "eligibility": "7+ nights", "percent": 12},
    {"type": "Off-Season", "eligibility": "May-June, Sep-Oct", "percent": 25}
]

# Room Status Codes
ROOM_STATUS = {
    "AV": {"status": "Available", "action": "Book Now"},
    "LM": {"status": "Limited", "action": "Book Soon"},
    "BK": {"status": "Booked", "action": "Waitlist or Show Alternatives"},
    "HD": {"status": "Hold", "action": "Check Back in 24h"}
}

# Guest Profiles (for personalization)
GUESTS = {
    "G001": {
        "id": "G001",
        "name": "Rajesh Kumar",
        "type": "Frequent Business",
        "loyalty_tier": "Gold",
        "total_stays": 15,
        "preferences": ["Executive rooms", "Cloud Nine dining"]
    },
    "G002": {
        "id": "G002",
        "name": "Emma Thompson",
        "type": "Leisure Explorer",
        "loyalty_tier": "Silver",
        "total_stays": 3,
        "preferences": ["Cultural tours", "Local experiences"]
    },
    "G003": {
        "id": "G003",
        "name": "David Chen",
        "type": "First-time Visitor",
        "loyalty_tier": "Member",
        "total_stays": 0,
        "preferences": ["Trip planning", "Guided activities"]
    }
}

# Predefined User Scenarios
SCENARIOS = {
    "S1": {
        "id": "S1",
        "title": "Sea View Booking with Alternatives",
        "user_input": "Book Cinnamon Grand for 3 nights in October for 2 people with sea view",
        "expected_response": "Premium Sea View available at $220/night or Cinnamon Lakeside Lake View at $175/night (budget alternative)"
    },
    "S2": {
        "id": "S2",
        "title": "Family Trip Down South",
        "user_input": "Mother with 2 kids, 3 nights, budget $700",
        "expected_response": "Cinnamon Bey Deluxe Family Room fits your budget at $585 for 3 nights + breakfast plan for $90"
    },
    "S3": {
        "id": "S3",
        "title": "Solo Traveler Full Trip Planning",
        "user_input": "Plan 10-day Sri Lanka trip for $3000",
        "expected_response": "10-day journey covers Colombo, Kandy, Habarana & Beruwala with total spend of $2,980"
    }
}

# Meal Plans
MEAL_PLANS = {
    "breakfast": {"name": "Breakfast Only", "price_per_day": 15},
    "half_board": {"name": "Half Board (Breakfast + Dinner)", "price_per_day": 35},
    "full_board": {"name": "Full Board (All Meals)", "price_per_day": 50},
    "all_inclusive": {"name": "All Inclusive", "price_per_day": 75}
}

# Package Deals
PACKAGES = {
    "family_fun": {
        "name": "Family Fun Package",
        "includes": ["Family Room", "Breakfast", "Kids Club Access", "1 Water Activity"],
        "discount_percent": 15,
        "min_nights": 3
    },
    "romantic_getaway": {
        "name": "Romantic Getaway",
        "includes": ["Sea View Room", "Candlelight Dinner", "Spa for 2", "Late Checkout"],
        "discount_percent": 20,
        "min_nights": 2
    },
    "adventure_explorer": {
        "name": "Adventure Explorer",
        "includes": ["Standard Room", "Breakfast", "2 Guided Tours", "Safari"],
        "discount_percent": 10,
        "min_nights": 4
    }
}


def get_hotel_by_id(hotel_id):
    """Get hotel details by ID"""
    return HOTELS.get(hotel_id)


def get_rooms_for_hotel(hotel_id):
    """Get available rooms for a hotel"""
    return ROOMS.get(hotel_id, [])


def get_activities_for_hotel(hotel_id):
    """Get activities available at a hotel"""
    return [a for a in ACTIVITIES if a["hotel_id"] == hotel_id]


def calculate_route_cost(route_list):
    """Calculate total transportation cost for a route"""
    total_cost = 0
    total_distance = 0

    for i in range(len(route_list) - 1):
        from_loc = route_list[i]
        to_loc = route_list[i + 1]

        route = next((r for r in TRANSPORTATION if r["from"] == from_loc and r["to"] == to_loc), None)
        if route:
            total_cost += route["cost"]
            total_distance += route["distance_km"]

    return {"total_cost": total_cost, "total_distance": total_distance}


def apply_promotion(base_price, promotion_type):
    """Apply promotion discount to base price"""
    promo = next((p for p in PROMOTIONS if p["type"] == promotion_type), None)
    if promo:
        discount = base_price * (promo["percent"] / 100)
        return {"final_price": base_price - discount, "discount": discount, "percent": promo["percent"]}
    return {"final_price": base_price, "discount": 0, "percent": 0}


def search_hotels_by_criteria(region=None, hotel_type=None, min_stars=None, max_price=None):
    """Search hotels by various criteria"""
    results = list(HOTELS.values())

    if region:
        results = [h for h in results if h["region"].lower() == region.lower()]

    if hotel_type:
        results = [h for h in results if hotel_type.lower() in h["type"].lower()]

    if min_stars:
        results = [h for h in results if h["stars"] >= min_stars]

    # If max_price specified, filter by room prices
    if max_price:
        filtered = []
        for hotel in results:
            rooms = get_rooms_for_hotel(hotel["id"])
            if any(room["price"] <= max_price for room in rooms):
                filtered.append(hotel)
        results = filtered

    return results
