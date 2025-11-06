"""Hotel booking conversation agent using LangGraph state management.

========================================================================================
 Copyright (c) 2025 OCTAVE. All rights reserved.

 This is proprietary and confidential software of OCTAVE.
 Unauthorized use, reproduction, or distribution is strictly prohibited.
========================================================================================
"""

import json
import logging
import pathlib
from typing import Optional

from langchain_core import messages

from octave.chml.chatbot.backend import models
from octave.chml.chatbot.backend.graph import graph_defs

logger = logging.getLogger(__name__)


class HotelBookingAgent:
    """Hotel booking agent using LangGraph for state management"""

    def __init__(self):
        self.llm = models.get_llm()

        hotel_data_path = (
            pathlib.Path(__file__).parents[0] / "resources" / "hotels_data.json"
        )

        # Load hotels data
        with open(hotel_data_path, "r", encoding="utf-8") as f:
            self.hotels_data = json.load(f)

        # Build the graph
        self.graph = graph_defs.build_booking_graph(self.hotels_data, self.llm)

    def process_message(
        self, user_message: str, session_state: Optional[dict] = None
    ) -> dict:
        """Process a user message and return response"""
        # Initialize or load state
        if session_state is None or not session_state:
            state = {
                "messages": [messages.HumanMessage(content=user_message)],
                "destination": None,
                "property_preferences": None,
                "selected_property": None,
                "check_in_date": None,
                "check_out_date": None,
                "adults": None,
                "children": None,
                "rooms": None,
                "ready_for_booking": False,
                "conversation_complete": False,
            }
        else:
            state = session_state.copy()
            # Ensure messages key exists
            if "messages" not in state:
                state["messages"] = []
            state["messages"].append(messages.HumanMessage(content=user_message))

        # Run the graph
        result = self.graph.invoke(state)  # type: ignore

        # Extract the last AI message
        ai_messages = [
            m for m in result["messages"] if isinstance(m, messages.AIMessage)
        ]
        last_response = (
            ai_messages[-1].content
            if ai_messages
            else "I'm here to help you book a hotel!"
        )

        return {
            "response": last_response,
            "state": result,
            "ready_for_booking": result.get("ready_for_booking", False),
            "conversation_complete": result.get("conversation_complete", False),
            "booking_data": (
                {
                    "property_id": (
                        result["selected_property"]["id"]
                        if result.get("selected_property")
                        else None
                    ),
                    "property_name": (
                        result["selected_property"]["name"]
                        if result.get("selected_property")
                        else None
                    ),
                    "chain_id": (
                        result["selected_property"]["chain_id"]
                        if result.get("selected_property")
                        else None
                    ),
                    "check_in": result.get("check_in_date"),
                    "check_out": result.get("check_out_date"),
                    "adults": result.get("adults"),
                    "children": result.get("children", 0),
                    "rooms": result.get("rooms", 1),
                }
                if result.get("ready_for_booking")
                else None
            ),
        }
