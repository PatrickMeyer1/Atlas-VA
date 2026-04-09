# Function to create the 2d grid array
from .garden_constants import TileType, RESOURCE_TILE_Y, TOOL_TILE_Y, STATION_X

def create_grid(width=12, height=6):
    grid = []

    for _ in range(height):
        row = []
        for _ in range(width):
            tile = {
                "type": TileType.GRASS, # grass, tilled, watered, stations
                "plant": None # carrot, lettuce, tomato
            }
            row.append(tile)
        grid.append(row)

    # Overwrite station tiles
    grid[RESOURCE_TILE_Y][STATION_X]["type"] = TileType.RESOURCE_STATION
    grid[TOOL_TILE_Y][STATION_X]["type"] = TileType.TOOL_STATION

    return grid

# Initializes the default game state. Will be called for game restarts
def restart_game():
    return {
        "inventory": {
            "tool": None,
            "consumables": {
                "seeds": {
                    "carrot": 0,
                    "lettuce": 0,
                    "tomato": 0,
                },
                "water": 0
            }
        },
        "position": {
            "x": 0,
            "y": 0
        },
        "grid": create_grid()
    }