"""
Refactored MCP-compatible tools for hotel reservation system
Clean, focused tools with fallback logic and better error handling
"""
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode


class UniversalBookingTool:
    """
    Universal conversational booking tool that intelligently extracts ALL booking information
    from natural language queries and manages the booking flow
    """
    
    def __init__(self, hotels_data: Dict[str, Any], llm=None):
        self.hotels_data = hotels_data
        self.llm = llm
    
    def process_booking_query(self, user_query: str, session_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intelligently process ANY booking-related query and extract all available information.
        
        Args:
            user_query: User's natural language input
            session_state: Current session state (destination, dates, guests, etc.)
            
        Returns:
            Dict with: extracted_info, updated_state, response_message, next_action
        """
        extracted_info = {}
        
        # 1. Extract destination
        destination = self._extract_destination(user_query)
        if destination:
            extracted_info['destination'] = destination
            session_state['destination'] = destination
        
        # 2. Extract dates
        dates = self._extract_dates(user_query)
        if dates.get('check_in'):
            extracted_info['check_in'] = dates['check_in']
            extracted_info['check_out'] = dates['check_out']
            session_state['check_in'] = dates['check_in']
            session_state['check_out'] = dates['check_out']
        
        # 3. Extract guest count
        guests = self._extract_guests(user_query)
        if guests.get('adults') is not None:
            extracted_info['adults'] = guests['adults']
            extracted_info['children'] = guests.get('children', 0)
            extracted_info['rooms'] = guests.get('rooms', 1)
            session_state['adults'] = guests['adults']
            session_state['children'] = guests.get('children', 0)
            session_state['rooms'] = guests.get('rooms', 1)
        
        # 4. Extract preferences
        preferences = self._extract_preferences(user_query)
        if preferences:
            extracted_info['preferences'] = preferences
            current_prefs = session_state.get('property_preferences', [])
            if not isinstance(current_prefs, list):
                current_prefs = []
            session_state['property_preferences'] = list(set(current_prefs + preferences))
        
        # 5. Check for specific hotel mention
        hotel = self._extract_hotel_name(user_query, session_state.get('destination'))
        if hotel:
            extracted_info['hotel'] = hotel['name']
            session_state['selected_property'] = hotel
        
        # Determine next step
        next_action = self._determine_next_action(session_state, extracted_info)
        response = self._build_response(session_state, extracted_info, next_action)
        
        return {
            'extracted_info': extracted_info,
            'updated_state': session_state,
            'response': response,
            'next_action': next_action
        }
    
    def _extract_destination(self, query: str) -> Optional[str]:
        """Extract destination with fallback to keyword matching"""
        if self.llm:
            try:
                return self._extract_destination_llm(query)
            except Exception as e:
                print(f"LLM extraction failed, using fallback: {e}")
        
        # Fallback: Simple keyword matching
        query_lower = query.lower()
        if any(word in query_lower for word in ['sri lanka', 'colombo', 'kandy', 'galle', 'ceylon']):
            return "Sri Lanka"
        elif any(word in query_lower for word in ['maldives', 'male', 'atoll']):
            return "Maldives"
        return None
    
    def _extract_destination_llm(self, query: str) -> Optional[str]:
        """LLM-based destination extraction"""
        prompt = f"""Extract the destination from: "{query}"
        
Available: Sri Lanka, Maldives
Respond with ONLY the destination name or "None"."""

        response = self.llm.invoke(prompt)
        result = (response.content if hasattr(response, 'content') else str(response)).strip()
        
        if result in ['Sri Lanka', 'Maldives']:
            return result
        return None
    
    def _extract_dates(self, query: str) -> Dict[str, Optional[str]]:
        """Extract dates with fallback to regex patterns"""
        if self.llm:
            try:
                return self._extract_dates_llm(query)
            except Exception as e:
                print(f"LLM date extraction failed, using fallback: {e}")
        
        # Fallback: Simple date pattern matching
        result = {'check_in': None, 'check_out': None}
        
        # Look for date patterns (YYYY-MM-DD, MM/DD/YYYY, etc.)
        date_pattern = r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}'
        dates_found = re.findall(date_pattern, query)
        
        if len(dates_found) >= 2:
            result['check_in'] = dates_found[0]
            result['check_out'] = dates_found[1]
        elif len(dates_found) == 1:
            result['check_in'] = dates_found[0]
            # Default to 2 nights
            try:
                check_in = datetime.strptime(dates_found[0], '%Y-%m-%d')
                check_out = check_in + timedelta(days=2)
                result['check_out'] = check_out.strftime('%Y-%m-%d')
            except:
                pass
        
        return result
    
    def _extract_dates_llm(self, query: str) -> Dict[str, Optional[str]]:
        """LLM-based date extraction"""
        today = datetime.now()
        prompt = f"""Today is {today.strftime('%Y-%m-%d')} (%A).

Extract check-in and check-out dates from: "{query}"

Rules:
- Return dates in YYYY-MM-DD format
- For relative dates like "next weekend", "tomorrow", calculate from today
- If only one date mentioned, assume 2-night stay
- If no dates, return null

Respond with ONLY JSON: {{"check_in": "YYYY-MM-DD or null", "check_out": "YYYY-MM-DD or null"}}"""

        response = self.llm.invoke(prompt)
        result_text = response.content if hasattr(response, 'content') else str(response)
        
        try:
            return json.loads(result_text.strip())
        except:
            return {'check_in': None, 'check_out': None}
    
    def _extract_guests(self, query: str) -> Dict[str, Optional[int]]:
        """Extract guest counts with fallback to keyword matching"""
        if self.llm:
            try:
                return self._extract_guests_llm(query)
            except Exception as e:
                print(f"LLM guest extraction failed, using fallback: {e}")
        
        # Fallback: Pattern matching
        query_lower = query.lower()
        result = {'adults': None, 'children': 0, 'rooms': 1}
        
        # Look for numbers followed by adult/adults/people/guests
        adult_pattern = r'(\d+)\s*(?:adult|people|guest|person)'
        adult_match = re.search(adult_pattern, query_lower)
        if adult_match:
            result['adults'] = int(adult_match.group(1))
        
        # Look for solo/couple/family keywords
        if 'solo' in query_lower or 'alone' in query_lower:
            result['adults'] = 1
        elif 'couple' in query_lower:
            result['adults'] = 2
        elif 'family' in query_lower:
            result['adults'] = 2
            result['children'] = 2
        
        # Look for children
        children_pattern = r'(\d+)\s*(?:child|children|kid)'
        child_match = re.search(children_pattern, query_lower)
        if child_match:
            result['children'] = int(child_match.group(1))
        
        # Look for rooms
        rooms_pattern = r'(\d+)\s*(?:room|rooms)'
        room_match = re.search(rooms_pattern, query_lower)
        if room_match:
            result['rooms'] = int(room_match.group(1))
        
        return result
    
    def _extract_guests_llm(self, query: str) -> Dict[str, Optional[int]]:
        """LLM-based guest extraction"""
        prompt = f"""Extract guest information from: "{query}"

Respond with ONLY JSON: {{"adults": number or null, "children": number or 0, "rooms": number or 1}}

Examples:
- "solo traveler" → {{"adults": 1, "children": 0, "rooms": 1}}
- "couple" → {{"adults": 2, "children": 0, "rooms": 1}}
- "family of 4" → {{"adults": 2, "children": 2, "rooms": 1}}
- "2 adults, 1 child, 2 rooms" → {{"adults": 2, "children": 1, "rooms": 2}}"""

        response = self.llm.invoke(prompt)
        result_text = response.content if hasattr(response, 'content') else str(response)
        
        try:
            return json.loads(result_text.strip())
        except:
            return {'adults': None, 'children': 0, 'rooms': 1}
    
    def _extract_preferences(self, query: str) -> List[str]:
        """Extract hotel preferences"""
        query_lower = query.lower()
        preferences = []
        
        # Define preference keywords
        pref_map = {
            'beach': ['beach', 'coastal', 'ocean', 'seaside', 'waterfront'],
            'luxury': ['luxury', 'premium', '5-star', 'upscale', 'deluxe'],
            'budget': ['budget', 'affordable', 'economical', 'cheap'],
            'city': ['city', 'urban', 'downtown', 'colombo'],
            'romantic': ['romantic', 'honeymoon', 'couple', 'intimate'],
            'family': ['family', 'kids', 'children', 'family-friendly'],
            'spa': ['spa', 'wellness', 'massage', 'relaxation'],
            'nature': ['nature', 'eco', 'wildlife', 'safari']
        }
        
        for pref_key, keywords in pref_map.items():
            if any(kw in query_lower for kw in keywords):
                preferences.append(pref_key)
        
        return preferences
    
    def _extract_hotel_name(self, query: str, destination: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Extract specific hotel name mentioned in query"""
        query_lower = query.lower()
        
        # Search through hotels data
        for dest in self.hotels_data.get('destinations', []):
            # Filter by destination if specified
            if destination and dest['name'] != destination:
                continue
            
            for hotel in dest.get('properties', []):
                hotel_name = hotel['name'].lower()
                hotel_words = set(hotel_name.split()) - {'hotel', 'resort', 'by', 'the', 'at', 'in'}
                
                # Check if significant hotel name parts are in query
                matches = sum(1 for word in hotel_words if word in query_lower)
                if matches >= 2 or hotel_name in query_lower:
                    return hotel
        
        return None
    
    def _determine_next_action(self, state: Dict[str, Any], extracted: Dict[str, Any]) -> str:
        """Determine the next step in booking flow"""
        has_destination = state.get('destination') is not None
        has_hotel = state.get('selected_property') is not None
        has_dates = state.get('check_in') is not None
        has_guests = state.get('adults') is not None
        has_preferences = len(state.get('property_preferences', [])) > 0
        
        if has_hotel and has_dates and has_guests:
            return 'show_rooms'
        elif has_hotel:
            return 'collect_booking_details'
        elif has_destination and has_preferences:
            return 'recommend_hotels'
        elif has_destination:
            return 'ask_preferences'
        else:
            return 'ask_destination'
    
    def _build_response(self, state: Dict[str, Any], extracted: Dict[str, Any], next_action: str) -> str:
        """Build contextual response based on state and next action"""
        response = ""
        
        # Acknowledge extracted info from THIS query
        if extracted:
            ack_items = []
            if 'destination' in extracted:
                ack_items.append(f"destination: **{extracted['destination']}**")
            if 'check_in' in extracted:
                ack_items.append(f"dates: **{extracted['check_in']} to {extracted['check_out']}**")
            if 'adults' in extracted:
                guest_text = f"{extracted['adults']} adult" + ("s" if extracted['adults'] > 1 else "")
                if extracted.get('children', 0) > 0:
                    guest_text += f", {extracted['children']} child" + ("ren" if extracted['children'] > 1 else "")
                ack_items.append(f"guests: **{guest_text}**")
            if 'hotel' in extracted:
                ack_items.append(f"hotel: **{extracted['hotel']}**")
            
            if ack_items:
                response += "Perfect! I've noted: " + ", ".join(ack_items) + ".\n\n"
        
        # Show what we ALREADY HAVE in the complete state
        current_info = []
        if state.get('destination'):
            current_info.append(f"destination={state['destination']}")
        if state.get('selected_property'):
            current_info.append(f"hotel={state['selected_property']['name']}")
        if state.get('check_in'):
            current_info.append(f"dates={state['check_in']} to {state['check_out']}")
        if state.get('adults'):
            guests_text = f"{state['adults']} adult"
            if state['adults'] > 1:
                guests_text += "s"
            if state.get('children', 0) > 0:
                guests_text += f", {state['children']} child" + ("ren" if state['children'] > 1 else "")
            current_info.append(f"guests={guests_text}")
        
        if current_info:
            response += f"✓ I already have: {', '.join(current_info)}.\n\n"
        
        # Next step guidance
        if next_action == 'ask_destination':
            response += "Which destination interests you?\n• **Sri Lanka** - Beaches, culture, diverse experiences\n• **Maldives** - Luxury island resorts"
        
        elif next_action == 'ask_preferences':
            response += f"Great! What type of property are you looking for in **{state['destination']}**?\n"
            response += "You can describe your ideal vacation (e.g., 'beach resort', 'luxury city hotel', 'family-friendly')"
        
        elif next_action == 'recommend_hotels':
            response += "Let me find the perfect properties for you!"
        
        elif next_action == 'collect_booking_details':
            missing = []
            if not state.get('check_in'):
                missing.append("travel dates")
            if not state.get('adults'):
                missing.append("number of guests")
            if missing:
                response += f"To complete your booking for **{state['selected_property']['name']}**, I need: {', '.join(missing)}"
        
        elif next_action == 'show_rooms':
            response += "Great! I have all your details. Let me check available rooms..."
        
        return response


class HotelRecommendationTool:
    """Simplified hotel recommendation tool"""
    
    def __init__(self, hotels_data: Dict[str, Any], llm=None):
        self.hotels_data = hotels_data
        self.llm = llm
    
    def recommend_hotels(self, destination: str, preferences: List[str], query: str = "") -> List[Dict[str, Any]]:
        """
        Recommend hotels based on destination and preferences
        
        Returns top 1-3 hotels ranked by relevance
        """
        # Get hotels for destination
        hotels = []
        for dest in self.hotels_data.get('destinations', []):
            if dest['name'] == destination:
                hotels = dest.get('properties', [])
                break
        
        if not hotels:
            return []
        
        # If no preferences, return all hotels
        if not preferences and not query:
            return hotels[:3]
        
        # Use LLM for intelligent ranking if available
        if self.llm:
            try:
                return self._rank_hotels_llm(hotels, preferences, query)
            except Exception as e:
                print(f"LLM ranking failed, using simple filter: {e}")
        
        # Fallback: Simple preference matching
        return self._simple_rank(hotels, preferences)
    
    def _rank_hotels_llm(self, hotels: List[Dict], preferences: List[str], query: str) -> List[Dict]:
        """Use LLM to rank hotels"""
        hotels_info = [{
            'index': i,
            'name': h['name'],
            'type': h.get('type', ''),
            'location': h.get('location', ''),
            'description': h.get('description', '')
        } for i, h in enumerate(hotels)]
        
        prompt = f"""Rank these hotels for a user who wants: {', '.join(preferences)}
Query: "{query}"

Hotels: {json.dumps(hotels_info, indent=2)}

Respond with ONLY a JSON array of top 3 hotel indices: [index1, index2, index3]"""

        response = self.llm.invoke(prompt)
        result_text = response.content if hasattr(response, 'content') else str(response)
        
        try:
            indices = json.loads(result_text.strip())
            return [hotels[i] for i in indices[:3] if i < len(hotels)]
        except:
            return hotels[:3]
    
    def _simple_rank(self, hotels: List[Dict], preferences: List[str]) -> List[Dict]:
        """Simple preference-based ranking"""
        scored_hotels = []
        
        for hotel in hotels:
            score = 0
            hotel_text = f"{hotel.get('name', '')} {hotel.get('description', '')} {hotel.get('type', '')}".lower()
            
            for pref in preferences:
                if pref.lower() in hotel_text:
                    score += 1
            
            scored_hotels.append((score, hotel))
        
        # Sort by score (descending) and return top 3
        scored_hotels.sort(key=lambda x: x[0], reverse=True)
        return [h for _, h in scored_hotels[:3]]


class ReservationUrlTool:
    """Generate reservation/booking URLs"""
    
    @staticmethod
    def generate_reservation_url(hotel: Dict[str, Any], booking_data: Dict[str, Any]) -> str:
        """
        Generate booking URL matching Cinnamon Hotels reservation system format.
        
        Expected format:
        https://reservations.cinnamonhotels.com/?adult=2&arrive=2025-10-20&chain=31106&child=0
        &currency=USD&depart=2025-10-21&hotel=42169&level=hotel&locale=en-US&rooms=1
        """
        base_url = "https://reservations.cinnamonhotels.com/"
        
        # Build params matching the official format
        params = {
            'adult': booking_data.get('adults', 1),
            'child': booking_data.get('children', 0),
            'rooms': booking_data.get('rooms', 1),
            'arrive': booking_data.get('check_in', ''),
            'depart': booking_data.get('check_out', ''),
            'hotel': hotel.get('id', ''),
            'chain': hotel.get('chain_id', '31106'),
            'level': 'hotel',
            'locale': 'en-US',
            'currency': 'USD',
            'productcurrency': 'USD',
            'segment': 'noMealPlanAssigned'
        }
        
        # Remove empty params
        params = {k: v for k, v in params.items() if v}
        
        return f"{base_url}?{urlencode(params)}"


class MCPToolRegistry:
    """Simplified registry for all MCP tools"""
    
    def __init__(self, hotels_data: Dict[str, Any], llm=None):
        self.universal_booking = UniversalBookingTool(hotels_data, llm)
        self.hotel_recommendation = HotelRecommendationTool(hotels_data, llm)
        self.reservation_url = ReservationUrlTool()
        
        # Keep legacy tools for backward compatibility
        self.destination_extraction = self.universal_booking
        self.date_extraction = self.universal_booking
        self.guest_extraction = self.universal_booking
        self.preference_extraction = self.universal_booking
        self.hotel_search = self.hotel_recommendation
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return [
            'process_booking_query',  # Main universal tool
            'recommend_hotels',
            'generate_reservation_url'
        ]
