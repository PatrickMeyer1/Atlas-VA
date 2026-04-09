from .constants import (
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

        message = ""
        status = True
        is_changed = False

        match action:
            # Show instructions/possible moves
            case "help":
                message = (
                    "Available actions:\n"
                    "- move: Move the player. Slots: direction ('up','down','left','right'), num_tiles (optional, default=1)\n"
                    "- plant: Plant a seed. Slots: seed ('carrot','lettuce','tomato')\n"
                    "- water: Water the current tile. No slots required\n"
                    "- till: Till the current tile. No slots required\n"
                    "- pickup_tool: Pick up or swap a tool.Slots: tool ('watering_can','hoe')\n"
                    "- pick_up_seed: Pick up seeds at the Resource Station. Slots: seed ('carrot','lettuce','tomato')\n"
                    "- fill_water: Refill watering can at Resource Station. No slots required\n"
                    "- restart: Reset the game to initial state. No slots required\n"
                    "- help: Show this instructions message"
                )

            # Reset the game to the default game state
            case "restart":
                self.game_state = restart_game()
                message = "Game restarted."
                is_changed = True

            # Move the character by x,y tiles
            case "move":
                direction = slots.get("direction") # right, left, up, down
                num_tiles = slots.get("num_tiles", 1) # Will be set to 1 before fulfillment if no num of tiles provided by user

                if direction == "right":
                    if x_position + num_tiles > MAX_X:
                        message = f"You cannot move by {num_tiles} to the right. It is out of bounds."
                        status = False
                    else:
                        self.game_state["position"]["x"] = x_position + num_tiles
                        message = f"You moved {num_tiles} tiles to the right and are now at ({self.game_state['position']['x']}, {y_position})."
                        is_changed = True
                elif direction == "left":
                    if x_position - num_tiles < 0:
                        message = f"You cannot move {num_tiles} to the left. It is out of bounds."
                        status = False
                    else:
                        self.game_state["position"]["x"] = x_position - num_tiles
                        message = f"You moved {num_tiles} tiles to the left and are now at ({self.game_state['position']['x']}, {y_position})."
                        is_changed = True
                elif direction == "up":
                    if y_position + num_tiles > MAX_Y:
                        message = f"You cannot move {num_tiles} up. It is out of bounds."
                        status = False
                    else:
                        self.game_state["position"]["y"] = y_position + num_tiles
                        message = f"You moved {num_tiles} tiles upwards and are now at ({x_position}, {self.game_state['position']['y']})."
                        is_changed = True
                elif direction == "down":
                    if y_position - num_tiles < 0:
                        message = f"You cannot move {num_tiles} down. It is out of bounds."
                        status = False
                    else:
                        self.game_state["position"]["y"] = y_position - num_tiles
                        message = f"You moved {num_tiles} tiles downwards and are now at ({x_position}, {self.game_state['position']['y']})."
                        is_changed = True

            # Plant a seed at the current tile
            case "plant":
                seed = slots.get("seed")
                seed_enum = PlantType[seed.upper()]

                if current_tile["type"] not in [TileType.TILLED, TileType.WATERED]:
                    message = "You can only plant seeds in tilled or watered tiles."
                    status = False
                elif current_tile["plant"]:
                    message = "You cannot plant seeds on a tile that is already occupied by a plant."
                    status = False
                elif seeds[seed_enum.value] <= 0:
                    message = f"You have an insufficient amount of {seed_enum.value} seeds. Needed = 1, Have = {seeds[seed_enum.value]}."
                    status = False
                else:
                    current_tile["plant"] = seed_enum
                    seeds[seed_enum.value] -= PLANT_COST
                    message = f"You have planted a {seed_enum.value} seed at tile position ({x_position}, {y_position})."
                    is_changed = True

            # Water the current tile
            case "water":
                if tool != ToolType.WATERING_CAN:
                    message = "You must equip the watering can tool to water the ground."
                    status = False
                elif current_tile["type"] in [TileType.RESOURCE_STATION, TileType.TOOL_STATION]:
                    message = "You can only water dirt tiles."
                    status = False
                elif current_tile["type"] == TileType.WATERED:
                    message = "You cannot water the tile more than once."
                    status = False
                elif current_tile["type"] == TileType.GRASS:
                    message = "You cannot water an untilled tile."
                    status = False
                elif current_tile["type"] == TileType.TILLED:
                    if water <= 0:
                        message = f"You have an insufficient amount of water. Needed = 1, Have = {water}."
                        status = False
                    else:
                        current_tile["type"] = TileType.WATERED
                        self.game_state["inventory"]["consumables"]["water"] -= WATER_COST
                        message = f"You have watered the tile at position ({x_position}, {y_position})."
                        is_changed = True
                    
            # Till the current tile
            case "till":
                if tool != ToolType.HOE:
                    message = "You must equip the hoe tool to till the ground."
                    status = False
                elif current_tile["type"] in [TileType.RESOURCE_STATION, TileType.TOOL_STATION]:
                    message = "You can only till grass tiles."
                    status = False
                elif current_tile["type"] == TileType.WATERED:
                    message = "You cannot till a watered tile."
                    status = False
                elif current_tile["type"] == TileType.TILLED:
                    message = "You cannot till an already tilled tile."
                    status = False
                elif current_tile["type"] == TileType.GRASS:
                    current_tile["type"] = TileType.TILLED
                    message = f"You have tilled the tile at position ({x_position}, {y_position})."
                    is_changed = True

            # Pick up or swap tool
            case "pickup_tool":
                new_tool = slots.get("tool")
                tool_enum = ToolType[new_tool.upper().replace(" ", "_")]

                if x_position != STATION_X or y_position != TOOL_TILE_Y:
                    message = "You must be located at the tool station to pick up a tool."
                    status = False
                elif tool == tool_enum:
                    message = f"You already have the {tool_enum.value} equipped."
                    status = False
                else:
                    self.game_state["inventory"]["tool"] = tool_enum
                    message = f"You have equipped the {tool_enum.value} tool."
                    is_changed = True

            # Pick up a seed
            case "pick_up_seed":
                seed = slots.get("seed")
                seed_enum = PlantType[seed.upper()]

                if x_position != STATION_X or y_position != RESOURCE_TILE_Y:
                    message = "You must be located at the resource station to pick up a seed."
                    status = False
                elif seeds[seed_enum.value] >= MAX_PLANT:
                    message = f"You already have the maximum amount of {seed_enum.value} seeds."
                    status = False
                else:
                    seeds[seed_enum.value] = MAX_PLANT
                    message = f"You have refilled your bag with {seed_enum.value} seeds."
                    is_changed = True

            # Fill watering can at resource station
            case "fill_water":
                if x_position != STATION_X or y_position != RESOURCE_TILE_Y:
                    message = "You must be located at the resource station to fill water."
                    status = False
                elif tool != ToolType.WATERING_CAN:
                    message = "You must equip the watering can tool to fill water."
                    status = False
                elif water >= MAX_WATER:
                    message = f"Your watering can is already full ({MAX_WATER})."
                    status = False
                else:
                    self.game_state["inventory"]["consumables"]["water"] = MAX_WATER
                    message = f"You have refilled your watering can to full ({MAX_WATER})"
                    is_changed = True

        return message, status, is_changed