from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# Mock Q&A data for Cinnamon Hotels
MOCK_RESPONSES = {
    "rooms": [
        "We offer a variety of luxurious rooms including Deluxe Rooms, Ocean View Suites, and Presidential Suites. Would you like to know more about a specific room type?",
        "Our rooms feature modern amenities, complimentary Wi-Fi, air conditioning, and stunning views. Prices start from $150 per night.",
    ],
    "eat": [
        "Cinnamon Hotels offers multiple dining options including our signature restaurant '7 Degrees North', poolside cafe, and 24-hour room service.",
        "Our chefs prepare authentic Sri Lankan cuisine, international dishes, and fresh seafood. We also cater to special dietary requirements.",
    ],
    "dining": [
        "Experience fine dining at our award-winning restaurants. We offer breakfast buffets, à la carte lunch, and themed dinner nights.",
        "Our bars serve premium cocktails, local arrack, and a selection of international wines and spirits.",
    ],
    "explore": [
        "Discover Sri Lanka with our curated experiences - whale watching in Mirissa, temple tours in Kandy, or safari adventures in Yala National Park.",
        "We offer city tours, water sports, cultural experiences, and wellness programs. Our concierge can help plan your perfect itinerary.",
    ],
    "help": [
        "I'm here to assist you! You can ask me about rooms, dining, experiences, booking modifications, or special requests.",
        "For immediate assistance, call our 24/7 reception at +94 11 249 1000 or email reservations@cinnamonhotels.com",
    ],
    "booking": [
        "To make a booking, you can use our website's booking engine, call us directly, or I can help guide you through the process. When would you like to stay?",
        "Our best rates are available when you book direct! Check-in is at 2:00 PM and check-out is at 12:00 PM.",
    ],
    "spa": [
        "Our Angsana Spa offers traditional Ayurvedic treatments, aromatherapy, and rejuvenating massages in a tranquil setting.",
        "Spa services include body scrubs, facials, couple treatments, and wellness packages. Advance booking recommended.",
    ],
    "location": [
        "Cinnamon Hotels has properties across Sri Lanka - from Colombo's bustling city to the pristine beaches of Bentota and cultural heart of Kandy.",
        "Our hotels are strategically located near major attractions, with easy access to airports and key tourist destinations.",
    ],
    "offers": [
        "Current promotions include: Early Bird Discount (20% off), Extended Stay Offer (4th night free), and Honeymoon Package with complimentary spa.",
        "Subscribe to our newsletter for exclusive deals and seasonal offers. MICE groups and corporate rates also available.",
    ],
    "default": [
        "That's a great question! Let me help you with that. Could you please provide more details?",
        "I'm here to make your stay memorable. Would you like information about our rooms, dining, or experiences?",
        "Thank you for your interest in Cinnamon Hotels. How may I assist you today?",
    ]
}

GREETINGS = [
    "Hello and welcome to Cinnamon Hotels & Resorts! I'm your virtual concierge. How can I help you today?",
    "Welcome to Cinnamon Hotels! I'm delighted to assist you with your stay. What would you like to know?",
]


def get_response_category(message):
    """Determine response category based on message content"""
    message_lower = message.lower()

    if any(word in message_lower for word in ['room', 'suite', 'accommodation', 'stay']):
        return 'rooms'
    elif any(word in message_lower for word in ['eat', 'food', 'restaurant', 'meal']):
        return 'eat'
    elif any(word in message_lower for word in ['dining', 'dinner', 'lunch', 'breakfast', 'bar', 'drink']):
        return 'dining'
    elif any(word in message_lower for word in ['explore', 'tour', 'activity', 'excursion', 'experience']):
        return 'explore'
    elif any(word in message_lower for word in ['help', 'assist', 'support', 'contact']):
        return 'help'
    elif any(word in message_lower for word in ['book', 'reservation', 'reserve', 'check-in', 'check-out']):
        return 'booking'
    elif any(word in message_lower for word in ['spa', 'massage', 'wellness', 'ayurveda']):
        return 'spa'
    elif any(word in message_lower for word in ['location', 'where', 'address', 'directions']):
        return 'location'
    elif any(word in message_lower for word in ['offer', 'promotion', 'deal', 'discount', 'price']):
        return 'offers'
    else:
        return 'default'


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Check if it's a greeting
    if any(word in user_message.lower() for word in ['hi', 'hello', 'hey', 'greetings']):
        response = random.choice(GREETINGS)
    else:
        # Get appropriate response based on message content
        category = get_response_category(user_message)
        response = random.choice(MOCK_RESPONSES[category])

    return jsonify({
        'response': response,
        'timestamp': '2025-10-10T12:00:00Z'
    })


@app.route('/api/quick-action', methods=['POST'])
def quick_action():
    """Handle quick action button clicks"""
    data = request.json
    action = data.get('action', '').lower()

    if action in MOCK_RESPONSES:
        response = random.choice(MOCK_RESPONSES[action])
    else:
        response = "I'm here to help! Please select an option or ask me a question."

    return jsonify({
        'response': response,
        'timestamp': '2025-10-10T12:00:00Z'
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Cinnamon Hotels Chatbot'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
