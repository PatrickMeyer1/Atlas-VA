## **Basic Intents**

1. **Out-Of-Scope** (no slots)
    - **Definition**: Intents which are out of scope of the assistant.
2. **Greetings** (no slots)
    - **Definition**: Allows the assistant to recognize when the user greets it.
3. **Goodbye** (no slots)
    - **Definition**: Allows the assistant to recognize when the user says goodbye.
4. **Timer** (Duration slot, TimerName slot)
    - **Definition:** Allows the user to set a timer.
    - **Slot 1: Duration.** Specifies how long the timer should last.
        - Required.
    - **Slot 2: TimerName.** Specifies the name of the timer.
        - Optional with default name `timer`.
5. **Weather** (City slot, Country slot)
    - **Definition:** Allows the user to get the weather of a particular city.
    - **Slot 1: City.** Specifies the city of interest.
        - Optional with default `Ottawa`
    - **Slot 2: Country.** Specifies the country of interest.
        - Optional with default `None` (it uses the first result returned by `GeoCoding`)

## **Specialized Domain Intents**

1. **GetPlantSunlight** (PlantName slot)
    - **Definition:** Allows the user to to get sunlight information for a specific plant.
    - **Slot 1: PlantName.** Specifies the common or scientific plant name to retrieve information for.
        - Required.
2. **GetPlantWateringCare** (PlantName slot)
    - **Definition:** Allows the user to to get watering care information for a specific plant.
    - **Slot 1: PlantName.** Specifies the common or scientific plant name to retrieve information for.
        - Required.
3. **GetPlantCycle** (PlantName slot)
    - **Definition:** Allows the user to get the cycle information for a specific plant (ex: `Perennial`).
    - **Slot 1: PlantName.** Specifies the common or scientific plant name to retrieve information for.
        - Required.
4. **GetPlantEdibility** (PlantName slot)
    - **Definition:** Allows the user to find out whether or not a specific plant is edible.
    - **Slot 1: PlantName.** Specifies the common or scientific plant name to retrieve information for.
        - Required.
5. **SearchPlantsByEnvironment** (Environment slot, Quantity slot)
    - **Definition:** Allows the user to get a list of plants that grow in a specific enviornment.
    - **Slot 1: Environment.** Specifies whether the plants should be suitable for indoor or outdoor environments.
        - Required.
        - **Expected Values:** `indoor` or `outdoor`
    - **Slot 2: Quantity.** Specifies the desired number of results.
        - Optional with default `3`.

## **Control System Intents**

1. **Restart** (No slots)
    - **Definition:** Allows the user to reset the game state.
2. **Move** (Direction slot, NumTiles slot)
    - **Definition:** Allows the user to move the character.
    - **Slot 1: Direction.** Specifies the direction of movement.
        - Required.
        - **Expected Values:** `left`, `right`, `up`, `down`.
    - **Slot 2: NumTiles.** Specifies the number of tiles to move.
        - Optional with default `1`.
3. **Plant** (Seed slot)
    - **Definition:** Allows the user to plant a seed.
    - **Slot 1: Seed.** Specifies which type of seed to plant.
        - Required.
        - **Expected Values:** `carrot`, `lettuce`, `tomato`
4. **Water** (No slots)
    - **Definition:** Allows the user to water the current tile.
5. **Till** (No slots)
    - **Definition:** Allows the user to till the current tile.
6. **PickUpTool** (Tool slot)
    - **Definition:** Allows the user to pick up or swap a tool.
    - **Slot 1: Tool.** Specifies the tool to pick up.
        - Required.
        - **Expected Values:** `watering can`, `hoe`
7. **PickUpSeed** (Seed slot)
    - **Definition:** Allows the user to pick up seeds at the Resource Station.
    - **Slot 1: Seed.** Specifies the type of seed to pick up.
        - Required.
        - **Expected Values:** `carrot`, `lettuce`, `tomato`
8. **FillWater** (No slots)
    - **Definition:** Allows the user to fill their watering can at the Resource Station.
9. **GameHelp** (No slots)
    - **Definition:** Allows the user to receive instructions regarding how to interact with the control system.
