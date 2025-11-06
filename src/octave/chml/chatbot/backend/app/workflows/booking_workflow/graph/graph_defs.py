"""Graph definitions.

===============================================================================
    Copyright (c) 2025 OCTAVE. All rights reserved.

    This is proprietary and confidential software of OCTAVE.
    Unauthorized use, reproduction, or distribution is strictly prohibited.
===============================================================================
"""

import functools

from langgraph import graph

from octave.chml.chatbot.backend.app.workflows.booking_workflow.graph import edges, nodes, states


def build_booking_graph(hotels_data: dict, llm):
    """Build the LangGraph workflow."""
    workflow = graph.StateGraph(states.BookingState)

    # Add nodes
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

    return workflow.compile()
