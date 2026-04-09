from enum import Enum

# Enums, constants and helper dicts. This should make it easier and less verbose when writing logic

class TileType(Enum):
    GRASS = "grass"
    TILLED = "tilled"
    WATERED = "watered"
    RESOURCE_STATION = "resource_station"
    TOOL_STATION = "tool_station"

class PlantType(Enum):
    CARROT = "carrot"
    LETTUCE = "lettuce"
    TOMATO = "tomato"

class ToolType(Enum):
    HOE = "hoe"
    WATERING_CAN = "watering can"

# https://matplotlib.org/stable/gallery/color/named_colors.html
class Color(Enum):
    # Tiles
    GRASS = "forestgreen"
    TILLED = "burlywood"
    WATERED = "saddlebrown"
    STATION = "grey"
    # Plants
    CARROT = "orange"
    LETTUCE = "lightgreen"
    TOMATO = "red"
    # Player
    PLAYER = "black"
    # Tools
    WATERING_CAN = "blue"
    HOE = "purple"
    
PLANT_COLORS = {
    PlantType.CARROT: Color.CARROT.value,
    PlantType.LETTUCE: Color.LETTUCE.value,
    PlantType.TOMATO: Color.TOMATO.value
}

TILE_COLORS = {
    TileType.GRASS: Color.GRASS.value,
    TileType.TILLED: Color.TILLED.value,
    TileType.WATERED: Color.WATERED.value,
    TileType.RESOURCE_STATION: Color.STATION.value,
    TileType.TOOL_STATION: Color.STATION.value
}

TOOL_COLORS = {
    ToolType.HOE: Color.HOE.value,
    ToolType.WATERING_CAN: Color.WATERING_CAN.value
}

RESOURCE_TILE_Y = 4
TOOL_TILE_Y = 3
STATION_X = 0

MAX_WATER = 10
WATER_COST = 1

MAX_PLANT = 5
PLANT_COST = 1

MAX_X = 11
MAX_Y = 5