"""
MCP-compatible tools for hotel reservation system
"""
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode


class HotelSearchTool:
    """MCP tool for searching hotels"""
    
    def __init__(self, hotels_data: Dict[str, Any]):
        self.hotels_data = hotels_data
    
    def search_hotels(self, destination: str, preferences: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for hotels by destination and preferences
        
        Args:
            destination: "Sri Lanka" or "Maldives"
            preferences: List of preferences like ["coastal", "romantic", "family"]
            
        Returns:
            List of matching hotel properties
        """
        dest_data = None
        for dest in self.hotels_data['destinations']:
            if dest['name'] == destination:
                dest_data = dest
                break
        
        if not dest_data:
            return []
        
        if not preferences:
            return dest_data['properties']
        
        # Score properties based on preference match
        scored_properties = []
        for prop in dest_data['properties']:
            score = 0
            for pref in preferences:
                if pref in prop.get('preferences', []):
                    score += 1
            scored_properties.append((score, prop))
        
        # Sort by score and return properties
        scored_properties.sort(key=lambda x: x[0], reverse=True)
        return [prop for score, prop in scored_properties]
    
    def find_property_by_name(self, property_name: str, destination: str) -> Optional[Dict[str, Any]]:
        """
        Find a specific property by name
        
        Args:
            property_name: Name of the property to find
            destination: Destination to search in
            
        Returns:
            Property data if found, None otherwise
        """
        properties = self.search_hotels(destination)
        property_name_lower = property_name.lower()
        
        for prop in properties:
            if property_name_lower in prop['name'].lower():
                return prop
        
        return None


class DateExtractionTool:
    """MCP tool for extracting and parsing dates"""
    
    @staticmethod
    def extract_dates(query: str) -> Dict[str, Optional[str]]:
        """
        Extract check-in and check-out dates from natural language
        
        Args:
            query: User query containing date information
            
        Returns:
            Dictionary with check_in and check_out dates in YYYY-MM-DD format
        """
        query_lower = query.lower()
        today = datetime.now()
        
        # Check for "next weekend"
        if 'next weekend' in query_lower:
            days_ahead = 7 - today.weekday() + 4  # Next Friday
            check_in = today + timedelta(days=days_ahead)
            check_out = check_in + timedelta(days=2)  # Sunday
            return {
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d')
            }
        
        # Check for "this weekend"
        elif 'this weekend' in query_lower or 'weekend' in query_lower:
            days_ahead = (4 - today.weekday()) % 7  # This Friday
            check_in = today + timedelta(days=days_ahead)
            check_out = check_in + timedelta(days=2)  # Sunday
            return {
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d')
            }
        
        # Check for "tomorrow"
        elif 'tomorrow' in query_lower:
            check_in = today + timedelta(days=1)
            check_out = check_in + timedelta(days=1)  # Next day
            return {
                'check_in': check_in.strftime('%Y-%m-%d'),
                'check_out': check_out.strftime('%Y-%m-%d')
            }
        
        # Try to extract specific dates (simple patterns)
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
        ]
        
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, query)
            dates_found.extend(matches)
        
        if len(dates_found) >= 2:
            return {
                'check_in': dates_found[0],
                'check_out': dates_found[1]
            }
        elif len(dates_found) == 1:
            return {
                'check_in': dates_found[0],
                'check_out': None
            }
        
        return {'check_in': None, 'check_out': None}


class GuestExtractionTool:
    """MCP tool for extracting guest information"""
    
    @staticmethod
    def extract_guests(query: str) -> Dict[str, int]:
        """
        Extract guest information from natural language
        
        Args:
            query: User query containing guest information
            
        Returns:
            Dictionary with adults, children, and rooms counts
        """
        query_lower = query.lower()
        result = {'adults': 1, 'children': 0, 'rooms': 1}
        
        # Extract adult information
        adult_match = re.search(r'\b(\d+)\s*(adults?|people|persons?|guests?)\b', query_lower)
        if adult_match:
            result['adults'] = int(adult_match.group(1))
        
        # Extract children information
        children_match = re.search(r'\b(\d+)\s*(child|children|kids?)\b', query_lower)
        if children_match:
            result['children'] = int(children_match.group(1))
        elif 'family' in query_lower:
            # Infer children presence for family bookings
            result['children'] = 2  # Default assumption
        
        # Extract room information
        rooms_match = re.search(r'\b(\d+)\s*(rooms?|suites?)\b', query_lower)
        if rooms_match:
            result['rooms'] = int(rooms_match.group(1))
        
        return result


class PreferenceExtractionTool:
    """MCP tool for extracting hotel preferences"""
    
    def __init__(self, hotels_data: Dict[str, Any]):
        self.preference_mapping = hotels_data.get('preference_mapping', {})
    
    def extract_preferences(self, query: str) -> List[str]:
        """
        Extract hotel preferences from natural language
        
        Args:
            query: User query containing preference information
            
        Returns:
            List of matched preferences
        """
        query_lower = query.lower()
        preferences = []
        
        for pref_type, keywords in self.preference_mapping.items():
            if any(keyword in query_lower for keyword in keywords + [pref_type]):
                preferences.append(pref_type)
        
        return preferences


class DestinationExtractionTool:
    """MCP tool for extracting destination information"""
    
    @staticmethod
    def extract_destination(query: str) -> Optional[str]:
        """
        Extract destination from natural language
        
        Args:
            query: User query containing destination information
            
        Returns:
            Destination name ("Sri Lanka" or "Maldives") or None
        """
        query_lower = query.lower()
        
        # Direct destination mentions
        if any(word in query_lower for word in ['sri lanka', 'srilanka', 'ceylon']):
            return "Sri Lanka"
        if any(word in query_lower for word in ['maldives', 'maldive']):
            return "Maldives"
        
        # City/location mentions for Sri Lanka
        sri_lanka_places = ['colombo', 'kandy', 'galle', 'habarana', 'beruwala', 'negombo']
        if any(place in query_lower for place in sri_lanka_places):
            return "Sri Lanka"
        
        # Atoll mentions for Maldives
        maldives_places = ['atoll', 'kaafu', 'vaavu', 'meemu', 'male']
        if any(place in query_lower for place in maldives_places):
            return "Maldives"
        
        return None


class ReservationUrlTool:
    """MCP tool for generating reservation URLs"""
    
    @staticmethod
    def generate_reservation_url(property_data: Dict[str, Any], reservation_data: Dict[str, Any]) -> str:
        """
        Generate Cinnamon Hotels reservation URL
        
        Args:
            property_data: Hotel property information
            reservation_data: Reservation details (dates, guests, etc.)
            
        Returns:
            Complete reservation URL
        """
        base_url = "https://reservations.cinnamonhotels.com/"
        
        params = {
            '_ga': 'GA1.2.729931654.1757909071',
            'adult': reservation_data.get('adults', 1),
            'arrive': reservation_data.get('check_in', ''),
            'chain': property_data.get('chain_id', '31106'),
            'child': reservation_data.get('children', 0),
            'currency': 'USD',
            'depart': reservation_data.get('check_out', ''),
            'hotel': property_data.get('id', ''),
            'level': 'hotel',
            'locale': 'en-US',
            'productcurrency': 'USD',
            'rooms': reservation_data.get('rooms', 1),
            'segment': 'noMealPlanAssigned'
        }
        
        return base_url + '?' + urlencode(params)


class IntentClassificationTool:
    """MCP tool for classifying user intent"""
    
    @staticmethod
    def classify_intent(query: str) -> str:
        """
        Classify user intent from natural language
        
        Args:
            query: User query to classify
            
        Returns:
            Intent classification string
        """
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['book', 'reserve', 'confirm', 'complete']):
            return 'confirm_booking'
        elif any(word in query_lower for word in ['when', 'date', 'check', 'weekend', 'tomorrow', 'today', 'next week', 'this week']):
            return 'provide_dates'
        elif 'select' in query_lower or any(str(i) in query for i in range(1, 6)):
            return 'select_property'
        elif any(word in query_lower for word in ['search', 'find', 'look', 'want']):
            return 'search'
        else:
            return 'general_inquiry'


# MCP Tool Registry
class MCPToolRegistry:
    """Registry for all MCP tools"""
    
    def __init__(self, hotels_data: Dict[str, Any]):
        self.hotel_search = HotelSearchTool(hotels_data)
        self.date_extraction = DateExtractionTool()
        self.guest_extraction = GuestExtractionTool()
        self.preference_extraction = PreferenceExtractionTool(hotels_data)
        self.destination_extraction = DestinationExtractionTool()
        self.reservation_url = ReservationUrlTool()
        self.intent_classification = IntentClassificationTool()
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return [
            'search_hotels',
            'find_property_by_name',
            'extract_dates',
            'extract_guests',
            'extract_preferences',
            'extract_destination',
            'generate_reservation_url',
            'classify_intent'
        ]