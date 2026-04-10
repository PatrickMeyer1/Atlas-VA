from text_to_num import text2num
import time

class BasicFulfillment:
    def __init__(self):
        self.VALID_UNITS = ["second", "seconds", "minute", "minutes", "hour", "hours"]

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
                pass