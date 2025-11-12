"""Weather tools using AccuWeather API for LangChain.

========================================================================================
 Copyright (c) 2025 OCTAVE. All rights reserved.

 This is proprietary and confidential software of OCTAVE.
 Unauthorized use, reproduction, or distribution is strictly prohibited.
========================================================================================
"""

import logging
import os
from typing import Optional

import dotenv
import requests
from langchain_core.tools import tool

# Load environment variables from .env file
dotenv.load_dotenv()

logger = logging.getLogger(__name__)

# AccuWeather location keys for major cities in Sri Lanka and Maldives
LOCATION_KEYS = {
    # Sri Lanka
    "colombo": "318203",
    "kandy": "244398",
    "galle": "242110",
    "jaffna": "242838",
    "trincomalee": "318850",
    "nuwara eliya": "244895",
    "ella": "241670",
    "bentota": "240623",
    "negombo": "244804",
    "sri lanka": "318203",  # Default to Colombo
    # Maldives
    "male": "241883",
    "maldives": "241883",  # Default to Male
    "addu city": "241347",
    "fuvahmulah": "242094",
}


def get_location_key(city: str) -> Optional[str]:
    """Get AccuWeather location key for a city."""
    return LOCATION_KEYS.get(city.lower().strip())


def fetch_current_weather(location_key: str) -> Optional[dict]:
    """Fetch current weather from AccuWeather API."""
    api_key = os.getenv("ACCUWEATHER_API_KEY")
    if not api_key:
        logger.error("ACCUWEATHER_API_KEY not found in environment")
        return None

    try:
        base_url = "http://dataservice.accuweather.com"
        url = f"{base_url}/currentconditions/v1/{location_key}"
        params = {"apikey": api_key, "details": "true"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data and len(data) > 0:
            return data[0]
        return None

    except requests.RequestException as e:
        logger.error("Error fetching current weather: %s", e)
        return None


def fetch_forecast(location_key: str, days: int = 5) -> Optional[list]:
    """Fetch weather forecast from AccuWeather API."""
    api_key = os.getenv("ACCUWEATHER_API_KEY")
    if not api_key:
        logger.error("ACCUWEATHER_API_KEY not found in environment")
        return None

    try:
        base_url = "http://dataservice.accuweather.com"
        endpoint = "1day" if days == 1 else "5day"
        url = f"{base_url}/forecasts/v1/daily/{endpoint}/{location_key}"
        params = {"apikey": api_key, "details": "true", "metric": "true"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data.get("DailyForecasts", [])

    except requests.RequestException as e:
        logger.error("Error fetching weather forecast: %s", e)
        return None


@tool
def get_current_weather(city: str) -> str:
    """Get current weather conditions for a city in Sri Lanka or Maldives.

    Args:
        city: City name (e.g., "Colombo", "Male", "Kandy", "Galle", etc.)

    Returns:
        Current weather information including temperature, conditions, humidity, and wind in raw data format for natural language generation
    """
    location_key = get_location_key(city)

    if not location_key:
        available_cities = ", ".join(
            [
                c.title()
                for c in LOCATION_KEYS.keys()
                if c not in ["sri lanka", "maldives"]
            ]
        )
        return (
            f"Weather information not available for '{city}'. "
            f"Available cities: {available_cities}"
        )

    weather_data = fetch_current_weather(location_key)
    if not weather_data:
        return f"Unable to fetch current weather for {city.title()} at the moment."

    try:
        temp_c = weather_data["Temperature"]["Metric"]["Value"]
        temp_f = weather_data["Temperature"]["Imperial"]["Value"]
        weather_text = weather_data["WeatherText"]
        humidity = weather_data.get("RelativeHumidity", "N/A")
        wind_speed = (
            weather_data.get("Wind", {})
            .get("Speed", {})
            .get("Metric", {})
            .get("Value", "N/A")
        )
        uv_index = weather_data.get("UVIndexText", "N/A")

        # Return structured data for LLM to convert to natural language
        result = (
            f"City: {city.title()}, "
            f"Condition: {weather_text}, "
            f"Temperature: {temp_c}°C ({temp_f}°F), "
            f"Humidity: {humidity}%, "
        )

        if wind_speed != "N/A":
            result += f"Wind Speed: {wind_speed} km/h, "

        result += f"UV Index: {uv_index}"

        return result

    except (KeyError, TypeError) as e:
        logger.error("Error formatting weather data: %s", e)
        return f"Error retrieving weather data for {city.title()}."


@tool
def get_weather_forecast(city: str, days: int = 5) -> str:
    """Get weather forecast for a city in Sri Lanka or Maldives.

    Args:
        city: City name (e.g., "Colombo", "Male", "Kandy", "Galle", etc.)
        days: Number of days for forecast (1 or 5, default is 5)

    Returns:
        Weather forecast with daily temperature ranges and conditions in raw data format for natural language generation
    """
    location_key = get_location_key(city)

    if not location_key:
        available_cities = ", ".join(
            [
                c.title()
                for c in LOCATION_KEYS.keys()
                if c not in ["sri lanka", "maldives"]
            ]
        )
        return (
            f"Weather information not available for '{city}'. "
            f"Available cities: {available_cities}"
        )

    # Normalize days to 1 or 5
    days = 1 if days == 1 else 5

    forecast_data = fetch_forecast(location_key, days)
    if not forecast_data:
        return f"Unable to fetch weather forecast for {city.title()} at the moment."

    try:
        # Return structured data for LLM to convert to natural language
        result = f"Weather forecast for {city.title()} for {days} day(s): "

        forecast_items = []
        for day in forecast_data[:days]:
            date = day.get("Date", "").split("T")[0]
            temp_min = day["Temperature"]["Minimum"]["Value"]
            temp_max = day["Temperature"]["Maximum"]["Value"]
            day_weather = day.get("Day", {}).get("IconPhrase", "N/A")
            night_weather = day.get("Night", {}).get("IconPhrase", "N/A")

            forecast_items.append(
                f"On {date}, temperatures will range from {temp_min}°C to {temp_max}°C "
                f"with {day_weather.lower()} during the day and {night_weather.lower()} at night"
            )

        result += "; ".join(forecast_items) + "."

        return result

    except (KeyError, TypeError, IndexError) as e:
        logger.error("Error formatting forecast data: %s", e)
        return f"Error retrieving forecast data for {city.title()}."


def get_weather_tools():
    """Get list of weather-related tools for LangChain agent.

    Returns:
        List of weather tools
    """
    return [get_current_weather, get_weather_forecast]
