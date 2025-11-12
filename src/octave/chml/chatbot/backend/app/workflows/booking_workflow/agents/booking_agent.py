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

from langchain_core import messages
from langgraph.checkpoint.memory import MemorySaver

from octave.chml.chatbot.backend.app.services import llm_service
from octave.chml.chatbot.backend.app.workflows.booking_workflow.graph import graph_defs

logger = logging.getLogger(__name__)


class HotelBookingAgent:
    """Hotel booking agent using LangGraph for state management"""

    def __init__(self, checkpointer=None):
        """Initialize the booking agent with optional checkpointer.

        Args:
            checkpointer: Optional LangGraph checkpointer (defaults to MemorySaver).
                         Can be replaced with SqliteSaver, RedisSaver, etc.
        """
        self.llm = llm_service.get_llm()

        hotel_data_path = (
            pathlib.Path(__file__).parents[4] / "resources" / "hotels_data.json"
        )

        # Load hotels data
        with open(hotel_data_path, "r", encoding="utf-8") as f:
            self.hotels_data = json.load(f)

        # Use provided checkpointer or default to MemorySaver
        self.checkpointer = checkpointer if checkpointer is not None else MemorySaver()

        # Build the graph
        self.graph = graph_defs.build_booking_graph(
            self.hotels_data, self.llm, self.checkpointer
        )

    def process_message(self, user_message: str, thread_id: str) -> dict:
        """Process a user message using LangGraph's thread-based state management.

        Args:
            user_message: The user's message to process.
            thread_id: Unique identifier for the conversation thread (e.g., session_id).
                      LangGraph will automatically load/save state for this thread.

        Returns:
            dict with response, state, and booking information.
        """
        # Create configuration with thread_id for state persistence
        config = {"configurable": {"thread_id": thread_id}}

        # Create input with new user message
        # LangGraph will automatically merge with existing state from checkpointer
        input_state = {"messages": [messages.HumanMessage(content=user_message)]}

        # Run the graph with thread configuration
        # LangGraph will automatically load previous state and save new state
        result = self.graph.invoke(input_state, config=config)  # type: ignore

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
            # "conversation_complete": result.get("conversation_complete", False),
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
