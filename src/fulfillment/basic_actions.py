from text_to_num import text2num
import time
import requests

from src.fulfillment.weather_constants import WEATHER_CODE_MAP, WEATHER_ICON_MAP, WEATHER_THEME_MAP

class BasicFulfillment:
    def __init__(self):
        self.VALID_UNITS = ["second", "seconds", "minute", "minutes", "hour", "hours"]

        self.CURRENT_VARS = (
            "temperature_2m,"           # Temperature
            "relative_humidity_2m,"     # Humidity
            "apparent_temperature,"     # Feels like temperature
            "precipitation,"            # Precipitation (rain amount)
            "weather_code,"             # Weather condition code
            "wind_speed_10m"            # Wind Speed
        )

        self.WEATHER_CODE_MAP = WEATHER_CODE_MAP
        self.WEATHER_ICON_MAP = WEATHER_ICON_MAP
        self.WEATHER_THEME_MAP = WEATHER_THEME_MAP

    def _get_coordinates(self, city, country=None):
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": city, "count": 10}

        try:
            response = requests.get(url, params=params)

            if response.status_code != 200:
                return None

            data = response.json()
            results = data.get("results")

            if not results: # no results found for city
                return None

            if country:
                for res in results:
                    if country.lower() == res.get("country", "").lower():
                        return res["latitude"], res["longitude"], res["country"]

            # Default first if no country provided in function argument
            first_result = results[0]
            return first_result["latitude"], first_result["longitude"], first_result.get("country")
        except Exception:
            return None
    
    def _call_weather_api(self, lat, lon):
        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": self.CURRENT_VARS,
            "timezone": "auto"
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                return None
            return response.json()
        except Exception:
            return None

    def fulfill(self, intent_dict):
        intent = intent_dict["intent"]
        slots = intent_dict.get("slots", {})

        match intent:
            case "oos" | "greetings" | "goodbye":
                return {"intent": intent, "success": True, "data": {}, "error_code": None}
            case "timer":
                if not slots.get("duration"):
                    return {"intent": intent, "success": False, "error_code": "missing_duration", "data": {"timername": slots.get("timername", "standard")}}
                
                timer_name = slots.get("timername", "standard")

                # need to parse duration and unit in same slot
                duration_str = slots["duration"]
                duration_parts = duration_str.split()

                if len(duration_parts) != 2: # we need exactly 2 parts (e.g. "5 minutes")
                    return {"intent": intent, "success": False, "error_code": "invalid_duration_format", "data": {"duration": duration_str, "timername": timer_name}}
                
                duration, unit = duration_parts

                if unit.lower() not in self.VALID_UNITS:
                    return {"intent": intent, "success": False, "error_code": "invalid_unit", "data": {"unit": unit, "timername": timer_name}}
                try:
                    duration_num = text2num(duration, 'en')
                except Exception:
                    return {"intent": intent, "success": False, "error_code": "invalid_duration", "data": {"duration": duration, "timername": timer_name}}
                
                multiplier = 0

                if 'second' in unit.lower():
                    multiplier = 1
                elif 'minute' in unit.lower():
                    multiplier = 60
                elif 'hour' in unit.lower():
                    multiplier = 3600

                end_time = time.time() + (duration_num * multiplier)

                return {
                    "intent": intent,
                    "success": True,
                    "data": {"duration": duration_num, "unit": unit, "timername": timer_name, "end_time": end_time},
                    "error_code": None
                }

            case "weather":
                raw_city = slots.get("city", "")
                raw_country = slots.get("country", "")

                # Use Ottawa as default and capitalize
                city = raw_city.capitalize() if raw_city else "Ottawa"
                country = raw_country.capitalize() if raw_country else None

                coordinates = self._get_coordinates(city, country)
                
                if not coordinates: 
                    return {"intent": intent, "success": False, "error_code": "invalid_location"}

                lat, lon, resolved_country = coordinates

                weather_data = self._call_weather_api(lat, lon)

                if not weather_data:
                    return {"intent": intent, "success": False, "error_code": "api_error", "data": {"city": city, "country": resolved_country}}
                
                current_weather = weather_data.get("current", {})
                current_units = weather_data.get("current_units", {})

                temperature = current_weather.get("temperature_2m")
                humidity = current_weather.get("relative_humidity_2m")
                feels_like = current_weather.get("apparent_temperature")
                precipitation = current_weather.get("precipitation")
                weather_code = current_weather.get("weather_code")
                weather_condition = self.WEATHER_CODE_MAP.get(weather_code, "unknown")
                wind_speed = current_weather.get("wind_speed_10m")

                # UI elements
                icon = self.WEATHER_ICON_MAP.get(weather_code, "cloud")
                themes = self.WEATHER_THEME_MAP.get(icon, self.WEATHER_THEME_MAP["cloud"])

                temperature_unit = current_units.get("temperature_2m", "°C")
                wind_speed_unit = current_units.get("wind_speed_10m", "km/h")
                relative_humidity_unit = current_units.get("relative_humidity_2m", "%")
                apparent_temperature_unit = current_units.get("apparent_temperature", "°C")
                precipitation_unit = current_units.get("precipitation", "mm")

                return {
                    "intent": intent,
                    "success": True,
                    "data": {"temperature": temperature, "humidity": humidity, "feels_like": feels_like, "precipitation": precipitation, "weather_condition": weather_condition, "icon": icon, "theme": themes, "wind_speed": wind_speed, "city": city, "country": resolved_country, "temperature_unit": temperature_unit, "wind_speed_unit": wind_speed_unit, "relative_humidity_unit": relative_humidity_unit, "apparent_temperature_unit": apparent_temperature_unit, "precipitation_unit": precipitation_unit},
                    "error_code": None
                }