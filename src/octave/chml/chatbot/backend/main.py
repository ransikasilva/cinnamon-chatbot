"""Hotel booking chatbot FastAPI backend.

========================================================================================
 Copyright (c) 2025 OCTAVE. All rights reserved.

 This is proprietary and confidential software of OCTAVE.
 Unauthorized use, reproduction, or distribution is strictly prohibited.
========================================================================================
"""

import datetime
import logging
from typing import Dict, Optional

import fastapi
import pydantic
from fastapi.middleware import cors

from octave.chml.chatbot.backend.app.workflows.booking_workflow.agents import booking_agent as ba

logger = logging.getLogger(__name__)

app = fastapi.FastAPI(title="Hotel Booking Chatbot API")

# Enable CORS
app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the booking agent
booking_agent = ba.HotelBookingAgent()

# In-memory session storage (use Redis in production)
sessions: Dict[str, dict] = {}


class QueryRequest(pydantic.BaseModel):
    """Request model for user queries."""

    query: str
    session_id: str


class QueryResponse(pydantic.BaseModel):
    """Response model for user queries."""

    response: str
    show_form: bool = False
    prefilled_data: Optional[dict] = None
    reservation_url: Optional[str] = None


class ReservationRequest(pydantic.BaseModel):
    """Request model for hotel reservations."""

    session_id: str
    reservation_data: dict


@app.get("/")
def read_root():
    """Root endpoint returning API status."""
    return {"message": "Hotel Booking Chatbot API is running"}


@app.post("/process_query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
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

    response = QueryResponse(
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
            response.reservation_url = generate_reservation_url(booking_data)

    return response


@app.post("/process_reservation")
async def process_reservation(request: ReservationRequest):
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
    reservation_url = generate_reservation_url(booking_data)

    return {"reservation_url": reservation_url}


def generate_reservation_url(booking_data: dict) -> str:
    """Generate Cinnamon Hotels reservation URL with query parameters."""
    base_url = "https://reservations.cinnamonhotels.com/"

    # Format dates for URL (YYYY-MM-DD)
    check_in = booking_data["check_in"]
    check_out = booking_data["check_out"]

    # Build URL with query parameters
    url = f"{base_url}?adult={booking_data['adults']}"
    url += f"&arrive={check_in}"
    url += f"&chain={booking_data['chain_id']}"
    url += f"&child={booking_data['children']}"
    url += "&currency=USD"
    url += f"&depart={check_out}"
    url += f"&hotel={booking_data['property_id']}"
    url += "&level=hotel"
    url += "&locale=en-US"
    url += "&productcurrency=USD"
    url += f"&rooms={booking_data['rooms']}"
    url += "&segment=BB"

    return url


@app.get("/health")
def health_check():
    """Health check endpoint returning service status."""
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
