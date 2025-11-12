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

from octave.chml.chatbot.backend.app.utils import weather_tools
from octave.chml.chatbot.backend.app.workflows.booking_workflow.graph import states

BookingState: TypeAlias = states.BookingState

# Configure logging to only show DEBUG from our modules
logging.basicConfig(
    level=logging.WARNING,  # Set root logger to WARNING to suppress most external logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Set our specific modules to DEBUG level
octave_logger = logging.getLogger("octave")
octave_logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


def extract_booking_info_node(state: BookingState, hotels_data, llm) -> BookingState:
    """Extract booking information from the user's message using the LLM."""
    logger.debug("=== EXECUTING: extract_booking_info_node ===")

    convo_summary = state.get("_conversation_summary", "")

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

    Conversation Summary: "{convo_summary}"
    Users Message: "{state['messages'][-1].content}"

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
    # logger.debug("BOOKING STATE BEFORE UPDATE: %s", state)

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
                    logger.debug("SELECTED PROPERTY BY LLM: %s", hotel["name"])
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
    logger.debug("Current destination: %s", state.get("destination"))

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


def classify_intent_node(state: BookingState, llm) -> BookingState:
    """Classify user intent: booking-related vs informational query."""
    logger.debug("=== EXECUTING: classify_intent_node ===")

    all_msgs = state["messages"]

    logger.debug("All Messages: %s", all_msgs)

    conversation_history = "\n".join(
        [
            f"{'User' if isinstance(m, messages.HumanMessage) else 'Assistant'}: {m.content}"
            for m in all_msgs[:-1]  # Exclude current message
        ]
    )

    # Update conversation summary for other nodes to use
    # if len(state["messages"]) % 2 == 0:  # Update summary every exchange
    summary_prompt = f"""Summarize this hotel booking conversation focusing on:
1. What the user wants (destination, preferences)
2. What has been discussed or decided
3. Current booking progress

Recent conversation:
{conversation_history}

Provide a concise summary:"""

    summary_response = llm.invoke(summary_prompt)
    state["_conversation_summary"] = summary_response.content.strip()
    logger.debug("Updated conversation summary: %s", state["_conversation_summary"])

    classification_prompt = f"""Analyze this user message and classify the intent.

Conversation Summary: "{state["_conversation_summary"]}"
Current Message: "{all_msgs[-1].content}"

Classify as ONE of:
1. "booking" - User is providing booking details, selecting options, or progressing booking
2. "info_query" - User is asking about amenities, policies, hotel info, prices, facilities, location details
3. "manage_booking" - User wants to manage/modify an existing booking, enter confirmation details, or access their reservation
4. "general" - weather info, Greetings, clarifications, thanks, or other general conversation

Return ONLY ONE WORD: booking, info_query, manage_booking, or general"""

    response = llm.invoke(classification_prompt)
    intent = response.content.strip().lower()

    # Default to booking if unclear
    if intent not in ["booking", "info_query", "manage_booking", "general"]:
        intent = "booking"

    state["_intent"] = intent
    logger.debug("Classified intent: %s", intent)

    return state


def handle_info_query_node(state: BookingState, hotels_data, llm) -> BookingState:
    """Handle informational queries about hotels, amenities, policies, etc."""
    logger.debug("=== EXECUTING: handle_info_query_node ===")

    last_message = state["messages"][-1].content

    # Use conversation summary if available, otherwise build context
    conversation_summary = state.get("_conversation_summary", "")
    context = ""
    # Add conversation summary for context
    if conversation_summary:
        context += f"Conversation so far: {conversation_summary}\n\n"

    info_prompt = f"""You are a helpful hotel booking assistant. Answer the user's question using the provided context.

Context:
{context}

User question: "{last_message}"

Hotels Data: {json.dumps(hotels_data, indent=2)}
Provide a helpful, friendly, and concise answer based on the context and the given info. 
If you don't have specific information, say so politely and offer to help with what you do know.

After answering, gently ask if they'd like to continue with their booking or have other questions."""

    response = llm.invoke(info_prompt)

    state["messages"].append(messages.AIMessage(content=response.content))
    # Don't change booking state, just answer the question

    logger.debug("Info query answered, returning to conversation flow")

    return state


def manage_booking_node(state: BookingState) -> BookingState:
    """Manage booking by showing message and preparing for redirection."""
    logger.debug("=== EXECUTING: manage_booking_node ===")

    # Set the booking URL
    booking_url = "https://reservations.cinnamonhotels.com/signin?_ga=2.127479821.1833670624.1762785086-2007558351.1762785086&_gl=1*1xzur26*_gcl_au*MTA1Mjc3NjgyMi4xNzE5OTkzNTUz&adult=1&arrive=2025-11-11&chain=31106&child=0&depart=2025-11-12&level=chain&locale=en-US&rooms=1"

    state["booking_url"] = booking_url

    response = """Perfect! To complete your booking, please:

📋 **Enter the following in the redirected window:**
   - Your itinerary or confirmation number
   - Item number (if applicable)
   - Email address

You will be redirected to the booking page to continue with your reservation."""

    state["messages"].append(messages.AIMessage(content=response))
    state["conversation_complete"] = True

    logger.debug("Booking management complete, URL set for redirection")

    return state


def handle_general_node(state: BookingState, llm) -> BookingState:
    """Handle general greetings, thanks, conversational messages, and weather queries."""
    logger.debug("=== EXECUTING: handle_general_node ===")

    last_message = state["messages"][-1].content
    conversation_summary = state.get("_conversation_summary", "")

    # Get all available tools and bind them to the LLM
    available_tools = weather_tools.get_weather_tools()
    llm_with_tools = llm.bind_tools(available_tools)

    general_prompt = f"""You are a friendly hotel booking assistant EXCLUSIVELY for Cinnamon Hotels.

Conversation Summary: "{conversation_summary}"
User Message: "{last_message}"

IMPORTANT RULES:
1. ONLY respond to greetings, thanks, clarifications, or topics related to Cinnamon Hotels, hotel bookings, travel to Sri Lanka/Maldives, or hospitality.
2. Use the available tools when needed to provide accurate information (e.g., weather queries about Sri Lanka or Maldives).
3. If the user asks about ANYTHING completely unrelated to Cinnamon Hotels or travel (e.g., sports, politics, cooking recipes, general knowledge, other hotels, etc.), politely decline with a message like:
   "I'm a specialized assistant for Cinnamon Hotels bookings. I can only help you with hotel reservations in Sri Lanka and the Maldives. How can I assist you with your hotel booking today?"

4. For greetings: Greet them warmly and offer to help with Cinnamon Hotels bookings.
5. For thanks: Acknowledge kindly and ask if there's anything else about Cinnamon Hotels you can help with.
6. For clarifications about hotels/bookings: Respond helpfully.

Keep your response friendly, concise, and focused on Cinnamon Hotels services.
"""

    response = llm_with_tools.invoke(general_prompt)

    # Check if the LLM wants to use tools
    if hasattr(response, "tool_calls") and response.tool_calls:
        # Execute tool calls
        tool_results = []
        tools_dict = {tool.name: tool for tool in available_tools}

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            logger.debug("Executing tool: %s with args: %s", tool_name, tool_args)

            if tool_name in tools_dict:
                tool_func = tools_dict[tool_name]
                tool_result = tool_func.invoke(tool_args)
                tool_results.append(tool_result)
            else:
                logger.warning("Unknown tool requested: %s", tool_name)

        # Have the LLM convert tool results to natural language
        if tool_results:
            tool_data = "\n\n".join(tool_results)

            natural_language_prompt = f"""You are a friendly hotel booking assistant for Cinnamon Hotels.

The user asked: "{last_message}"

Data retrieved from tools: {tool_data}

Convert this data into a natural, conversational response. Don not greet the user in the beginning because as this might be asked in the midst of the conversation.
After providing the information, ask if they need help with their hotel booking.

Keep the response concise and conversational."""

            final_response = llm.invoke(natural_language_prompt)
            state["messages"].append(messages.AIMessage(content=final_response.content))
        else:
            state["messages"].append(messages.AIMessage(content=response.content))
    else:
        # No tools needed, just return the response
        state["messages"].append(messages.AIMessage(content=response.content))

    logger.debug("General greeting/conversation handled")

    return state
