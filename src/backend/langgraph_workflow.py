"""
LangGraph-based reservation workflow with MCP tool integration
"""
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, TypedDict, Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# Add the parent directory to the path to import models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from models import get_llm, get_gemini_llm
from mcp_tools import MCPToolRegistry


class ReservationState(TypedDict):
    """LangGraph state schema for reservation workflow"""
    # User input
    messages: Annotated[list, add_messages]
    user_query: str
    session_id: str
    
    # Extracted information
    destination: Optional[str]
    property_preferences: List[str]
    selected_property: Optional[Dict[str, Any]]
    check_in: Optional[str]
    check_out: Optional[str]
    adults: int
    children: int
    rooms: int
    intent: str
    
    # Available properties
    available_properties: List[Dict[str, Any]]
    
    # Response generation
    response_text: str
    show_form: bool
    prefilled_data: Dict[str, Any]
    reservation_url: Optional[str]
    
    # Workflow control
    next_step: str
    conversation_complete: bool


class ReservationWorkflow:
    """LangGraph workflow for hotel reservation"""
    
    def __init__(self, hotels_data_path: str = "hotels_data.json"):
        # Load hotel data
        with open(hotels_data_path, 'r') as f:
            self.hotels_data = json.load(f)
        
        # Initialize MCP tools
        self.tools = MCPToolRegistry(self.hotels_data)
        
        # Initialize LLM
        try:
            self.llm = get_llm()
            self.llm_type = "azure"
        except Exception as e:
            print(f"Azure OpenAI not available: {e}")
            try:
                self.llm = get_gemini_llm()
                self.llm_type = "gemini"
            except Exception as e2:
                print(f"Gemini also not available: {e2}")
                self.llm = None
                self.llm_type = None
        
        # Create workflow graph
        self.workflow = self._create_workflow()
        
        # Memory for conversation persistence
        self.memory = MemorySaver()
        
        # Compile the graph
        self.app = self.workflow.compile(checkpointer=self.memory)
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(ReservationState)
        
        # Add nodes
        workflow.add_node("extract_info", self._extract_info_node)
        workflow.add_node("find_properties", self._find_properties_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("complete_booking", self._complete_booking_node)
        
        # Define the flow
        workflow.set_entry_point("extract_info")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "extract_info",
            self._route_after_extraction,
            {
                "find_properties": "find_properties",
                "generate_response": "generate_response",
                "complete_booking": "complete_booking"
            }
        )
        
        workflow.add_conditional_edges(
            "find_properties",
            self._route_after_properties,
            {
                "generate_response": "generate_response",
                "complete_booking": "complete_booking"
            }
        )
        
        workflow.add_conditional_edges(
            "generate_response",
            self._route_after_response,
            {
                "complete_booking": "complete_booking",
                "end": END
            }
        )
        
        workflow.add_edge("complete_booking", END)
        
        return workflow
    
    def _extract_info_node(self, state: ReservationState) -> ReservationState:
        """Extract information from user query using MCP tools"""
        query = state["user_query"]
        
        # Use MCP tools to extract information
        destination = self.tools.destination_extraction.extract_destination(query)
        preferences = self.tools.preference_extraction.extract_preferences(query)
        dates = self.tools.date_extraction.extract_dates(query)
        guests = self.tools.guest_extraction.extract_guests(query)
        intent = self.tools.intent_classification.classify_intent(query)
        
        # Update state with extracted information (only if not already set)
        updates = {}
        if destination and not state.get("destination"):
            updates["destination"] = destination
        
        # For preferences, append to existing rather than replace (unless empty)
        current_preferences = state.get("property_preferences", [])
        if preferences:
            # Combine unique preferences
            combined_preferences = list(set(current_preferences + preferences))
            updates["property_preferences"] = combined_preferences
        
        if dates["check_in"] and not state.get("check_in"):
            updates["check_in"] = dates["check_in"]
        
        if dates["check_out"] and not state.get("check_out"):
            updates["check_out"] = dates["check_out"]
        
        if guests["adults"] > 1 and state.get("adults", 1) == 1:
            updates["adults"] = guests["adults"]
        
        if guests["children"] > 0 and state.get("children", 0) == 0:
            updates["children"] = guests["children"]
        
        if guests["rooms"] > 1 and state.get("rooms", 1) == 1:
            updates["rooms"] = guests["rooms"]
        
        updates["intent"] = intent
        
        # Handle property selection by name (check current state's destination first)
        current_destination = state.get("destination") or destination
        if current_destination and not state.get("selected_property"):
            # Check if user mentioned a specific property name
            query_lower = query.lower()
            
            # More specific property name matching
            if "cinnamon grand" in query_lower or "grand colombo" in query_lower:
                property = self.tools.hotel_search.find_property_by_name("Cinnamon Grand Colombo", current_destination)
                if property:
                    updates["selected_property"] = property
            elif "cinnamon lakeside" in query_lower or "lakeside colombo" in query_lower:
                property = self.tools.hotel_search.find_property_by_name("Cinnamon Lakeside Colombo", current_destination)
                if property:
                    updates["selected_property"] = property
            elif "cinnamon lodge" in query_lower or "lodge habarana" in query_lower:
                property = self.tools.hotel_search.find_property_by_name("Cinnamon Lodge Habarana", current_destination)
                if property:
                    updates["selected_property"] = property
            elif "cinnamon bey" in query_lower or "bey beruwala" in query_lower:
                property = self.tools.hotel_search.find_property_by_name("Cinnamon Bey Beruwala", current_destination)
                if property:
                    updates["selected_property"] = property
            elif "cinnamon citadel" in query_lower or "citadel kandy" in query_lower:
                property = self.tools.hotel_search.find_property_by_name("Cinnamon Citadel Kandy", current_destination)
                if property:
                    updates["selected_property"] = property
        
        return {**state, **updates}
    
    def _find_properties_node(self, state: ReservationState) -> ReservationState:
        """Find matching properties using MCP tools"""
        destination = state.get("destination")
        preferences = state.get("property_preferences", [])
        
        if not destination:
            return state
        
        # Search for properties
        properties = self.tools.hotel_search.search_hotels(destination, preferences)
        
        # If we have only one property and no selection yet, auto-select it
        if len(properties) == 1 and not state.get("selected_property"):
            return {
                **state,
                "available_properties": properties,
                "selected_property": properties[0]
            }
        
        return {
            **state,
            "available_properties": properties
        }
    
    def _generate_response_node(self, state: ReservationState) -> ReservationState:
        """Generate conversational response using LLM or fallback logic"""
        # Determine if we should show the booking form
        show_form = (
            state.get("selected_property") is not None and
            state.get("check_in") is not None and
            state.get("check_out") is not None
        )
        
        prefilled_data = {}
        if show_form:
            property = state.get("selected_property")
            prefilled_data = {
                'checkIn': state.get("check_in"),
                'checkOut': state.get("check_out"),
                'adults': state.get("adults", 1),
                'children': state.get("children", 0),
                'rooms': state.get("rooms", 1),
                'propertyName': property.get('name') if property else '',
                'destination': state.get("destination", '')
            }
        
        if self.llm:
            response_text = self._generate_llm_response(state)
        else:
            response_text = self._generate_fallback_response(state)
        
        if show_form:
            response_text += f"\n\nPerfect! I have all the details for your booking. Please review the information below and confirm your reservation."
        
        return {
            **state,
            "response_text": response_text,
            "show_form": show_form,
            "prefilled_data": prefilled_data
        }
    
    def _complete_booking_node(self, state: ReservationState) -> ReservationState:
        """Complete the booking and generate reservation URL"""
        selected_property = state.get("selected_property")
        
        if not selected_property:
            return {
                **state,
                "response_text": "Error: No property selected for booking.",
                "conversation_complete": True
            }
        
        # Generate reservation URL using MCP tool
        reservation_data = {
            'check_in': state.get("check_in"),
            'check_out': state.get("check_out"),
            'adults': state.get("adults", 1),
            'children': state.get("children", 0),
            'rooms': state.get("rooms", 1)
        }
        
        reservation_url = self.tools.reservation_url.generate_reservation_url(
            selected_property, reservation_data
        )
        
        return {
            **state,
            "reservation_url": reservation_url,
            "conversation_complete": True,
            "response_text": f"Great! Your reservation for {selected_property['name']} is ready. Click the link to complete your booking."
        }
    
    def _route_after_extraction(self, state: ReservationState) -> str:
        """Route after information extraction"""
        intent = state.get("intent", "search")
        selected_property = state.get("selected_property")
        check_in = state.get("check_in")
        check_out = state.get("check_out")
        destination = state.get("destination")
        
        # If we have all the key information (property + dates), we can show the form
        if selected_property and check_in and check_out:
            return "generate_response"  # This will trigger form display
        
        # If we have confirmation intent and all required info
        if intent == "confirm_booking" and selected_property:
            return "complete_booking"
        
        # If we have destination but need to find properties
        elif destination and not state.get("available_properties"):
            return "find_properties"
        
        # Otherwise generate a response to continue the conversation
        else:
            return "generate_response"
    
    def _route_after_properties(self, state: ReservationState) -> str:
        """Route after finding properties"""
        if (state.get("selected_property") and 
            state.get("check_in") and 
            state.get("check_out") and 
            state.get("intent") == "confirm_booking"):
            return "complete_booking"
        else:
            return "generate_response"
    
    def _route_after_response(self, state: ReservationState) -> str:
        """Route after generating response"""
        if state.get("show_form") and state.get("intent") == "confirm_booking":
            return "complete_booking"
        else:
            return "end"
    
    def _generate_llm_response(self, state: ReservationState) -> str:
        """Generate response using LLM"""
        session_context = f"""
Current session state:
- Destination: {state.get('destination')}
- Property preferences: {state.get('property_preferences')}
- Selected property: {state.get('selected_property', {}).get('name') if state.get('selected_property') else None}
- Check-in: {state.get('check_in')}
- Check-out: {state.get('check_out')}
- Adults: {state.get('adults', 1)}, Children: {state.get('children', 0)}, Rooms: {state.get('rooms', 1)}
"""
        
        properties_context = ""
        available_properties = state.get("available_properties", [])
        if available_properties:
            properties_context = "Available properties:\n"
            for i, prop in enumerate(available_properties[:3], 1):
                properties_context += f"{i}. {prop['name']} in {prop['location']} - {prop['description']}\n"
        
        prompt = f"""
You are a friendly and helpful hotel reservation assistant for Cinnamon Hotels. 
Your goal is to help customers find and book the perfect hotel.

{session_context}

{properties_context}

User Query: "{state.get('user_query')}"
User Intent: {state.get('intent')}

Generate a natural, conversational response that:
1. Acknowledges what the user has provided
2. Guides them to the next step in the booking process
3. Is warm, professional, and helpful
4. Keeps the conversation flowing naturally
5. If properties are available, present them in an engaging way
6. If information is missing, ask for it in a friendly manner

Guidelines:
- Keep responses concise but informative
- Use friendly, conversational tone
- Don't repeat information already established
- Focus on moving the conversation forward
- If user has selected everything needed, prepare them for the booking form

Respond as the assistant:
"""
        
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            return response_text.strip()
        except Exception as e:
            print(f"LLM response generation failed: {e}")
            # return self._generate_fallback_response(state)
    
    # def _generate_fallback_response(self, state: ReservationState) -> str:
    #     """Generate fallback response when LLM is not available"""
    #     selected_property = state.get("selected_property")
    #     check_in = state.get("check_in")
    #     check_out = state.get("check_out")
    #     destination = state.get("destination")
        
    #     # If we have everything needed for booking
    #     if selected_property and check_in and check_out:
    #         return (
    #             f"Perfect! I have all your reservation details for **{selected_property['name']}** "
    #             f"from {check_in} to {check_out} for {state.get('adults', 1)} adult(s)"
    #             f"{' and ' + str(state.get('children', 0)) + ' child(ren)' if state.get('children', 0) > 0 else ''} "
    #             f"in {state.get('rooms', 1)} room(s). "
    #             f"This {selected_property.get('type', '')} property in {selected_property.get('location', '')} is {selected_property.get('description', '')}."
    #         )
        
    #     # If property is selected but missing dates
    #     elif selected_property and not (check_in and check_out):
    #         return (
    #             f"Great choice! **{selected_property['name']}** is a wonderful property. "
    #             f"I have all your accommodation preferences ready. "
    #             f"Could you please let me know your preferred check-in and check-out dates?"
    #         )
        
    #     # If dates are provided but no property selected
    #     elif check_in and check_out and not selected_property:
    #         return (
    #             f"Perfect! I have your dates from {check_in} to {check_out}. "
    #             f"Now let me help you choose the perfect property for your stay."
    #         )
        
    #     # Original fallback logic for other cases
    #     elif not destination:
    #         return (
    #             "I'd love to help you find the perfect hotel! "
    #             "Are you looking to stay in Sri Lanka or the Maldives? "
    #             "Each destination offers unique experiences - Sri Lanka has rich culture and diverse landscapes, "
    #             "while the Maldives offers pristine beaches and overwater villas."
    #         )
    #     elif not state.get("property_preferences") and not selected_property:
    #         dest_name = destination
    #         if dest_name == "Sri Lanka":
    #             return (
    #                 f"Great choice! {dest_name} has amazing properties. "
    #                 "What type of experience are you looking for? We have:\n"
    #                 "• Coastal/beachfront properties for ocean lovers\n"
    #                 "• City hotels for urban experiences and business\n"
    #                 "• Nature/eco-friendly resorts for wildlife enthusiasts\n"
    #                 "• Hill country properties for scenic mountain views\n\n"
    #                 "What sounds most appealing to you?"
    #             )
    #         else:
    #             return (
    #                 f"Excellent! The {dest_name} offers incredible luxury resorts. "
    #                 "All our properties are coastal with stunning beaches. "
    #                 "Are you looking for:\n"
    #                 "• Romantic/honeymoon experiences\n"
    #                 "• Family-friendly resorts\n"
    #                 "• Diving and water sports activities\n"
    #                 "• Adults-only peaceful retreats\n\n"
    #                 "What type of experience interests you most?"
    #             )
    #     elif not selected_property:
    #         properties = state.get("available_properties", [])
    #         if properties:
    #             if len(properties) == 1:
    #                 return f"Perfect! I found the ideal property for you: **{properties[0]['name']}** in {properties[0]['location']}. {properties[0]['description']}"
    #             else:
    #                 property_list = ""
    #                 for i, prop in enumerate(properties[:3], 1):
    #                     property_list += f"{i}. **{prop['name']}** - {prop['location']}\n   {prop['description']}\n\n"
    #                 return f"I found several great options for you:\n\n{property_list}Which property interests you most?"
    #         else:
    #             return "Let me search for available properties for you."
    #     else:
    #         return "Thank you for the information. Let me help you with your reservation."
    
    def process_query(self, session_id: str, query: str) -> Dict[str, Any]:
        """Process a user query through the LangGraph workflow"""
        config = {"configurable": {"thread_id": session_id}}
        
        # Get existing state or create initial state
        try:
            current_state = self.app.get_state(config)
            if current_state and current_state.values:
                # Merge with existing state, updating only the new query
                state = {
                    **current_state.values,
                    "user_query": query,
                    "messages": current_state.values.get("messages", []) + [{"role": "user", "content": query}]
                }
            else:
                # Create fresh initial state
                state = {
                    "messages": [{"role": "user", "content": query}],
                    "user_query": query,
                    "session_id": session_id,
                    "destination": None,
                    "property_preferences": [],
                    "selected_property": None,
                    "check_in": None,
                    "check_out": None,
                    "adults": 1,
                    "children": 0,
                    "rooms": 1,
                    "intent": "search",
                    "available_properties": [],
                    "response_text": "",
                    "show_form": False,
                    "prefilled_data": {},
                    "reservation_url": None,
                    "next_step": "",
                    "conversation_complete": False
                }
        except Exception as e:
            print(f"Error getting state: {e}")
            # Fallback to fresh state
            state = {
                "messages": [{"role": "user", "content": query}],
                "user_query": query,
                "session_id": session_id,
                "destination": None,
                "property_preferences": [],
                "selected_property": None,
                "check_in": None,
                "check_out": None,
                "adults": 1,
                "children": 0,
                "rooms": 1,
                "intent": "search",
                "available_properties": [],
                "response_text": "",
                "show_form": False,
                "prefilled_data": {},
                "reservation_url": None,
                "next_step": "",
                "conversation_complete": False
            }
        
        # Run the workflow
        result = self.app.invoke(state, config)
        
        # Return the response in the expected format
        return {
            'response': result.get("response_text", ""),
            'show_form': result.get("show_form", False),
            'prefilled_data': result.get("prefilled_data", {}),
            'reservation_url': result.get("reservation_url"),
            'session_state': result
        }
    
    def complete_reservation(self, session_id: str, reservation_data: Dict) -> Dict[str, Any]:
        """Complete a reservation with final details"""
        # Get current state
        config = {"configurable": {"thread_id": session_id}}
        current_state = self.app.get_state(config)
        
        if not current_state or not current_state.values.get("selected_property"):
            return {
                'error': 'No property selected',
                'reservation_url': None
            }
        
        # Update state with final reservation data
        updated_state = {
            **current_state.values,
            "check_in": reservation_data.get('checkIn'),
            "check_out": reservation_data.get('checkOut'),
            "adults": reservation_data.get('adults', 1),
            "children": reservation_data.get('children', 0),
            "rooms": reservation_data.get('rooms', 1),
            "intent": "confirm_booking",
            "user_query": "confirm booking"
        }
        
        # Run the completion workflow
        result = self.app.invoke(updated_state, config)
        
        return {
            'reservation_url': result.get("reservation_url"),
            'property': result.get("selected_property"),
            'session_state': result
        }