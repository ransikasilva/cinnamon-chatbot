"""Chatbot API endpoints.

========================================================================================
 Copyright (c) 2025 OCTAVE. All rights reserved.

 This is proprietary and confidential software of OCTAVE.
 Unauthorized use, reproduction, or distribution is strictly prohibited.
========================================================================================
"""

import logging

import fastapi
from langchain_core import runnables

from octave.chml.chatbot.backend.app.schemas import requests, responses
from octave.chml.chatbot.backend.app.utils import helpers
from octave.chml.chatbot.backend.app.workflows.booking_workflow.agents import (
    booking_agent as ba,
)

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()

# Initialize the booking agent
booking_agent = ba.HotelBookingAgent()

# # In-memory session storage (use Redis in production)
# sessions: Dict[str, dict] = {}


@router.post("/process_query", response_model=responses.QueryResponse)
async def process_query(request: requests.QueryRequest):
    """Process user query through the booking agent"""
    session_id = request.session_id
    query = request.query

    logger.info("Processing message '%s' for thread_id: %s", query, session_id)

    # Process the message through the agent
    result = booking_agent.process_message(query, thread_id=session_id)

    response = responses.QueryResponse(
        response=result["response"],
        show_form=False,
        prefilled_data=None,
        reservation_url=None,
    )

    # Get the state
    state = result["state"]

    # Check for booking URL (for manage booking flow)
    if state.get("booking_url"):
        response.reservation_url = state["booking_url"]

        # Clear the booking_url from state to prevent repeated redirects
        config: runnables.RunnableConfig = {"configurable": {"thread_id": session_id}}
        booking_agent.graph.update_state(config, {"booking_url": None})

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

    return response


@router.post("/process_reservation")
async def process_reservation(request: requests.ReservationRequest):
    """Process final reservation with form data."""
    session_id = request.session_id
    reservation_data = request.reservation_data

    # Get current state from LangGraph checkpointer
    config = {"configurable": {"thread_id": session_id}}
    current_state = booking_agent.graph.get_state(config)  # type: ignore

    if not current_state.values or not current_state.values.get("selected_property"):
        return {"error": "Invalid session or no property selected"}

    # Prepare booking data
    selected_property = current_state.values["selected_property"]
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

    # Clear booking state to prevent repeated redirects and allow new bookings
    config_clear: runnables.RunnableConfig = {"configurable": {"thread_id": session_id}}
    booking_agent.graph.update_state(
        config_clear,
        {
            "ready_for_booking": False,
            "show_booking_form": False,
            "selected_property": None,
            "check_in_date": None,
            "check_out_date": None,
            "adults": None,
            "children": None,
            "rooms": None,
        },
    )

    return {"reservation_url": reservation_url}
