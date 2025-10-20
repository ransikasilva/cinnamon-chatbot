"""
LangGraph and MCP-powered hotel reservation system
"""
import json
import sys
import os
from typing import Dict, Any

# Import the new LangGraph workflow
from langgraph_workflow import ReservationWorkflow


class HotelReservationTool:
    """
    Main reservation tool using LangGraph workflows and MCP tools
    """
    
    def __init__(self, hotels_data_path: str = "hotels_data.json"):
        """Initialize the reservation tool with LangGraph workflow"""
        self.workflow = ReservationWorkflow(hotels_data_path)
        self.sessions = {}  # Keep for compatibility, but workflow handles state
    
    def process_reservation_query(self, session_id: str, query: str) -> Dict[str, Any]:
        """
        Process reservation queries using LangGraph workflow
        
        Args:
            session_id: Unique session identifier
            query: User's natural language query
            
        Returns:
            Dictionary with response, form status, and session state
        """
        return self.workflow.process_query(session_id, query)
    
    def complete_reservation(self, session_id: str, reservation_data: Dict) -> Dict[str, Any]:
        """
        Complete the reservation with final details
        
        Args:
            session_id: Unique session identifier
            reservation_data: Final reservation details from form
            
        Returns:
            Dictionary with reservation URL and property details
        """
        return self.workflow.complete_reservation(session_id, reservation_data)