import os
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from models import get_llm
import streamlit as st
import warnings

# Suppress the specific warning
warnings.filterwarnings('ignore', message='.*ScriptRunContext.*')
# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
# Initialize reservation state in session state
print(f"Script run")
if "reservation_state" not in st.session_state:
    # print(f"DEBUG: Initializing reservation_state in session")
    st.session_state.reservation_state = {
        'step': None,
        'location': None,           # Sri Lanka or Maldives
        'property_type': None,      # coastal, city, cultural, budget, premium
        'property': None,           # Selected hotel name
        'check_in': None,
        'check_out': None,
        'duration': None,
        'guests': None,
        'children': 0,              # Number of children
        'rooms_needed': 1,
        'budget_range': [100, 500], # [min, max] in USD per night
        'room_type': None,
        'meal_type': None,          # breakfast, half board, full board, all inclusive
        'total_cost': 0,
        'preferences': {},
        'confirmation_details': {}
    }

from reservation_tools import (
    start_reservation_process, set_destination_preference, select_property_with_ai,
    confirm_property_selection, set_booking_details, check_availability_and_show_rooms, 
    select_room_type, select_meal_plan, confirm_final_reservation, 
    sync_from_session_state, sync_to_session_state
)
from change_booking_tools import change_existing_booking
from general_query_tools import get_hotel_info, handle_general_query

# Initialize global reservation state with session state values
sync_from_session_state()


# Legacy tools for backwards compatibility and other options
bookings = {}  # In-memory dict for existing bookings


# State Definition
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

# Enhanced system prompt for natural conversation with new flow
system_prompt = """
You are a friendly and professional hotel chatbot assistant for Cinnamon Hotels. You provide exceptional service with a warm, human-like conversational style.

These are the main options you have to assist users:
1. Make a new reservation
2. Change an existing booking  
3. Know something about our hotels
4. Other (general questions)

NEW RESERVATION FLOW GUIDELINES:

**For Option 1 (Make a new reservation): Follow these exact sequence**
1. FIRST: Use start_reservation_process tool - introduces the new flow and asks for destination
2. SECOND: Use set_destination_preference tool - handles Sri Lanka vs Maldives selection if user gives other than these two options send him a proper concise message saying We are currently operate only in Sri Lanka and Maldives only. Please choose one of these destinations. in that case no need to call the tool
3. THIRD: Use select_property_with_ai tool - AI-powered property selection based on user preferences
4. FOURTH: Use confirm_property_selection tool - handles user's response to recommendation (accept or alternatives)
5. FIFTH: Use set_booking_details tool - collects dates, guests, children, and budget
6. SIXTH: Use check_availability_and_show_rooms tool - shows available rooms within budget
7. SEVENTH: Use select_room_type tool - handles room selection
8. EIGHTH: Use select_meal_plan tool - handles meal plan selection and cost calculation
9. FINAL: Use confirm_final_reservation tool - shows summary and confirms booking


**IMPORTANT: Property Confirmation Step:**
- After select_property_with_ai provides a recommendation, ALWAYS use confirm_property_selection tool next
- When user says "Yes, let's book this" or similar acceptance phrases, use confirm_property_selection tool
- When user says "Show me alternatives" or wants other options, use confirm_property_selection tool  
- This tool handles the transition from property_confirmation to booking_details step

**For Option 2 (Change Booking):**
- Ask for booking reference number
- Use change_existing_booking tool with their request
- Wait for user response before any additional actions

**For Option 3 (Hotel Info):**
- Use get_hotel_info tool to show property details
- Wait for user response before offering reservations

**For Option 4 (General Questions):**
- Use handle_general_query tool for policies, amenities, etc.
- Wait for user response before additional help

CONVERSATION STYLE:
- Be warm, friendly, and professional
- Use emojis appropriately to make it engaging
- Acknowledge user inputs positively
- Provide clear, organized information
- Ask follow-up questions to understand needs better
- Always offer next steps or additional help

CRITICAL REMINDERS:
- Always wait for user input before proceeding to the next step
- Present tool responses naturally and ask for the next piece of information
- Let the user guide the conversation pace
- Follow the NEW reservation flow sequence exactly


"""

# Cache the LLM and tools to avoid re-authentication
@st.cache_resource
def get_cached_llm_with_tools():
    llm = get_llm()
    tools = [
        start_reservation_process, set_destination_preference, select_property_with_ai,
        confirm_property_selection, set_booking_details, check_availability_and_show_rooms, 
        select_room_type, select_meal_plan, confirm_final_reservation,
        get_hotel_info, change_existing_booking, handle_general_query
    ]
    return llm.bind_tools(tools), tools

llm_with_tools, tools = get_cached_llm_with_tools()

# Nodes
def agent_node(state: AgentState) -> AgentState:
    """Agent node that invokes the LLM."""
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    # print(f"DEBUG: Full LLM response: {response}")
    # Simple debug: Print tool selection
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            print(f"🔧 DEBUG: LLM selected tool '{tool_call['name']}' with args: {tool_call['args']}")
    else:
        print(f"💬 DEBUG: LLM response (no tools): {response.content[:100]}...")
    
    return {"messages": [response]}

# Tool node (prebuilt to handle tool calls)
tool_node = ToolNode(tools=tools)

# Custom function to control tool execution flow
def should_continue(state: AgentState) -> str:
    """Decide whether to continue with tools or end"""
    last_message = state["messages"][-1]
    
    # If the last message has tool calls, execute them
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    else:
        return END

# Graph Setup
graph = StateGraph(state_schema=AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", END)  
graph.set_entry_point("agent")
runnable = graph.compile()

# Streamlit UI
st.set_page_config(
    page_title="Cinnamon Hotels Chatbot",
    page_icon="🏨",
    layout="wide"
)


st.title("🏨 Cinnamon Hotels Assistant")
st.markdown("*Your personal booking companion*")


# Add initial greeting if no messages
if not st.session_state.messages:
    welcome_message = f"""Welcome to Cinnamon Hotels! 🌟 

I'm here to help you with all your hotel needs. What can I do for you today?"""
    
    st.session_state.messages.append(AIMessage(content=welcome_message))



chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        role = "assistant" if isinstance(message, (AIMessage, ToolMessage)) else "user"
        # print(f"DEBUG: Rendering message from {role}: {message.content[:20]}")
        if role == "assistant" and message.content.strip() == "":
            continue  # Skip empty assistant messages
        with st.chat_message(role):
            st.markdown(message.content,unsafe_allow_html=True)
        

# Check if we should show option buttons
# print(f"DEBUG: Current reservation step: {st.session_state.reservation_state}")
show_welcome_options_buttons = False
if st.session_state.reservation_state['step'] is None:
    show_welcome_options_buttons = True
# else:
#     show_welcome_options_buttons = False

# Initialize user_input
user_input = None

# Quick action buttons
if show_welcome_options_buttons:
    st.markdown("---")
    st.markdown("### Quick Actions:")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏨 Make Reservation", key="option1", use_container_width=True):
            user_input = "I want to make a new reservation"
        
    with col2:
        if st.button("📝 Change Booking", key="option2", use_container_width=True):
            user_input = "I need to change my existing booking"
            
    with col3:
        if st.button("ℹ️ Hotel Info", key="option3", use_container_width=True):
            user_input = "Tell me about your hotels"
            
    with col4:
        if st.button("💬 Ask Question", key="option4", use_container_width=True):
            user_input = "I have a general question"

# Interactive widgets during reservation
if st.session_state.reservation_state['step'] is not None:
    step = st.session_state.reservation_state.get('step', 'welcome')
    
    if step == 'booking_details':
        st.markdown("---")
        st.markdown("### 📅 Complete Your Booking Details")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Travel Dates:**")
            check_in = st.date_input(
                "Check-in Date",
                value=st.session_state.reservation_state.get('check_in'),
                key="checkin_widget"
            )
            check_out = st.date_input(
                "Check-out Date", 
                value=st.session_state.reservation_state.get('check_out'),
                key="checkout_widget"
            )
            
            st.markdown("**Guests:**")
            adults = st.number_input(
                "Adults",
                min_value=1,
                max_value=10,
                value=st.session_state.reservation_state.get('guests', 2),
                key="adults_widget"
            )
            
            children = st.number_input(
                "Children",
                min_value=0,
                max_value=6,
                value=st.session_state.reservation_state.get('children', 0),
                key="children_widget"
            )
            
        with col2:
            st.markdown("**Budget Range (per night, USD):**")
            budget_range = st.slider(
                "Select your budget range",
                min_value=50,
                max_value=1200,
                value=st.session_state.reservation_state.get('budget_range', [100, 500]),
                step=25,
                key="budget_widget"
            )
            st.write(f"💰 ${budget_range[0]} - ${budget_range[1]} per night")
            
            rooms_needed = st.number_input(
                "Number of Rooms",
                min_value=1,
                max_value=5,
                value=st.session_state.reservation_state.get('rooms_needed', 1),
                key="rooms_widget"
            )
        
        if st.button("✅ Confirm Booking Details", key="confirm_booking_details"):
            # Update reservation state with widget values
            duration = (check_out - check_in).days if check_out > check_in else 1
            st.session_state.reservation_state.update({
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d'),
                'budget_range': budget_range,
                'guests': int(adults),
                'children': int(children),
                'rooms_needed': int(rooms_needed),
                'duration': duration
            })
            user_input = f"Check-in {check_in}, check-out {check_out}, {adults} adults and {children} children, {rooms_needed} room(s), budget ${budget_range[0]}-${budget_range[1]} per night"
    
    elif step == 'location':
        st.markdown("---")
        st.markdown("### 🌍 Choose Your Destination")
        st.markdown("Select your preferred destination or type it in the chat:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sri Lanka", key="location_sl", use_container_width=True):
                user_input = "Sri Lanka"
                # st.success("🇱🇰 Sri Lanka selected!")
                
        with col2:
            if st.button("Maldives", key="location_maldives", use_container_width=True):
                user_input = "Maldives"
                # st.success("🏝️ Maldives selected!")
        
        st.markdown("**Or type:** *Sri Lanka* • *Maldives*")
        
    # elif step == 'property_selection':
    #     st.markdown("---")
    #     st.markdown("🏨 Describe Your Ideal Experience" \
    #     "Tell me about your perfect vacation in the chat below! I'll analyze your preferences and recommend the ideal property that matches your style, budget, and dreams.")
    #     # st.info("💬 Tell me about your perfect vacation in the chat below! I'll analyze your preferences and recommend the ideal property that matches your style, budget, and dreams.")
        
    elif step == 'property_confirmation':
        st.markdown("---")
        st.markdown("### 🤔 What would you like to do?")
        
        # Show recommended property info if available
        recommended_property = st.session_state.reservation_state.get('recommended_property')
        # if recommended_property:
        #     st.info(f"💡 I've recommended **{recommended_property}** based on your preferences!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, let's book this!", key="confirm_property", use_container_width=True):
                user_input = "Yes, let's book this"
                # st.success("✅ Property confirmed! Let's proceed with booking details.")
                
        with col2:
            if st.button("🔍 Show me alternatives", key="show_alternatives", use_container_width=True):
                user_input = "Show me alternatives"
                # st.info("🔍 Let me show you other available options...")
        
        st.markdown("**Or tell me more about what you're looking for in the chat below!**")

# Regular text input (always available at the bottom)
chat_input = st.chat_input("Type your message here... 💬")
if not user_input and chat_input:
    user_input = chat_input

# Process user input
if user_input:
    # Check if this is a duplicate message (avoid processing same message twice)
    if not st.session_state.messages or st.session_state.messages[-1].content != user_input:
        # Add user message
        user_msg = HumanMessage(content=user_input)
        st.session_state.messages.append(user_msg)
        
        # Run the graph with enhanced feedback
        with st.spinner("Let me help you with that... 🤔"):
            try:
                # Sync reservation state before tool execution
                sync_from_session_state()
                
                # Invoke with current messages and user session context
                messages_with_context = st.session_state.messages.copy()
                
                result = runnable.invoke({"messages": messages_with_context})
                
                # Sync reservation state back after tool execution
                sync_to_session_state()
                
                # Process new messages
                new_messages = result["messages"][len(st.session_state.messages):]
                for i, msg in enumerate(new_messages):
                    st.session_state.messages.append(msg)
                        
            except Exception as e:
                error_msg = AIMessage(content=f"""I apologize, but I encountered an issue while processing your request. 

Please try again, or contact our reservations team directly:
📞 Phone: +94 11 123 4567
📧 Email: reservations@cinnamonhotels.com

Error details: {str(e)}""")
                
                st.session_state.messages.append(error_msg)
        
        # Trigger a rerun to show the new messages
        st.rerun()