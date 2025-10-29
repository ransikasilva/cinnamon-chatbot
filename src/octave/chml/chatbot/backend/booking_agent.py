"""Hotel booking conversation agent using LangGraph state management.

========================================================================================
 Copyright (c) 2025 OCTAVE. All rights reserved.

 This is proprietary and confidential software of OCTAVE.
 Unauthorized use, reproduction, or distribution is strictly prohibited.
========================================================================================
"""

import functools
import json
import logging
import pathlib
from typing import Optional

from langchain_core import messages
from langgraph import graph

from octave.chml.chatbot.backend import models
from octave.chml.chatbot.backend.graph import edges, nodes, states

logger = logging.getLogger(__name__)


class HotelBookingAgent:
    """Hotel booking agent using LangGraph for state management"""

    def __init__(self):
        self.llm = models.get_llm()

        hotel_data_path = (
            pathlib.Path(__file__).parents[5] / "resources" / "hotels_data.json"
        )

        # Load hotels data
        with open(hotel_data_path, "r", encoding="utf-8") as f:
            self.hotels_data = json.load(f)

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = graph.StateGraph(states.BookingState)

        # Add nodes
        workflow.add_node(
            "extract_booking_info",
            functools.partial(
                nodes.extract_booking_info_node,
                hotels_data=self.hotels_data,
                llm=self.llm,
            ),
        )
        workflow.add_node("check_destination", nodes.check_destination_node)
        workflow.add_node(
            "check_property",
            functools.partial(
                nodes.check_property_node,
                hotels_data=self.hotels_data,
                llm=self.llm,
            ),
        )
        workflow.add_node("check_booking_details", nodes.check_booking_details_node)
        workflow.add_node("finalize", nodes.finalize_node)

        # Set entry point
        workflow.set_entry_point("extract_booking_info")

        # Add edges
        workflow.add_edge("extract_booking_info", "check_destination")
        workflow.add_conditional_edges(
            "check_destination",
            edges.route_after_destination,
            {"check_property": "check_property", "ask_destination": graph.END},
        )
        workflow.add_conditional_edges(
            "check_property",
            functools.partial(edges.route_after_property, llm=self.llm),
            {
                "check_booking_details": "check_booking_details",
                "ask_property": graph.END,
            },
        )
        workflow.add_conditional_edges(
            "check_booking_details",
            edges.route_after_booking_details,
            {"finalize": "finalize", "ask_details": graph.END},
        )
        workflow.add_edge("finalize", graph.END)

        return workflow.compile()

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
