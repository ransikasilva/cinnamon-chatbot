"""Conditional edge implementations for LangGraph graphs.

===============================================================================
    Copyright (c) 2025 OCTAVE. All rights reserved.

    This is proprietary and confidential software of OCTAVE.
    Unauthorized use, reproduction, or distribution is strictly prohibited.
===============================================================================
"""

import json
import logging
from typing import Literal, TypeAlias

from octave.chml.chatbot.backend.app.workflows.booking_workflow.graph import states

BookingState: TypeAlias = states.BookingState

logger = logging.getLogger(__name__)


def route_after_destination(
    state: BookingState,
) -> Literal["check_property", "ask_destination"]:
    """Route based on whether we have destination"""

    logger.debug(
        "=== ROUTING: route_after_destination -> destination=%s ===",
        state.get("destination"),
    )
    if state.get("destination"):
        return "check_property"
    return "ask_destination"


def route_after_property(
    state: BookingState, llm
) -> Literal["check_booking_details", "ask_property"]:
    """Route based on whether we have property selected"""
    logger.debug(
        "=== ROUTING: route_after_property -> selected_property=%s ===",
        (
            state.get("selected_property")["name"]
            if state.get("selected_property")
            else None
        ),
    )
    if state.get("selected_property"):
        return "check_booking_details"

    # Check if user selected a property from recommendations
    if state.get("_recommendations"):
        last_message = state["messages"][-1].content.lower()

        # Use LLM to determine which property user selected
        selection_prompt = f"""User message: "{last_message}"

        Available properties:
        {json.dumps(state['_recommendations'], indent=2)}

        Did the user select a property? If yes, return the property ID. If no, return null.
        Return ONLY: the property ID string (like "46401") or null, nothing else."""

        response = llm.invoke(selection_prompt)
        property_id = response.content.strip().strip('"')

        if property_id and property_id != "null":
            # Find and set the selected property
            selected = None
            recommendations = state.get("_recommendations")
            if recommendations:
                selected = next(
                    (p for p in recommendations if p["id"] == property_id),
                    None,
                )
            if selected:
                state["selected_property"] = selected
                return "check_booking_details"

    return "ask_property"


def route_after_booking_details(
    state: BookingState,
) -> Literal["finalize", "ask_details"]:
    """Route based on whether we have all booking details"""
    logger.debug(
        "=== ROUTING: route_after_booking_details -> ready_for_booking=%s ===",
        state.get("ready_for_booking"),
    )
    if state.get("ready_for_booking"):
        return "finalize"
    return "ask_details"


def route_by_intent(
    state: BookingState,
) -> Literal["handle_general", "handle_info", "manage_booking", "continue_booking"]:
    """Route to appropriate node based on classified intent."""
    intent = state.get("_intent", "booking")

    logger.debug(
        "=== ROUTING: route_by_intent -> intent=%s (from state._intent=%s) ===",
        intent,
        state.get("_intent"),
    )

    if intent == "general":
        return "handle_general"
    elif intent == "info_query":
        return "handle_info"
    elif intent == "manage_booking":
        return "manage_booking"
    else:
        # "booking" intent continues with booking flow
        return "continue_booking"
