from pathlib import Path
from text_to_num import text2num

from control_system.garden_interface import GardenController
from control_system.constants import PlantType, ToolType
# etc.

# This will deal with the output from the VoiceAssitanceNLU. It will clean up the output or return a don't have enough info or wtv
# It will interact with the interface of each intent (If needed)

# need to deal with string to text

# not doing tempaltes yet, later

class Controller:
    def __init__(self):
        self.garden_controller = GardenController() # could be an argument

    def _make_response(self, tts_message, success=False, image_path=None):
        return {"tts_message": tts_message, "success": success, "image_path": image_path}

    def cleanup_and_dispatch(self, intent_dict):
        intent = intent_dict["intent"]
        slots = intent_dict.get("slots", {})

        VALID_SEEDS = [p.value for p in PlantType]
        VALID_TOOLS = [t.value for t in ToolType]
        VALID_DIRECTIONS = ["up", "down", "left", "right"] # we can expand this later with synonyms and whatnot

        match intent:
            case "oos":
                pass
            case "greetings":
                pass
            case "goodbye":
                pass
            case "timer":
                pass
            case "weather":
                pass
            case "get_plant_sunlight":
                pass
            case "get_plant_watering_care":
                pass
            case "get_plant_cycle":
                pass
            case "get_plant_edibility":
                pass
            case "search_plants_by_environment":
                pass
            # Control System
            case "move":
                direction = slots.get("direction")
                if not direction:
                    return self._make_response(
                        "Which direction? Up, down, left, or right?",
                        success=False
                    )
                elif direction.lower() not in VALID_DIRECTIONS:
                    return self._make_response(
                        "Direction must be up, down, left, or right.",
                        success=False
                    )

                try:
                    num = text2num(slots.get("numtiles"), 'en') # default to 1 if none provided
                except Exception: 
                    num = 1

                print(num)

                return self.garden_controller.handle_voice_intent({"intent": intent, "slots": {"direction": slots["direction"], "num_tiles": num}}) # num_tiles, need to parse number and add to slots
            case "plant" | "pickup_seed":
                seed = slots.get("seed") or slots.get("plantname")
                if not seed:
                    return self._make_response(
                        f"What do you want to {intent}?",
                        success=False
                    )
                
                if seed.lower() not in VALID_SEEDS:
                    return self._make_response(
                        f"You can only {intent} carrot, lettuce, or tomatoes.",
                        success=False
                    )
                
                return self.garden_controller.handle_voice_intent({
                    "intent": intent, 
                    "slots": {"seed": seed.lower()}
                })
            case "water" | "till" | "fill_water" | "restart" | "game_help":
                intent = intent.replace("game_help", "help")
                return self.garden_controller.handle_voice_intent({"intent": intent, "slots": {}})
            case "pickup_tool":
                tool = slots.get("tool")
                if not tool:
                    return self._make_response(
                        "What tool should I pick up?",
                        success=False
                    )
                
                if tool.lower() not in VALID_TOOLS:
                    return self._make_response(
                        "You can only pick up the watering can or the hoe.",
                        success=False
                    )
                
                return self.garden_controller.handle_voice_intent({
                    "intent": intent, 
                    "slots": {"tool": tool.lower()}
                })
            case _:
                return self._make_response(
                    "Sorry, I don't understand that command.",
                    success=False
                )

        # For now, while passing the other intents to not get a crash
        return self._make_response(
            "Sorry, I don't understand that command.",
            success=False
        )