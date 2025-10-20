"""
LangGraph-based reservation workflow with LLM-driven agent approach
Uses LangChain's ReAct agent for dynamic tool selection and reasoning
"""
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool

# Add the parent directory to the path to import models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from models import get_llm, get_gemini_llm
from mcp_tools import MCPToolRegistry


class ReservationState:
    """State management for agent-based reservation system"""
    
    def __init__(self):
        self.destination: Optional[str] = None
        self.property_preferences: List[str] = []
        self.selected_property: Optional[Dict[str, Any]] = None
        self.check_in: Optional[str] = None
        self.check_out: Optional[str] = None
        self.adults: int = 1
        self.children: int = 0
        self.rooms: int = 1
        self.available_properties: List[Dict[str, Any]] = []
        self.reservation_url: Optional[str] = None
        self.chat_history: List[Dict[str, str]] = []
        self.intent: str = "search"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            'destination': self.destination,
            'property_preferences': self.property_preferences,
            'selected_property': self.selected_property,
            'check_in': self.check_in,
            'check_out': self.check_out,
            'adults': self.adults,
            'children': self.children,
            'rooms': self.rooms,
            'available_properties': self.available_properties,
            'reservation_url': self.reservation_url,
            'intent': self.intent
        }


class ReservationWorkflow:
    """LLM-driven agent for hotel reservation using ReAct pattern"""
    
    def __init__(self, hotels_data_path: str = "hotels_data.json"):
        # Load hotel data
        with open(hotels_data_path, 'r') as f:
            self.hotels_data = json.load(f)
        
        # Initialize LLM first
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
                raise Exception("No LLM available. Please configure Azure OpenAI or Gemini.")
        
        # Initialize MCP tools (pass LLM to tools so they can use it)
        self.tools = MCPToolRegistry(self.hotels_data, self.llm)
        
        # Session storage for states
        self.sessions: Dict[str, ReservationState] = {}
        
        # Current session context (set during process_query)
        self.current_session_id: Optional[str] = None
        
        # Create LangChain tools for agent
        self.agent_tools = self._create_agent_tools()
        
        # Create agent prompt
        self.agent_prompt = self._create_agent_prompt()
        
        # Create the ReAct agent (LLM + tools + prompt)
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.agent_tools,
            prompt=self.agent_prompt
        )
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.agent_tools,
            verbose=True,  # See LLM's reasoning
            max_iterations=10,
            handle_parsing_errors=True
        )
    
    def _get_session_state(self, session_id: str) -> ReservationState:
        """Get or create session state"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ReservationState()
        return self.sessions[session_id]
    
    def _create_agent_tools(self) -> List[Tool]:
        """Create simplified, focused tools for the agent"""
        
        # Main universal booking query processor
        def process_booking_query_func(user_query: str) -> str:
            """
            Universal tool for processing ANY booking-related conversation.
            Intelligently extracts destination, dates, guests, preferences, and hotel selections.
            Use this for all conversational booking queries.
            """
            try:
                # Get current session ID from context
                session_id = self.current_session_id
                if not session_id:
                    return "Error: No active session"
                
                state = self._get_session_state(session_id)
                
                # Convert state object to dict for the tool
                state_dict = state.to_dict()
                
                result = self.tools.universal_booking.process_booking_query(user_query, state_dict)
                
                # Update session state object with extracted info
                for key, value in result['updated_state'].items():
                    if hasattr(state, key):
                        setattr(state, key, value)
                
                # Debug: Print updated state
                print(f"[DEBUG] State after update: destination={state.destination}, hotel={state.selected_property['name'] if state.selected_property else None}, dates={state.check_in} to {state.check_out}")
                
                return result['response']
            except Exception as e:
                return f"Error processing query: {str(e)}"
        
        process_booking_tool = Tool(
            name="process_booking_query",
            func=process_booking_query_func,
            description="""PRIMARY TOOL - Use for ALL booking-related conversations. Handles: greetings, destination queries, date mentions, guest counts, preferences, hotel selections. Intelligently extracts and tracks all booking information."""
        )
        
        # Get current session state
        def get_state_func(dummy_input: str = "") -> str:
            """Check what booking info has been collected so far"""
            try:
                session_id = self.current_session_id
                if not session_id:
                    return "Error: No active session"
                    
                state = self._get_session_state(session_id)
                return json.dumps({
                    'destination': state.destination,
                    'selected_hotel': state.selected_property,
                    'check_in': state.check_in,
                    'check_out': state.check_out,
                    'adults': state.adults,
                    'children': state.children,
                    'rooms': state.rooms,
                    'preferences': state.property_preferences
                })
            except Exception as e:
                return f"Error: {str(e)}"
        
        get_state_tool = Tool(
            name="check_booking_status",
            func=get_state_func,
            description="""Check current booking progress. Use at start of conversation to see what info has been collected."""
        )
        
        # Recommend hotels
        def recommend_hotels_func(dummy_input: str = "") -> str:
            """Find and recommend hotels based on collected preferences"""
            try:
                session_id = self.current_session_id
                if not session_id:
                    return "Error: No active session"
                    
                state = self._get_session_state(session_id)
                
                if not state.destination:
                    return "Please specify a destination first (Sri Lanka or Maldives)"
                
                hotels = self.tools.hotel_recommendation.recommend_hotels(
                    destination=state.destination,
                    preferences=state.property_preferences,
                    query=""
                )
                
                if not hotels:
                    return f"No hotels found for {state.destination}"
                
                # Format recommendations
                response = f"I found {len(hotels)} perfect options in {state.destination}:\n\n"
                for i, hotel in enumerate(hotels, 1):
                    response += f"{i}. **{hotel['name']}** - {hotel.get('location', '')}\n"
                    response += f"   {hotel.get('description', '')}\n\n"
                
                # Store for selection
                state.available_properties = hotels
                
                response += "Which one interests you? Just tell me the number or name!"
                return response
            except Exception as e:
                return f"Error: {str(e)}"
        
        recommend_tool = Tool(
            name="recommend_hotels",
            func=recommend_hotels_func,
            description="""Show hotel recommendations after destination and preferences are known."""
        )
        
        # Select a specific hotel
        def select_hotel_func(hotel_name: str) -> str:
            """Select a specific hotel by name"""
            try:
                session_id = self.current_session_id
                if not session_id:
                    return "Error: No active session"
                    
                state = self._get_session_state(session_id)
                
                # Find hotel in available properties or search all hotels
                selected = None
                
                # First check available properties
                for hotel in state.available_properties:
                    if hotel_name.lower() in hotel['name'].lower():
                        selected = hotel
                        break
                
                # If not found, search all hotels for destination
                if not selected and state.destination:
                    for dest in self.hotels_data.get('destinations', []):
                        if dest['name'] == state.destination:
                            for hotel in dest.get('properties', []):
                                if hotel_name.lower() in hotel['name'].lower():
                                    selected = hotel
                                    break
                
                if selected:
                    state.selected_property = selected
                    return f"Perfect! I've selected **{selected['name']}** for you. Now I need dates and guest count to proceed."
                else:
                    return f"I couldn't find '{hotel_name}'. Please try again or ask for recommendations."
                    
            except Exception as e:
                return f"Error: {str(e)}"
        
        select_hotel_tool = Tool(
            name="select_hotel",
            func=select_hotel_func,
            description="""Select a specific hotel by name when user confirms their choice. Input: hotel_name"""
        )
        
        # Generate booking URL
        def generate_url_func(dummy_input: str = "") -> str:
            """Generate final booking URL when all details are ready"""
            try:
                session_id = self.current_session_id
                if not session_id:
                    return "Error: No active session"
                    
                state = self._get_session_state(session_id)
                
                if not state.selected_property:
                    return "ERROR: No hotel selected"
                if not state.check_in or not state.check_out:
                    return "ERROR: Missing dates"
                
                booking_data = {
                    'check_in': state.check_in,
                    'check_out': state.check_out,
                    'adults': state.adults,
                    'children': state.children,
                    'rooms': state.rooms
                }
                
                url = self.tools.reservation_url.generate_reservation_url(
                    state.selected_property, booking_data
                )
                state.reservation_url = url
                return url
            except Exception as e:
                return f"Error: {str(e)}"
        
        generate_url_tool = Tool(
            name="generate_booking_url",
            func=generate_url_func,
            description="""Generate final booking URL when hotel, dates, and guests are all confirmed."""
        )
        
        return [
            process_booking_tool,
            get_state_tool,
            recommend_tool,
            select_hotel_tool,
            generate_url_tool
        ]
    
    def _create_agent_prompt(self) -> PromptTemplate:
        """Create the agent's system prompt with ReAct pattern instructions"""
        template = """You are a friendly hotel reservation assistant for Cinnamon Hotels.
Your goal: Help customers find and book the perfect hotel in Sri Lanka or the Maldives.

AVAILABLE TOOLS:
{tools}

CRITICAL RULES:
1. **ALWAYS use 'process_booking_query' FIRST** for every user message. This tool:
   - Extracts new information from user's query
   - Updates and remembers ALL booking details (destination, dates, guests, preferences, hotel)
   - Returns what's been collected AND what's still needed
   - YOU MUST READ AND TRUST this tool's response!

2. **READ THE TOOL RESPONSE CAREFULLY**:
   - The tool tells you exactly what information has been collected
   - The tool tells you what's missing
   - Base your Final Answer ONLY on what the tool says
   - DO NOT ask for information the tool says it already has!

3. **When to use OTHER tools**:
   - Use 'recommend_hotels' if tool says "Let me find properties" OR user asks to see options
   - Use 'select_hotel' when user picks a specific hotel from recommendations
   - Use 'check_booking_status' if you're unsure what info has been collected
   - Use 'generate_booking_url' when ALL required info is collected (hotel, dates, guests)

4. **REQUIRED FORMAT**:
   Thought: [What should I do? What tool should I use?]
   Action: [tool name from: {tool_names}]
   Action Input: [the input for the tool]
   Observation: [tool result - READ THIS CAREFULLY!]
   ... (repeat if needed)
   Thought: Based on the tool response, I should [tell user X / ask for Y / show Z]
   Final Answer: [Your response based ONLY on tool observations]

5. **DO NOT HALLUCINATE**:
   - If tool says "I have destination and guests", DO NOT ask for them again!
   - If tool says "I need dates", ONLY ask for dates
   - Trust the tool's memory - it remembers across all messages in this session

EXAMPLE:
User: next weekend
Thought: I should process this to extract dates
Action: process_booking_query
Action Input: next weekend
Observation: Perfect! I've noted: dates: 2025-10-25 to 2025-10-27. I already have: destination=Sri Lanka, guests=1 adult, hotel=Cinnamon Bey. Ready to generate booking URL!
Thought: The tool says all info is collected! I should generate the booking URL
Action: generate_booking_url
Action Input: 
Observation: https://reservations.cinnamonhotels.com/...
Thought: I have the booking URL to give the user
Final Answer: Perfect! I have all your details. Here's your booking link: [URL]

NOW BEGIN!
Current session: {session_id}
User Query: {input}

{agent_scratchpad}"""
        
        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad", "session_id"],
            partial_variables={
                "tools": self._get_tools_description(),
                "tool_names": self._get_tool_names()
            }
        )
    
    def _get_tools_description(self) -> str:
        """Get formatted tools description"""
        return "\n".join([f"- {tool.name}: {tool.description}" for tool in self.agent_tools])
    
    def _get_tool_names(self) -> str:
        """Get comma-separated tool names"""
        return ", ".join([tool.name for tool in self.agent_tools])
    
    def process_query(self, session_id: str, query: str) -> Dict[str, Any]:
        """Process a user query using the LLM agent"""
        print(f"\n\n{'#'*80}")
        print(f"# NEW QUERY PROCESSING (AGENT-BASED)")
        print(f"# Session ID: {session_id}")
        print(f"# Query: '{query}'")
        print(f"{'#'*80}\n")
        
        # Set current session context for tools to access
        self.current_session_id = session_id
        
        # Get or create session state
        state = self._get_session_state(session_id)
        
        # Invoke the agent
        try:
            result = self.agent_executor.invoke({
                "input": query,
                "session_id": session_id
            })
            
            response_text = result.get('output', '')
            
            print(f"\nDEBUG: [AGENT] Agent execution completed")
            print(f"DEBUG: [AGENT] Response: {response_text[:200]}...")
            
        except Exception as e:
            print(f"ERROR: Agent execution failed: {e}")
            import traceback
            traceback.print_exc()
            response_text = "I apologize, but I encountered an error. Could you please rephrase your request?"
        
        # Update chat history
        state.chat_history.append({'role': 'user', 'content': query})
        state.chat_history.append({'role': 'assistant', 'content': response_text})
        
        # Determine if we should show the booking form
        show_form = (
            state.selected_property is not None and
            state.check_in is not None and
            state.check_out is not None
        )
        
        # Prepare prefilled data for the form
        prefilled_data = {}
        if show_form:
            prefilled_data = {
                'checkIn': state.check_in or '',
                'checkOut': state.check_out or '',
                'adults': state.adults,
                'children': state.children,
                'rooms': state.rooms,
                'propertyName': state.selected_property.get('name', ''),
                'destination': state.destination or ''
            }
        
        print(f"\nDEBUG: [PROCESS_QUERY] Completed")
        print(f"DEBUG: [PROCESS_QUERY] Show form: {show_form}")
        print(f"DEBUG: [PROCESS_QUERY] Selected property: {state.selected_property.get('name') if state.selected_property else None}")
        print(f"{'#'*80}\n\n")
        
        return {
            'response': response_text,
            'show_form': show_form,
            'prefilled_data': prefilled_data,
            'reservation_url': state.reservation_url,
            'session_state': state.to_dict()
        }
    
    def complete_reservation(self, session_id: str, reservation_data: Dict) -> Dict[str, Any]:
        """Complete a reservation with final details from the booking form"""
        print(f"\n{'#'*80}")
        print(f"# COMPLETING RESERVATION")
        print(f"# Session ID: {session_id}")
        print(f"{'#'*80}\n")
        
        # Get session state
        state = self._get_session_state(session_id)
        
        if not state.selected_property:
            return {
                'error': 'No property selected',
                'reservation_url': None
            }
        
        # Update state with final reservation data
        state.check_in = reservation_data.get('checkIn')
        state.check_out = reservation_data.get('checkOut')
        state.adults = reservation_data.get('adults', 1)
        state.children = reservation_data.get('children', 0)
        state.rooms = reservation_data.get('rooms', 1)
        state.intent = "confirm_booking"
        
        # Generate reservation URL
        url_reservation_data = {
            'check_in': state.check_in,
            'check_out': state.check_out,
            'adults': state.adults,
            'children': state.children,
            'rooms': state.rooms
        }
        
        reservation_url = self.tools.reservation_url.generate_reservation_url(
            state.selected_property, url_reservation_data
        )
        state.reservation_url = reservation_url
        
        print(f"DEBUG: [COMPLETE_RESERVATION] URL generated: {reservation_url}")
        print(f"{'#'*80}\n\n")
        
        return {
            'reservation_url': reservation_url,
            'property': state.selected_property,
            'session_state': state.to_dict()
        }