import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import streamlit as st
from langchain_core.tools import tool


def filter_hotels_by_location_and_type(hotels_data, location):
    """
    Filter hotels based on location and type criteria:
    - If location is Sri Lanka: include only hotels and resorts (exclude Maldives type)
    - If location is Maldives: include only Maldives type
    Returns list of filtered hotels with name, description, and type
    """
    filtered_hotels = []

    for hotel in hotels_data:
        hotel_type = hotel.get("Type", "")
        hotel_location = hotel.get("Location", "")

        # Filter based on location
        if location == "Sri Lanka":
            # For Sri Lanka: include hotels and resorts but exclude Maldives type
            if "Sri Lanka" in hotel_location and hotel_type != "Maldives":
                filtered_hotels.append(
                    {
                        "Name": hotel.get("Name", ""),
                        "Type": hotel_type,
                        "Location": hotel_location,
                        "UniqueDescription": hotel.get("UniqueDescription", ""),
                        "RoomTypes": hotel.get("RoomTypes", []),
                        "TotalRooms": hotel.get("TotalRooms", 0),
                    }
                )
        elif location == "Maldives":
            # For Maldives: include only Maldives type
            if hotel_type == "Maldives":
                filtered_hotels.append(
                    {
                        "Name": hotel.get("Name", ""),
                        "Type": hotel_type,
                        "Location": hotel_location,
                        "UniqueDescription": hotel.get("UniqueDescription", ""),
                        "RoomTypes": hotel.get("RoomTypes", []),
                        "TotalRooms": hotel.get("TotalRooms", 0),
                    }
                )

    return filtered_hotels


def calculate_total_cost(reservation_state):
    """Calculate the total cost based on room rate, duration, guests, children, and meal plan"""

    # Get reservation details
    duration = reservation_state.get("duration", 1)
    guests = reservation_state.get("guests", 1)
    children = reservation_state.get("children", 0)
    rooms_needed = reservation_state.get("rooms_needed", 1)
    meal_type = reservation_state.get("meal_type", "Room Only")
    selected_room_data = reservation_state.get("selected_room_data", {})

    # Get room rate per night
    room_rate_per_night = selected_room_data.get(
        "base_rate_per_night", 200
    )  # Default fallback

    # Calculate base room cost
    base_room_cost = room_rate_per_night * duration * rooms_needed

    # Define meal plan costs per person per day
    meal_costs = {
        "room only": 0,
        "breakfast included": 25,
        "half board": 50,
        "full board": 75,
        "all inclusive": 120,
    }

    # Get meal cost per person per day
    meal_cost_per_day = meal_costs.get(meal_type.lower(), 0)

    # Calculate total meal costs
    total_people = guests + children
    total_meal_cost = meal_cost_per_day * total_people * duration

    # Calculate total cost
    total_cost = base_room_cost + total_meal_cost

    return {
        "total_cost": total_cost,
        "breakdown": {
            "room_cost": base_room_cost,
            "meal_cost": total_meal_cost,
            "room_rate_per_night": room_rate_per_night,
            "meal_cost_per_person_per_day": meal_cost_per_day,
            "duration": duration,
            "guests": guests,
            "children": children,
            "rooms": rooms_needed,
        },
    }


def parse_booking_details(booking_info: str) -> dict:
    """Parse user booking information into structured data"""
    import re
    from datetime import datetime, timedelta

    info = booking_info.lower()
    original_info = booking_info  # Keep original case for dates
    parsed = {
        "check_in": None,
        "check_out": None,
        "guests": None,
        "children": None,
        "rooms": None,
        "budget_range": None,
    }

    # Parse check-in date (various formats)
    checkin_patterns = [
        r"check-in[:\s]+(\d{4}-\d{2}-\d{2})",  # check-in 2025-10-09
        r"checkin[:\s]+(\d{4}-\d{2}-\d{2})",  # checkin 2025-10-09
        r"(\d{4}-\d{2}-\d{2})\s*(?:to|,|\s+check)",  # 2025-10-09 to/,/check
    ]

    for pattern in checkin_patterns:
        match = re.search(pattern, original_info, re.IGNORECASE)
        if match:
            parsed["check_in"] = match.group(1)
            break

    # Parse check-out date (various formats)
    checkout_patterns = [
        r"check-out[:\s]+(\d{4}-\d{2}-\d{2})",  # check-out 2025-10-15
        r"checkout[:\s]+(\d{4}-\d{2}-\d{2})",  # checkout 2025-10-15
        r"(?:to|,)\s*(\d{4}-\d{2}-\d{2})",  # to 2025-10-15
        r"check-out\s+(\d{4}-\d{2}-\d{2})",  # check-out 2025-10-15
    ]

    for pattern in checkout_patterns:
        match = re.search(pattern, original_info, re.IGNORECASE)
        if match:
            parsed["check_out"] = match.group(1)
            break

    # Parse guest count
    guest_matches = re.findall(r"(\d+)\s*(?:adult|guest|people|person)", info)
    if guest_matches:
        parsed["guests"] = int(guest_matches[0])

    # Parse children count
    children_matches = re.findall(r"(\d+)\s*(?:child|children|kid)", info)
    if children_matches:
        parsed["children"] = int(children_matches[0])

    # Parse room count
    room_matches = re.findall(r"(\d+)\s*room", info)
    if room_matches:
        parsed["rooms"] = int(room_matches[0])

    # Parse budget range - improved pattern to avoid matching dates
    budget_patterns = [
        r"budget\s+\$?(\d+)[-\s]*(?:to|-|\$)\s*\$?(\d+)",  # budget $100-$500
        r"\$(\d{2,4})[-\s]*(?:to|-)\s*\$(\d{2,4})",  # $100-$500 (2-4 digits to avoid dates)
        r"budget\s+\$?(\d+)\s*[-]\s*\$?(\d+)",  # budget $100-$500
    ]

    for pattern in budget_patterns:
        budget_matches = re.findall(pattern, info)
        if budget_matches:
            min_budget, max_budget = budget_matches[0]
            # Only accept reasonable budget ranges (not dates)
            min_val, max_val = int(min_budget), int(max_budget)
            if min_val < 2000 and max_val < 2000 and min_val < max_val:
                parsed["budget_range"] = [min_val, max_val]
                break

    return parsed
