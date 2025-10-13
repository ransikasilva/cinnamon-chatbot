from flask import Flask, request, jsonify
from flask_cors import CORS
from simple_responses import get_response, DEFAULT_GREETINGS
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with simple response mapping"""
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Normalize apostrophes at the entry point - handle various apostrophe encodings
    user_message = (user_message
                   .replace('\u2019', "'")  # Right single quotation mark
                   .replace('\u2018', "'")  # Left single quotation mark
                   .replace('`', "'")       # Backtick
                   .replace("'", "'")       # Another variant
                   .replace("'", "'")       # Another variant
                   .replace('�', "'"))      # Replacement character (encoding error)

    print(f"DEBUG: User message received: {repr(user_message)}")

    # Check if it's a greeting
    if any(word in user_message.lower() for word in ['hi', 'hello', 'hey', 'greetings']):
        response_text = random.choice(DEFAULT_GREETINGS)
        return jsonify({
            'type': 'text',
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        })

    # Get simple response
    response_data = get_response(user_message)
    print(f"DEBUG: Response data: {response_data}")

    # Handle structured vs text responses
    if response_data.get('type') == 'structured':
        return jsonify({
            'type': 'structured',
            'data': response_data,
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'type': 'text',
            'response': response_data.get('response', 'I apologize, I could not understand that.'),
            'show_map_button': response_data.get('show_map_button', False),
            'timestamp': datetime.now().isoformat()
        })


@app.route('/api/quick-action', methods=['POST'])
def quick_action():
    """Handle quick action button clicks"""
    data = request.json
    action = data.get('action', '').lower()

    quick_responses = {
        'rooms': "We offer luxurious rooms across all our properties. What type of room are you interested in? Sea view, family suites, or executive rooms?",
        'spa': "Our Angsana Spa offers traditional Ayurvedic treatments, aromatherapy, and rejuvenating massages. Would you like to know about our spa packages?",
        'dining': "Experience fine dining at our award-winning restaurants. We offer Sri Lankan cuisine, international dishes, and themed dinner nights. What would you like to know?",
        'explore': "Discover Sri Lanka with our curated experiences - from temple tours to wildlife safaris. Would you like recommendations based on your interests?",
        'help': "I'm here to assist you! You can ask me about rooms, dining, experiences, or I can help you plan your entire trip. What would you like to know?"
    }

    response_text = quick_responses.get(action, "I'm here to help! Please select an option or ask me a question.")

    return jsonify({
        'type': 'text',
        'response': response_text,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Cinnamon Hotels Chatbot'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)

