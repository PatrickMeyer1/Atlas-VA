from text_to_num import text2num

from src.control_system.garden_controller import GardenController
from src.control_system.garden_constants import PlantType, ToolType

class GardenFulfillment:
    def __init__(self):
        self.garden_controller = GardenController() # could be an argument

        self.VALID_SEEDS = [p.value for p in PlantType]
        self.VALID_TOOLS = [t.value for t in ToolType]
        self.VALID_DIRECTIONS = ["up", "down", "left", "right"] # we can expand this later with synonyms and whatnot

    def fulfill(self, intent_dict):
        intent = intent_dict["intent"]
        slots = intent_dict.get("slots", {})

        match intent:
            case "move":
                direction = slots.get("direction")
                if not direction:
                    return {"intent": intent, "success": False, "error_code": "missing_direction"}
                elif direction.lower() not in self.VALID_DIRECTIONS:
                    return {"intent": intent, "success": False, "error_code": "invalid_direction", "data": {"direction": direction, "valid_options": self.VALID_DIRECTIONS}}
                
                try:
                    num = text2num(slots.get("numtiles"), 'en') # default to 1 if none provided
                except Exception: 
                    num = 1

                # Fulfill
                return self.garden_controller.handle_voice_intent({"intent": intent, "slots": {"direction": slots["direction"], "num_tiles": num}}) # num_tiles, need to parse number and add to slots
            case "plant" | "pickup_seed":
                seed = slots.get("seed") or slots.get("plantname")
                if not seed:
                    return {"intent": intent, "success": False, "error_code": "missing_seed"}
                
                # Plural to singular (e.g. "carrots" to "carrot")
                if seed.endswith("s") and seed[:-1] in self.VALID_SEEDS: # carrots, lettuces
                    seed = seed[:-1]
                elif seed.endswith("es") and seed[:-2] in self.VALID_SEEDS: # tomatoes
                    seed = seed[:-2]

                if seed.lower() not in self.VALID_SEEDS:
                    return {"intent": intent, "success": False, "error_code": "invalid_seed", "data": {"provided": seed, "valid_options": self.VALID_SEEDS}}
                
                return self.garden_controller.handle_voice_intent({
                    "intent": intent, 
                    "slots": {"seed": seed.lower()}
                })
            case "water" | "till" | "fill_water" | "restart" | "game_help":
                return self.garden_controller.handle_voice_intent({"intent": intent, "slots": {}})
            case "pickup_tool":
                tool = slots.get("tool")
                if not tool:
                    return {"intent": intent, "success": False, "error_code": "missing_tool"}
                
                if tool.lower() not in self.VALID_TOOLS:
                    return {"intent": intent, "success": False, "error_code": "invalid_tool", "data": {"provided": tool, "valid_options": self.VALID_TOOLS}}
                
                return self.garden_controller.handle_voice_intent({
                    "intent": intent, 
                    "slots": {"tool": tool.lower()}
                })
            case _:
                return {"intent": intent, "success": False, "error_code": "invalid_intent"}