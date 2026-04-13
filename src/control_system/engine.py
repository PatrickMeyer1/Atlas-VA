from .garden_constants import (
    TileType, PlantType, ToolType, MAX_X, MAX_Y, 
    STATION_X, RESOURCE_TILE_Y, TOOL_TILE_Y, 
    PLANT_COST, WATER_COST, MAX_PLANT, MAX_WATER
)
from .state import restart_game

class GardenEngine:
    def __init__(self):
        self.game_state = restart_game()

    def fulfill_intent(self, intent): # Intent is a dict with intent and slots
    
        action = intent["intent"]
        slots = intent.get("slots", {})

        # unwrap state to variables
        grid = self.game_state["grid"]
        x_position = self.game_state["position"]["x"]
        y_position = self.game_state["position"]["y"]
        current_tile = grid[y_position][x_position]
        seeds = self.game_state["inventory"]["consumables"]["seeds"]
        water = self.game_state["inventory"]["consumables"]["water"]
        tool = self.game_state["inventory"]["tool"]

        result = {
            "intent": action,
            "success": True,
            "is_changed": False,
            "data": {},
            "error_code": None
        }

        match action:
            # Show instructions/possible moves
            case "game_help":
                result["data"] = {
                    "available_actions": [
                        "move", "plant", "water", "till", "pickup_tool", "pickup_seed", "fill_water", "restart", "game_help"
                    ]
                }

            # Reset the game to the default game state
            case "restart":
                self.game_state = restart_game()
                result["is_changed"] = True

            # Move the character by x,y tiles
            case "move":
                direction = slots.get("direction") # right, left, up, down
                num_tiles = slots.get("num_tiles", 1)

                new_x, new_y = x_position, y_position
                if direction == "right": new_x += num_tiles
                elif direction == "left": new_x -= num_tiles
                elif direction == "up": new_y += num_tiles
                elif direction == "down": new_y -= num_tiles

                if not (0 <= new_x <= MAX_X and 0 <= new_y <= MAX_Y):
                    result.update({"success": False, "error_code": "out_of_bounds", "data": {"direction": direction, "num_tiles": num_tiles}})
                else:
                    self.game_state["position"]["x"] = new_x
                    self.game_state["position"]["y"] = new_y
                    result.update({"is_changed": True, "data": {"pos": (new_x, new_y), "direction": direction, "num_tiles": num_tiles}})

            # Plant a seed at the current tile
            case "plant":
                seed = slots.get("seed")
                seed_enum = PlantType[seed.upper()]

                if current_tile["type"] not in [TileType.TILLED, TileType.WATERED]:
                    result.update({"success": False, "error_code": "soil_not_ready"})
                elif current_tile["plant"]:
                    result.update({"success": False, "error_code": "tile_occupied"})
                elif seeds[seed_enum.value] <= 0:
                    result.update({"success": False, "error_code": "insufficient_seeds", "data": {"seed": seed_enum.value}})
                else:
                    current_tile["plant"] = seed_enum
                    seeds[seed_enum.value] -= PLANT_COST
                    result.update({"is_changed": True, "data": {"planted_seed": seed_enum.value, "remaining_seeds": seeds[seed_enum.value], "pos": (x_position, y_position)}})

            # Water the current tile
            case "water":
                if tool != ToolType.WATERING_CAN:
                    result.update({"success": False, "error_code": "wrong_tool", "data": {"required": "watering can"}})
                elif current_tile["type"] in [TileType.RESOURCE_STATION, TileType.TOOL_STATION]:
                    result.update({"success": False, "error_code": "invalid_tile_type"})
                elif current_tile["type"] == TileType.WATERED:
                    result.update({"success": False, "error_code": "tile_already_watered"})
                elif current_tile["type"] == TileType.GRASS:
                    result.update({"success": False, "error_code": "soil_not_ready", "data": {"pos": (x_position, y_position)}})
                elif current_tile["type"] == TileType.TILLED:
                    if water <= 0:
                        result.update({"success": False, "error_code": "insufficient_water"})
                    else:
                        current_tile["type"] = TileType.WATERED
                        self.game_state["inventory"]["consumables"]["water"] -= WATER_COST
                        result.update({"is_changed": True, "success": True, "data": {"pos": (x_position, y_position)}})
                    
            # Till the current tile
            case "till":
                if tool != ToolType.HOE:
                    result.update({"success": False, "error_code": "wrong_tool", "data": {"required": "hoe"}})
                elif current_tile["type"] in [TileType.RESOURCE_STATION, TileType.TOOL_STATION]:
                    result.update({"success": False, "error_code": "invalid_tile_type"})
                elif current_tile["type"] == TileType.WATERED:
                    result.update({"success": False, "error_code": "tile_already_watered"})
                elif current_tile["type"] == TileType.TILLED:
                    result.update({"success": False, "error_code": "already_tilled", "data": {"pos": (x_position, y_position)}})
                elif current_tile["type"] == TileType.GRASS:
                    current_tile["type"] = TileType.TILLED
                    result.update({"is_changed": True, "success": True, "data": {"pos": (x_position, y_position)}})

            # Pick up or swap tool
            case "pickup_tool":
                new_tool = slots.get("tool")
                tool_enum = ToolType[new_tool.upper().replace(" ", "_")]

                if x_position != STATION_X or y_position != TOOL_TILE_Y:
                    result.update({"success": False, "error_code": "wrong_location", "data": {"required": "tool station"}})
                elif tool == tool_enum:
                    result.update({"success": False, "error_code": "already_equipped", "data": {"tool": new_tool}})
                else:
                    self.game_state["inventory"]["tool"] = tool_enum
                    result.update({"is_changed": True, "success": True, "data": {"tool": new_tool}})

            # Pick up a seed
            case "pickup_seed":
                seed = slots.get("seed")
                seed_enum = PlantType[seed.upper()]

                if x_position != STATION_X or y_position != RESOURCE_TILE_Y:
                    result.update({"success": False, "error_code": "wrong_location", "data": {"required": "resource station"}})
                elif seeds[seed_enum.value] >= MAX_PLANT:
                    result.update({"success": False, "error_code": "maximum_seeds", "data": {"seed": seed_enum.value, "max": MAX_PLANT}})
                else:
                    seeds[seed_enum.value] = MAX_PLANT
                    result.update({"is_changed": True, "success": True, "data": {"seed": seed_enum.value, "max": MAX_PLANT}})

            # Fill watering can at resource station
            case "fill_water":
                if x_position != STATION_X or y_position != RESOURCE_TILE_Y:
                    result.update({"success": False, "error_code": "wrong_location", "data": {"required": "resource station"}})
                elif tool != ToolType.WATERING_CAN:
                    result.update({"success": False, "error_code": "wrong_tool", "data": {"required": "watering can"}})
                elif water >= MAX_WATER:
                    result.update({"success": False, "error_code": "maximum_water", "data": {"water": water, "max": MAX_WATER}})
                else:
                    self.game_state["inventory"]["consumables"]["water"] = MAX_WATER
                    result.update({"is_changed": True, "success": True, "data": {"water": MAX_WATER}})

        return result