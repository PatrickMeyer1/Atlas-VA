# Used Gemini, feel free to change/add more

SYSTEM_PROMPTS = {
    "garden": """
    """,
    "api": """
    """,
    "basic": """
    """
}

BASIC_TEMPLATES = {

}

API_TEMPLATES = {

}

GARDEN_TEMPLATES = {
    "restart": {
        "success": [
            "The garden has been reset! You are back at the start and ready for a fresh beginning.",
            "Everything has been cleared. You're starting with a clean slate in the garden!"
        ],
    },
    "game_help": {
        "success": [
            "You can perform the following actions in the garden: {available_actions}. Which one would you like to do?",
            "I'm ready to help! Your available commands are: {available_actions}. Just let me know what you need."
        ],
    },
    "move": {
        "success": [
            "You've moved {num_tiles} tiles {direction} and are now at {pos}.",
            "You are heading {direction} for {num_tiles} spaces. Your current position is {pos}."
        ],
        "failure": {
            "out_of_bounds": [
                "You can't go that far {direction}; the edge of the garden has been reached.",
                "Moving {direction} that much would put you outside the garden fence!"
            ],
            "missing_direction": [
                "You didn't specify a direction. Would you like to move up, down, left, or right?",
                "I'm not sure where to go because you haven't given me a direction yet."
            ],
            "invalid_direction": [
                "You've chosen to move {direction}, but that isn't a valid option. Please choose from: {valid_options}.",
                "I can't move {direction}. Your valid choices for direction are {valid_options}."
            ]
        }
    },
    "plant": {
        "success": [
            "You've planted the {planted_seed} at {pos}. You have {remaining_seeds} left.",
            "The {planted_seed} seeds are now in the ground at {pos}."
        ],
        "failure": {
            "soil_not_ready": [
                "You can't plant here yet. The soil at {pos} needs to be tilled first.",
                "This spot isn't ready for seeds. Try tilling the grass first."
            ],
            "tile_occupied": [
                "There is already something growing here at {pos}!",
                "You can't plant that there; this tile is already occupied."
            ],
            "insufficient_seeds": [
                "You don't have any {seed} seeds left! Head to the resource station.",
                "The bag is empty of {seed} seeds. A restock is needed."
            ],
            "missing_seed": [
                "You haven't mentioned what you want to plant. Which seeds should I use?",
                "I need to know which plant you are referring to before I can start digging."
            ],
            "invalid_seed": [
                "You've asked for {provided}, but that seed isn't in your collection. You can plant: {valid_options}.",
                "The {provided} seeds aren't available for planting. Please choose from {valid_options}."
            ]
        }
    },
    "water": {
        "success": [
            "You've watered the tile at {pos}. The soil looks much better.",
            "Soil at {pos} is now hydrated and ready for growth."
        ],
        "failure": {
            "wrong_tool": [
                "You need to be holding the {required} to water the ground.",
                "Watering can't happen without the {required}. Go grab it."
            ],
            "tile_already_watered": [
                "This spot is already nice and damp.",
                "No need to water here; the tile at {pos} is already watered."
            ],
            "insufficient_water": [
                "The watering can is empty! A refill is needed at the resource station.",
                "You are out of water. Head back to the station to fill up."
            ],
            "soil_not_ready": [
                "You can't water plain grass. It needs to be tilled first.",
                "There's no point watering untilled ground. Let's till it first."
            ],
            "invalid_tile_type": [
                "Only dirt tiles can be watered, not the stations!",
                "That's a station tile; watering it won't help the plants."
            ]
        }
    },
    "till": {
        "success": [
            "You've tilled the earth at {pos}. It's ready for some seeds!",
            "The ground at {pos} is now plowed and ready for planting."
        ],
        "failure": {
            "wrong_tool": [
                "The {required} is needed before the soil can be tilled.",
                "The ground can't be broken up without the {required}."
            ],
            "already_tilled": [
                "This spot is already tilled and ready to go.",
                "The tile at {pos} has already been prepared."
            ],
            "tile_already_watered": [
                "This tile is already watered; tilling it now would be too messy!",
                "You can't till a tile that's already been watered."
            ],
            "invalid_tile_type": [
                "The floor of the station can't be tilled!",
                "This isn't a dirt tile. Only the grass can be tilled."
            ]
        }
    },
    "pickup_tool": {
        "success": [
            "You've equipped the {tool}. What should be done first?",
            "You are now holding the {tool}. Ready to get to work!"
        ],
        "failure": {
            "wrong_location": [
                "You need to be at the {required} to change tools.",
                "You aren't at the {required} yet. Move there first."
            ],
            "already_equipped": [
                "You are already holding the {tool}!",
                "The {tool} is already equipped."
            ],
            "missing_tool": [
                "You didn't specify which tool you want to grab from the station.",
                "I'm ready to swap gear, but you need to tell me which tool you'd like to hold."
            ],
            "invalid_tool": [
                "You've asked for the {provided}, but the only tools available are: {valid_options}.",
                "The {provided} isn't in the tool shed. You can pick up the {valid_options}."
            ]
        }
    },
    "pickup_seed": {
        "success": [
            "The bag has been restocked with {seed} seeds. You're at the max capacity of {max}!",
            "A fresh pack of {seed} seeds has been grabbed. You have {max} ready to plant."
        ],
        "failure": {
            "wrong_location": [
                "Seeds can only be picked up at the {required}.",
                "You need to be at the {required} to restock the seeds."
            ],
            "maximum_seeds": [
                "The bag is already full of {seed} seeds!",
                "You already have {max} {seed} seeds. No more can be carried."
            ],
            "missing_seed": [
                "You didn't say which seeds you want to pick up from the station.",
                "I need to know which variety of seeds you want to add to your bag."
            ],
            "invalid_seed": [
                "You've requested {provided}, but the resource station only stocks: {valid_options}.",
                "The station doesn't have {provided}. You can pick up {valid_options}."
            ]
        }
    },
    "fill_water": {
        "success": [
            "The watering can has been refilled. It's back up to {water} units.",
            "The watering can is full! Ready to hydrate the garden."
        ],
        "failure": {
            "wrong_location": [
                "Refilling can only happen at the {required}.",
                "Move to the {required} to get more water."
            ],
            "wrong_tool": [
                "The {required} must be held before it can be filled up!",
                "You aren't carrying the {required}. Equip it first."
            ],
            "maximum_water": [
                "The watering can is already full at {max} units.",
                "No need for a refill; the {max} unit limit has already been reached."
            ]
        }
    }
}