# Used Gemini, feel free to change/add more

SYSTEM_PROMPTS = {
    "garden": """
        For each of the following scenarios, generate a concise and friendly response that confirms the action taken or explains the reason for failure,
        without mentioning technical details or error codes. Use the provided data to personalize the response with relevant information such as direction,
        seed type, or position in the garden.

        - [Move Success] Data: {'INTENT': 'move', 'RESULT': 'COMMAND_SUCCESSFUL', 'direction': 'down', 'num_tiles': 2, 'pos': (0, 2)}
        Confirm the movement by stating the direction and number of tiles moved, and announce the coordinates. 

        - [Move Failure] Data: {'INTENT': 'move', 'RESULT': 'COMMAND_FAILED_ERROR', 'ERROR_TYPE': 'out_of_bounds', 'direction': 'left'}
        Politely explain that the movement failed because they have reached the edge of the garden boundary.

        - [Plant Success] Data: {'INTENT': 'plant', 'RESULT': 'COMMAND_SUCCESSFUL', 'planted_seed': 'tomato', 'remaining_seeds': 3, 'pos': (1, 1)}
        Celebrate the planting at the current location and remind them how many seeds of that type remain in their bag.

        - [Plant Failure] Data: {'INTENT': 'plant', 'RESULT': 'COMMAND_FAILED_ERROR', 'ERROR_TYPE': 'soil_not_ready'}
        Explain that seeds can't grow here yet because the soil needs to be tilled and prepared first.

        - [Water Success] Data: {'INTENT': 'water', 'RESULT': 'COMMAND_SUCCESSFUL', 'pos': (4, 2)}
        Confirm that the soil at their current position has been hydrated.

        - [Water Failure] Data: {'INTENT': 'water', 'RESULT': 'COMMAND_FAILED_ERROR', 'ERROR_TYPE': 'insufficient_water'}
        Alert the user that their watering can is empty and they need to visit the resource station for a refill.

        - [Till Success] Data: {'INTENT': 'till', 'RESULT': 'COMMAND_SUCCESSFUL', 'pos': (3, 3)}
        Confirm the ground is now plowed and ready for seeds at their location.

        - [Till Failure] Data: {'INTENT': 'till', 'RESULT': 'COMMAND_FAILED_ERROR', 'ERROR_TYPE': 'already_tilled'}
        Let the user know the soil here is already prepared and doesn't need further tilling.

        - [Tool Success] Data: {'INTENT': 'pickup_tool', 'RESULT': 'COMMAND_SUCCESSFUL', 'tool': 'hoe'}
        Confirm they have successfully equipped the new tool and are ready to use it.

        - [Tool Failure] Data: {'INTENT': 'pickup_tool', 'RESULT': 'COMMAND_FAILED_ERROR', 'ERROR_TYPE': 'wrong_location', 'required': 'tool station'}
        Remind the user that tools can only be swapped while standing at the tool station.

        - [Seed Success] Data: {'INTENT': 'pickup_seed', 'RESULT': 'COMMAND_SUCCESSFUL', 'seed': 'lettuce', 'max': 5}
        Confirm they have restocked their seeds to the maximum capacity.

        - [Seed Failure] Data: {'INTENT': 'pickup_seed', 'RESULT': 'COMMAND_FAILED_ERROR', 'ERROR_TYPE': 'maximum_seeds', 'seed': 'carrot'}
        Inform them that they are already carrying the maximum number of those seeds.

        - [Refill Success] Data: {'INTENT': 'fill_water', 'RESULT': 'COMMAND_SUCCESSFUL', 'water': 10}
        Announce that the watering can is now full and ready for use.

        - [Refill Failure] Data: {'INTENT': 'fill_water', 'RESULT': 'COMMAND_FAILED_ERROR', 'ERROR_TYPE': 'wrong_tool', 'required': 'watering can'}
        Explain that they need to be holding the watering can before they can refill it at the station.

        - [Restart Success] Data: {'INTENT': 'restart', 'RESULT': 'COMMAND_SUCCESSFUL'}
        Confirm the garden has been reset to its original state for a fresh start.

        - [Game Help] Data: {'INTENT': 'game_help', 'RESULT': 'COMMAND_SUCCESSFUL', 'available_actions': 'move, plant, water, till, pickup_tool, pickup_seed, fill_water, restart, help'}
        Summarize the available actions naturally, grouping them by movement, plant care, and resource gathering.
    """,
    "api": """
    """,
    "basic": """
        - [Greetings] Data: {'INTENT': 'greetings', 'RESULT': 'COMMAND_SUCCESSFUL', 'ERROR_TYPE': None}
        Provide a friendly greeting to the user, asking how you can assist them today.

        - [Goodbye] Data: {'INTENT': 'goodbye', 'RESULT': 'COMMAND_SUCCESSFUL', 'ERROR_TYPE': None}
        Provide a friendly farewell message, indicating that you are signing off but will be available for future assistance.

        - [OOS] Data: {'INTENT': 'oos', 'RESULT': 'COMMAND_SUCCESSFUL', 'ERROR_TYPE': None}:
        Provide a friendly response indicating that the requested action is outside of current capabilities, without mentioning technical limitations or error codes.

        - [Timer Success] Data: {'INTENT': 'timer', 'RESULT': 'COMMAND_SUCCESSFUL', 'duration': 10, 'unit': 'minutes', 'timername': 'pizza'}
        Confirm that a timer has been started, mentioning the specific name, duration, and unit provided.

        - [Timer Failure] Data: {'INTENT': 'timer', 'RESULT': 'COMMAND_FAILED_ERROR', 'ERROR_TYPE': 'missing_duration'}
        Politely ask the user how long they want the timer to last since they didn't provide a duration.

        - [Timer Failure] Data: {'INTENT': 'timer', 'RESULT': 'COMMAND_FAILED_ERROR', 'ERROR_TYPE': 'invalid_unit', 'unit': 'days'}
        Explain that you can only set timers for seconds, minutes, or hours, and that the unit they provided is not supported.

        - [Weather Success] Data: {'INTENT': 'weather', 'RESULT': 'COMMAND_SUCCESSFUL', 'city': 'Ottawa', 'country': 'Canada', 'weather_condition': 'clear sky', 'temperature': 22, 'temperature_unit': '°C', 'feels_like': 21, 'apparent_temperature_unit': '°C', 'humidity': 45, 'relative_humidity_unit': '%', 'wind_speed': 10, 'wind_speed_unit': 'km/h'}
        Confirm the current weather conditions for the specified city. Naturally include the temperature, how it feels, and relevant details like humidity or wind speed using their respective units.

        - [Weather Failure] Data: {'INTENT': 'weather', 'RESULT': 'COMMAND_FAILED_ERROR', 'ERROR_TYPE': 'missing_location'}
        Politely inform the user that you need a city name to look up the weather, as no location was provided in their request.

        - [Weather Failure] Data: {'INTENT': 'weather', 'RESULT': 'COMMAND_FAILED_ERROR', 'ERROR_TYPE': 'invalid_location', 'location': 'Atlantis'}
        Explain that you couldn't find any geographical data for the city provided and ask the user to double-check the name or try a different location.

        - [Weather Failure] Data: {'INTENT': 'weather', 'RESULT': 'COMMAND_FAILED_ERROR', 'ERROR_TYPE': 'api_error'}
        Apologize and let the user know that there is currently a problem connecting to the weather service, and suggest they try again in a few moments.
    """
}

BASIC_TEMPLATES = {
    "greetings": {
        "success": [
            "Hello! I'm Atlas. How can I help you today?",
            "Hi there!",
            "Greetings! What's on the agenda for today?"
        ]
    },
    "goodbye": {
        "success": [
            "Goodbye! I'll be here if you need more help.",
            "See you later! Have a great day!",
            "Bye for now! See you soon!"
        ]
    },
    "oos": {
        "success": [
            "I'm sorry, I can't do that yet.",
            "I'm not quite sure how to help with that. Should we focus on the something else?",
            "That's outside of my current expertise. Let's stick to something else for now."
        ]
    },
    "timer": {
        "success": [
            "The {timername} timer has been set for {duration} {unit}. I'll let you know when it's up!",
            "{timername} timer started for {duration} {unit}. I'll keep track of the time for you.",
            "I've set a {timername} timer for {duration} {unit}. I'll alert you when the time is up!"
        ],
        "failure": {
            "missing_duration": [
                "How long should I set the {timername} timer for?",
                "I need to know the duration for your {timername} timer. Try saying 'five minutes'."
            ],
            "invalid_duration_format": [
                "I didn't quite catch the time. Could you say that as a number and a unit, like 'ten minutes'?",
                "I'm having trouble with the time format. Try 'thirty seconds' or 'one hour'."
            ],
            "invalid_unit": [
                "I can only set timers in seconds, minutes, or hours. You asked for {unit}.",
                "Sorry, {unit} isn't a time unit I can track. Please use seconds, minutes, or hours."
            ],
            "invalid_duration": [
                "I couldn't understand that number. Could you try saying it again?",
                "I'm having trouble recognizing the number '{duration}'. Could you repeat it?"
            ]
        }
    },
    "weather": {
        "success": [
            "In {city}, {country} it's currently {weather_condition} at {temperature}{temperature_unit}. It feels like {feels_like}{apparent_temperature_unit} with {humidity}{relative_humidity_unit} humidity.",
            "The weather in {city}, {country} is {weather_condition}. The temperature is {temperature}{temperature_unit}, though it feels closer to {feels_like}{apparent_temperature_unit} due to the wind.",
            "Right now in {city}, {country} you'll find {weather_condition} conditions. It's {temperature}{temperature_unit} with a wind speed of {wind_speed} {wind_speed_unit}.",
            "It is {weather_condition} in {city}, {country}. The temperature is {temperature}{temperature_unit} with {precipitation} {precipitation_unit} of precipitation recorded.",
            "Currently in {city}, {country} it's {temperature}{temperature_unit} and {weather_condition}. With {humidity}{relative_humidity_unit} humidity, it feels like {feels_like}{apparent_temperature_unit} outside."
        ],
        "failure": {
            "invalid_location": [
                "The location you provided isn't valid. Please specify a valid city or area for the weather.",
                "I couldn't understand the location you gave. Please provide a valid city or area for the weather information.",
                "That doesn't seem like a valid location. Please tell me which city or area you'd like the weather for."
            ],
            "api_error": [
                "I'm having trouble fetching the weather right now for {city}, {country}. Please try again later.",
                "Sorry, I'm unable to get the weather information for {city}, {country} at the moment. Please check back later.",
                "There seems to be an issue with the weather service. I can't provide the weather for {city}, {country} right now, but please try again later."
            ]
        }
    }
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