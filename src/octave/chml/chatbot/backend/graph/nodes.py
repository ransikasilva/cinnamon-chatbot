"""Node implementations for LangGraph graphs.

===============================================================================
    Copyright (c) 2025 OCTAVE. All rights reserved.

    This is proprietary and confidential software of OCTAVE.
    Unauthorized use, reproduction, or distribution is strictly prohibited.
===============================================================================
"""

import datetime
import json
import logging
from typing import TypeAlias

from langchain_core import messages

from octave.chml.chatbot.backend.graph import states

BookingState: TypeAlias = states.BookingState

logger = logging.getLogger(__name__)


def extract_booking_info_node(state: BookingState, hotels_data, llm) -> BookingState:
    """Extract booking information from the user's message using the LLM."""
    logger.debug("EXECUTING: extract_booking_info_node.")

    last_message = state["messages"][-1].content

    # Get current date for relative date parsing.
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Get available hotels for context.
    available_hotels = []
    for dest in hotels_data["destinations"]:
        for hotel in dest["properties"]:
            available_hotels.append(
                {
                    "id": hotel["id"],
                    "name": hotel["name"],
                    "destination": dest["name"],
                    "location": hotel["location"],
                }
            )

    # If there are recommendations, include them prominently in the prompt/
    recommendations_context = ""
    if state.get("_recommendations") and not state.get("selected_property"):
        recommendations_context = f"""
        IMPORTANT: The user was just shown these specific hotel recommendations and 
        may be selecting one by number or name:
        {json.dumps(state["_recommendations"], indent=2)}

        If the user's message is a number (1, 2, 3), map it to the corresponding 
        hotel from the recommendations above.
        If the user mentions a hotel name, match it against the recommendations 
        first.
        """

    extraction_prompt = f"""You are an information extraction assistant for a hotel
     booking system.
    Current date: {current_date}

    {recommendations_context}

    Extract the following information from the user's message. If information is not 
    present, return null.

    Available destinations: Sri Lanka, Maldives

    Available hotels:
    {json.dumps(available_hotels, indent=2)}

    User message: "{last_message}"

    Previous conversation context:
    - Current destination: {state.get('destination')}
    - Current property preferences: {state.get('property_preferences')}
    - Current check-in: {state.get('check_in_date')}
    - Current check-out: {state.get('check_out_date')}
    - Current adults: {state.get('adults')}
    - Current children: {state.get('children')}
    - Current rooms: {state.get('rooms')}

    Extract and return ONLY a JSON object with these fields:
    {{
        "destination": "Sri Lanka" or "Maldives" or null,
        "property_preferences": "description of what they're looking for" or null,
        "selected_hotel_id": "hotel ID if user mentioned a specific hotel name OR 
        selected by number" or null,
        "check_in_date": "YYYY-MM-DD" or null,
        "check_out_date": "YYYY-MM-DD" or null,
        "adults": number or null,
        "children": number or null,
        "rooms": number or null
    }}

    Important:
    - For dates: Convert relative dates like "next weekend", "tomorrow", "next week"
        to actual YYYY-MM-DD format
    - For adults: Extract number of adults/guests (default assumptions: "I" =
        1 adult, "we" might be 2 adults)
    - For children: Look for mentions of kids, children, or specific numbers
    - For property_preferences: Extract general preferences like "beach", "city",
        "luxury", "family-friendly" ONLY if no specific hotel is mentioned
    - For selected_hotel_id:
    * If recommendations are present and user says a number (1, 2, 3), return the
        ID of that numbered hotel from the recommendations
    * If user mentions a specific hotel name, return the matching hotel ID
    * Otherwise return null
    - Return ONLY the JSON object, no other text."""

    response = llm.invoke(extraction_prompt)

    try:
        extracted_data = json.loads(str(response.content))
    except json.JSONDecodeError:
        # If parsing fails, continue with existing state
        return state

    logger.debug("EXTRACTED INFO: %s", extracted_data)
    logger.debug("BOOKING STATE BEFORE UPDATE: %s", state)

    # Update state with extracted information (only if not null).
    if extracted_data.get("destination"):
        state["destination"] = extracted_data["destination"]

    if extracted_data.get("property_preferences"):
        # Append to existing preferences if any
        if state.get("property_preferences"):
            if state["property_preferences"] is not None:
                state[
                    "property_preferences"
                ] += f" {extracted_data['property_preferences']}"
            else:
                state["property_preferences"] = extracted_data["property_preferences"]
        else:
            state["property_preferences"] = extracted_data["property_preferences"]

    # Handle selected hotel ID
    if extracted_data.get("selected_hotel_id") and not state.get("selected_property"):
        hotel_id = extracted_data["selected_hotel_id"]
        # Find the hotel across all destinations
        for dest in hotels_data["destinations"]:
            for hotel in dest["properties"]:
                if hotel["id"] == hotel_id:
                    state["selected_property"] = hotel
                    state["destination"] = dest["name"]  # Also set destination
                    logger.debug("SELECTED PROPERTY BY LLM: %s", hotel['name'])
                    break
            if state.get("selected_property"):
                break

    if extracted_data.get("check_in_date"):
        state["check_in_date"] = extracted_data["check_in_date"]
    if extracted_data.get("check_out_date"):
        state["check_out_date"] = extracted_data["check_out_date"]
    if extracted_data.get("adults"):
        state["adults"] = extracted_data["adults"]
    if extracted_data.get("children"):
        state["children"] = extracted_data["children"]
    if extracted_data.get("rooms"):
        state["rooms"] = extracted_data["rooms"]

    return state


def check_destination_node(state: BookingState) -> BookingState:
    """Check if we have destination, if not ask for it"""
    logger.debug("=== EXECUTING: check_destination_node ===")

    if not state.get("destination"):
        # Ask for destination
        response = (
            "I'd be happy to help you book a hotel! We have beautiful "
            + "properties in Sri Lanka and the Maldives. "
            + "Which destination interests you?"
        )
        state["messages"].append(messages.AIMessage(content=response))
        state["conversation_complete"] = False

    return state


def check_property_node(state: BookingState, hotels_data, llm) -> BookingState:
    """Check if we have property preferences and recommend hotels"""
    logger.debug("=== EXECUTING: check_property_node ===")
    if not state.get("selected_property"):
        # Get hotels for the destination
        destination_data = next(
            (
                d
                for d in hotels_data["destinations"]
                if d["name"] == state["destination"]
            ),
            None,
        )

        if not destination_data:
            state["messages"].append(
                messages.AIMessage(
                    content="I'm sorry, I couldn't find that destination."
                )
            )
            state["conversation_complete"] = False
            return state

        properties = destination_data["properties"]

        # If we have preferences, use LLM to match properties
        if state.get("property_preferences"):
            matching_prompt = f"""You are a hotel recommendation assistant.

            User preferences: {state['property_preferences']}
            User destination: {state['destination']}

            Available hotels:
            {json.dumps(properties, indent=2)}

            Based on the user's preferences recommend the most matching hotels.
                Could be one or more
            Return ONLY a JSON array of hotel IDs in order of relevance, 
            like: ["46401", "46403", "46402"]

            Consider the hotel's type, description, location, preferences tags,
                and amenities when matching."""

            response = llm.invoke(matching_prompt)

            try:
                recommended_ids = json.loads(str(response.content))
                recommended_hotels = [
                    h for h in properties if h["id"] in recommended_ids
                ]
                # Sort by the order in recommended_ids
                recommended_hotels.sort(key=lambda x: recommended_ids.index(x["id"]))
            except (json.JSONDecodeError, TypeError):
                # Fallback: return first 3 hotels
                recommended_hotels = properties[:3]
        else:
            # No preferences yet, ask what they're looking for
            hotel_list = "\n".join(
                [f"- {h['name']}: {h['description']}" for h in properties]
            )
            response = f"""Great choice! We have several wonderful properties
                in {state['destination']}:

            {hotel_list}

            What type of experience are you looking for? (e.g., beachfront, 
            city center, nature retreat, luxury, family-friendly)"""

            state["messages"].append(messages.AIMessage(content=response))
            state["conversation_complete"] = False
            return state

        # Present recommendations
        recommendations_text = "\n\n".join(
            [
                f"{i+1}. **{h['name']}** ({h['location']})\n   {h['description']}"
                for i, h in enumerate(recommended_hotels)
            ]
        )

        response = f"""Based on your preferences, I recommend these properties
         in {state['destination']}:

        {recommendations_text}

        Which property would you like to book? (You can tell me the number or name)"""

        state["messages"].append(messages.AIMessage(content=response))
        state["conversation_complete"] = False

        # Store recommendations for next interaction
        state["_recommendations"] = recommended_hotels

    return state


def check_booking_details_node(state: BookingState) -> BookingState:
    """Check if we have all booking details"""
    logger.debug("=== EXECUTING: check_booking_details_node ===")

    # Signal that form should be shown since we have property selected
    state["show_booking_form"] = True

    missing_details = []

    if not state.get("check_in_date"):
        missing_details.append("check-in date")
    if not state.get("check_out_date"):
        missing_details.append("check-out date")
    if not state.get("adults"):
        missing_details.append("number of guests")
    if state.get("rooms") is None:
        missing_details.append("number of rooms")

    if missing_details:
        # Inform user that a form will be shown
        response = f"Perfect! I'll show you a booking form for **{state['selected_property']['name']}**. "
        response += "Please fill in the remaining details to complete your reservation."

        state["messages"].append(messages.AIMessage(content=response))
        state["conversation_complete"] = False
    else:
        # We have all details, ready for booking
        state["ready_for_booking"] = True

    return state


def finalize_node(state: BookingState) -> BookingState:
    """Prepare final response with booking details"""
    logger.debug("=== EXECUTING: finalize_node ===")
    property_info = state["selected_property"]

    # Set defaults
    if state.get("children") is None:
        state["children"] = 0
    if state.get("rooms") is None:
        state["rooms"] = 1

    response = f"""Excellent! I have all the details for your booking:

🏨 **Hotel:** {property_info['name']}
📍 **Location:** {property_info['location']}, {state['destination']}
📅 **Check-in:** {state['check_in_date']}
📅 **Check-out:** {state['check_out_date']}
👥 **Guests:** {state['adults']} adult(s)"""

    if state["children"] is not None and state["children"] > 0:
        response += f", {state['children']} child(ren)"

    response += f"\n🚪 **Rooms:** {state['rooms']}"
    response += (
        "\n\nI'll now open the booking page for you to complete your reservation!"
    )

    state["messages"].append(messages.AIMessage(content=response))
    state["conversation_complete"] = True
    state["ready_for_booking"] = True

    return state
