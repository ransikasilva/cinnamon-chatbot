"""Graph definitions.

===============================================================================
    Copyright (c) 2025 OCTAVE. All rights reserved.

    This is proprietary and confidential software of OCTAVE.
    Unauthorized use, reproduction, or distribution is strictly prohibited.
===============================================================================
"""

import functools

from langgraph import graph
from langgraph.checkpoint.memory import MemorySaver

from octave.chml.chatbot.backend.app.workflows.booking_workflow.graph import (
    edges,
    nodes,
    states,
)


def build_booking_graph(hotels_data: dict, llm, checkpointer=None):
    """Build the LangGraph workflow with flexible query handling and optional checkpointer."""
    workflow = graph.StateGraph(states.BookingState)

    # Add nodes
    workflow.add_node(
        "classify_intent",
        functools.partial(nodes.classify_intent_node, llm=llm),
    )
    workflow.add_node(
        "handle_info",
        functools.partial(
            nodes.handle_info_query_node,
            hotels_data=hotels_data,
            llm=llm,
        ),
    )
    workflow.add_node(
        "extract_booking_info",
        functools.partial(
            nodes.extract_booking_info_node,
            hotels_data=hotels_data,
            llm=llm,
        ),
    )
    workflow.add_node("check_destination", nodes.check_destination_node)
    workflow.add_node(
        "check_property",
        functools.partial(
            nodes.check_property_node,
            hotels_data=hotels_data,
            llm=llm,
        ),
    )
    workflow.add_node("check_booking_details", nodes.check_booking_details_node)
    workflow.add_node("finalize", nodes.finalize_node)

    # Set entry point - always classify intent first
    workflow.set_entry_point("classify_intent")

    # Route based on intent
    workflow.add_conditional_edges(
        "classify_intent",
        edges.route_by_intent,
        {
            "handle_info": "handle_info",
            "continue_booking": "extract_booking_info",
        },
    )

    # Info query loops back to allow more questions
    workflow.add_edge("handle_info", graph.END)

    # Normal booking flow
    workflow.add_edge("extract_booking_info", "check_destination")
    workflow.add_conditional_edges(
        "check_destination",
        edges.route_after_destination,
        {"check_property": "check_property", "ask_destination": graph.END},
    )
    workflow.add_conditional_edges(
        "check_property",
        functools.partial(edges.route_after_property, llm=llm),
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

    # Use provided checkpointer or default to MemorySaver
    if checkpointer is None:
        checkpointer = MemorySaver()

    return workflow.compile(checkpointer=checkpointer)
