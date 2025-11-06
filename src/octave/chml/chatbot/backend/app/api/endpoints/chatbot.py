"""Chatbot API endpoints.

========================================================================================
 Copyright (c) 2025 OCTAVE. All rights reserved.

 This is proprietary and confidential software of OCTAVE.
 Unauthorized use, reproduction, or distribution is strictly prohibited.
========================================================================================
"""
import logging
from typing import Dict

import fastapi

from octave.chml.chatbot.backend.app.schemas import requests, responses
from octave.chml.chatbot.backend.app.workflows.booking_workflow.agents import booking_agent as ba
from octave.chml.chatbot.backend.app.utils import helpers

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()

# Initialize the booking agent
booking_agent = ba.HotelBookingAgent()

# In-memory session storage (use Redis in production)
sessions: Dict[str, dict] = {}


@router.post("/process_query", response_model=responses.QueryResponse)
async def process_query(request: requests.QueryRequest):
    """Process user query through the booking agent"""
    session_id = request.session_id
    query = request.query

    # Get or create session state
    session_state = sessions.get(session_id)

    logger.info(
        "Calling process_message %s with session state: %s", query, session_state
    )
    # Process the message through the agent
    result = booking_agent.process_message(
        query, session_state if session_state is not None else {}
    )

    # Update session
    sessions[session_id] = result["state"]

    response = responses.QueryResponse(
        response=result["response"],
        show_form=False,
        prefilled_data=None,
        reservation_url=None,
    )

    # Get the state
    state = result["state"]

    # Check if we should show the booking form
    if state.get("show_booking_form") and state.get("selected_property"):
        response.show_form = True
        response.prefilled_data = {
            "checkIn": state.get("check_in_date", ""),
            "checkOut": state.get("check_out_date", ""),
            "adults": state.get("adults") if state.get("adults") else 1,
            "children": (
                state.get("children") if state.get("children") is not None else 0
            ),
            "rooms": state.get("rooms") if state.get("rooms") else 1,
        }

    # If ready for booking with complete data, prepare the URL
    if result.get("ready_for_booking") and result.get("booking_data"):
        booking_data = result["booking_data"]

        # Check if we have all required data for direct URL
        if all(
            [
                booking_data.get("property_id"),
                booking_data.get("chain_id"),
                booking_data.get("check_in"),
                booking_data.get("check_out"),
                booking_data.get("adults"),
            ]
        ):
            # Generate reservation URL
            response.reservation_url = helpers.generate_reservation_url(booking_data)

    return response


@router.post("/process_reservation")
async def process_reservation(request: requests.ReservationRequest):
    """Process final reservation with form data."""
    session_id = request.session_id
    reservation_data = request.reservation_data

    # Get session state
    session_state = sessions.get(session_id)

    if not session_state or not session_state.get("selected_property"):
        return {"error": "Invalid session or no property selected"}

    # Prepare booking data
    selected_property = session_state["selected_property"]
    booking_data = {
        "property_id": selected_property["id"],
        "chain_id": selected_property["chain_id"],
        "check_in": reservation_data.get("checkIn"),
        "check_out": reservation_data.get("checkOut"),
        "adults": reservation_data.get("adults", 1),
        "children": reservation_data.get("children", 0),
        "rooms": reservation_data.get("rooms", 1),
    }

    logger.info("Finalizing booking with data: %s", booking_data)

    # Generate reservation URL
    reservation_url = helpers.generate_reservation_url(booking_data)

    return {"reservation_url": reservation_url}
