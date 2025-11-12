"""State implementations for the LangGraph graphs.

===============================================================================
    Copyright (c) 2025 OCTAVE. All rights reserved.

    This is proprietary and confidential software of OCTAVE.
    Unauthorized use, reproduction, or distribution is strictly prohibited.
===============================================================================
"""

from typing import Annotated, TypedDict

from langgraph.graph import message


class BookingState(TypedDict):
    """State for the booking conversation"""

    messages: Annotated[list, message.add_messages]
    destination: str | None
    property_preferences: str | None
    selected_property: dict | None
    check_in_date: str | None
    check_out_date: str | None
    adults: int | None
    children: int | None
    rooms: int | None
    ready_for_booking: bool
    # conversation_complete: bool
    show_booking_form: bool
    manage_booking_url: str | None  # URL for booking redirection
    _recommendations: list | None  # Temporary storage for property recommendations
    _intent: str | None  # User intent classification: booking, info_query, general
    _conversation_summary: str | None  # Summary of conversation so far for context
