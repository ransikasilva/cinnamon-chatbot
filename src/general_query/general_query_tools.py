import json
import os
import sys
from langchain_core.tools import tool

# Add parent directory to sys.path to import models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models import get_llm


@tool
def get_hotel_info(query: str = None) -> str:
    """Get information about our hotels and properties."""
    try:
        properties = []

        info_text = (
            "🏨 **Welcome to Cinnamon Hotels!** Here are our beautiful properties:\n\n"
        )

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
def handle_general_query(question: str, data: dict = None) -> str:
    """Handle general questions about hotels, services, policies, offers, etc.
    Uses LLM to generate contextual responses based on available data.
    
    Args:
        question (str): User's question about hotels, services, policies, etc.
        data (dict, optional): Custom data to override default dummy data
        
    Returns:
        str: LLM-generated response based on the question and available data
    """
    try:
        # Default comprehensive hotel data (can be overridden by passing data parameter)
        default_data = {
            "properties": [
                {
                    "name": "Cinnamon Bey Beruwala",
                    "location": "Beruwala, Sri Lanka",
                    "type": "Beach Resort",
                    "description": "A stunning beachfront resort offering pristine beaches, luxury accommodations, and family-friendly activities.",
                    "amenities": ["Private beach access", "Swimming pools", "Spa services", "Water sports", "Kids' club", "Free WiFi", "24/7 room service"],
                    "dining": ["Multiple restaurants with ocean views", "International and local cuisine", "Pool bar and beach service", "All-inclusive packages available"],
                    "activities": ["Water sports", "Beach volleyball", "Cultural shows", "Kids' activities", "Spa treatments"],
                    "room_types": ["Deluxe Ocean View", "Family Suite", "Premium Beach Villa"],
                    "features": ["Private beach", "Spa", "Water sports", "Kids' club"]
                },
                {
                    "name": "Cinnamon Lakeside Colombo",
                    "location": "Colombo, Sri Lanka", 
                    "type": "City Hotel",
                    "description": "An elegant city hotel overlooking Beira Lake with modern amenities and business facilities.",
                    "amenities": ["Executive lounge", "Meeting rooms", "Airport transfers", "Free WiFi", "Fitness center", "Business center"],
                    "dining": ["Fine dining restaurant", "Casual café and bar", "Room service available", "Business lunch options"],
                    "activities": ["City tour arrangements", "Business meetings", "Lake views", "Shopping assistance"],
                    "room_types": ["Executive Room", "Lake View Suite", "Business Room"],
                    "features": ["Executive lounge", "Meeting rooms", "Airport transfers"]
                }
            ],
            "policies": {
                "cancellation": "Free cancellation up to 24 hours before check-in. Late cancellations may incur charges.",
                "check_in": "3:00 PM (Early check-in subject to availability)",
                "check_out": "12:00 PM (Late check-out subject to availability)",
                "payment": "Major credit cards accepted. Security deposit may be required at check-in.",
                "children": "Children under 12 stay free when sharing with parents (maximum 2 children per room)",
                "pets": "Pet-friendly rooms available upon request with advance notice"
            },
            "offers": [
                {
                    "title": "Early Bird Special",
                    "details": "Book 30 days in advance and save 25% on room rates",
                    "validity": "Valid for stays throughout the year"
                },
                {
                    "title": "Weekend Getaway Package", 
                    "details": "Complimentary breakfast and late checkout for weekend bookings",
                    "validity": "Friday to Sunday stays"
                },
                {
                    "title": "Family Fun Package",
                    "details": "Free meals for children under 12 and complimentary access to kids' activities",
                    "validity": "Available at Cinnamon Bey Beruwala"
                },
                {
                    "title": "Business Traveler Deal",
                    "details": "Airport transfers included and access to executive lounge",
                    "validity": "Available at Cinnamon Lakeside Colombo"
                }
            ],
            "services": {
                "concierge": "24/7 concierge services for tour bookings, transportation, and local recommendations",
                "spa": "Full-service spa with traditional Sri Lankan treatments and modern wellness facilities",
                "dining": "Multiple dining venues offering international cuisine, local specialties, and dietary accommodations",
                "business": "Fully equipped business center with meeting rooms and conference facilities",
                "recreation": "Swimming pools, fitness centers, water sports, and cultural activities"
            }
        }

        # Merge provided data with defaults if data parameter is passed
        if data:
            for key, value in data.items():
                default_data[key] = value

        # Create comprehensive LLM prompt for general queries
        query_prompt = f"""You are a knowledgeable and friendly hotel concierge at Cinnamon Hotels. Answer the user's question using the provided hotel data.

USER'S QUESTION: "{question}"

HOTEL DATA:
{json.dumps(default_data, indent=2)}

GUIDELINES:
- Provide accurate, helpful information based on the data provided
- Be conversational, warm, and professional - as if speaking to a valued guest
- Use the hotel data naturally in your response, don't just list it verbatim
- Include relevant emojis and formatting to make responses engaging
- If the question is about specific policies, offers, or services, focus on those areas
- If comparing properties, highlight key differences and help the user choose
- If the user asks about something not in the data, acknowledge it honestly and offer to connect them with reservations
- Keep responses helpful and comprehensive but not overwhelming
- Always end with a helpful follow-up question or offer to assist further
- Format your response with clear sections and bullet points when appropriate
- If you are not sure about something, do not make up an answer. Instead, politely inform the user that you do not have that information and suggest contacting the reservations team for further assistance.

RESPOND DIRECTLY TO THE USER'S QUESTION:"""

        # Get LLM response
        llm = get_llm()
        response = llm.invoke(query_prompt)
        response_text = response.content if hasattr(response, "content") else str(response)
        
        return response_text
        
    except Exception as e:
        print(f"Error in general query processing: {e}")
        return f"""I apologize, but I encountered an issue processing your question about: {question}

I'm here to help with:
🏨 Hotel information and amenities
📅 Making new reservations  
📝 Existing booking changes
🍽️ Dining and services
📋 Policies and procedures
🎁 Current offers and promotions

Please try asking again, or feel free to contact our reservations team directly at reservations@cinnamonhotels.com for immediate assistance."""
