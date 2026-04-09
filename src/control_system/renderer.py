import time
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from .garden_constants import (
    TILE_COLORS, TOOL_COLORS, PLANT_COLORS, 
    Color, TileType, ToolType, PlantType, 
    STATION_X, RESOURCE_TILE_Y, TOOL_TILE_Y
)

class Renderer:
    def draw_garden(self, state):
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_xlim(0,12)
        ax.set_ylim(0,6)
        ax.set_xticks([])
        ax.set_yticks([])

        # Add inventory text
        inventory_text = (
            f"Carrot seeds: {state['inventory']['consumables']['seeds']['carrot']} | "
            f"Lettuce seeds: {state['inventory']['consumables']['seeds']['lettuce']} | "
            f"Tomato seeds: {state['inventory']['consumables']['seeds']['tomato']} | "
            f"Water: {state['inventory']['consumables']['water']} | "
            f"Tool: {state['inventory']['tool'].value.capitalize() if state['inventory']['tool'] else 'None'}"
        )

        ax.text(6, -0.25, inventory_text, ha="center", va="bottom")
        
        # Add station text

        ax.text(
            x=STATION_X - 0.3,
            y=RESOURCE_TILE_Y + 0.5,
            s="Resource\n Station",
            fontsize=10,
            ha='right',
            va='center'
        )

        ax.text(
            x=STATION_X - 0.3,
            y=TOOL_TILE_Y + 0.5,
            s="Tool\n Station",
            fontsize=10,
            ha='right',
            va='center'
        )

        # Loop through grid, setting each tile to its correct type and adding plants if present
        # We could obviously keep an array of tiles that changed, but 72 elems won't matter at O(m*n)
        for y in range(len(state["grid"])):
            for x in range(len(state["grid"][y])):
                tile = state["grid"][y][x]
                x_position = state["position"]["x"]
                y_position = state["position"]["y"]

                # Types
                color = TILE_COLORS[tile["type"]]
                ax.add_patch(Rectangle((x, y), 1, 1, facecolor=color))

                # Special Types
                if tile["type"] == TileType.TOOL_STATION: # No tool == display both
                    if not state["inventory"]["tool"]:
                        ax.add_patch(Circle((x + 0.25, y + 0.5), 0.15, facecolor=TOOL_COLORS[ToolType.HOE], edgecolor='black', linewidth=0.75))
                        ax.add_patch(Circle((x + 0.75, y + 0.5), 0.15, facecolor=TOOL_COLORS[ToolType.WATERING_CAN], edgecolor='black', linewidth=0.75))
                    elif state["inventory"]["tool"] == ToolType.HOE: # Holding hoe == display watering can
                        ax.add_patch(Circle((x + 0.5, y + 0.5), 0.15, facecolor=TOOL_COLORS[ToolType.WATERING_CAN], edgecolor='black', linewidth=0.75))
                    elif state["inventory"]["tool"] == ToolType.WATERING_CAN: # Holding watering can == display hoe
                        ax.add_patch(Circle((x + 0.5, y + 0.5), 0.15, facecolor=TOOL_COLORS[ToolType.HOE], edgecolor='black', linewidth=0.75))

                if tile["type"] == TileType.RESOURCE_STATION: # Display consumables
                    ax.add_patch(Circle((x + 0.25, y + 0.25), 0.15, facecolor=PLANT_COLORS[PlantType.CARROT], edgecolor='black', linewidth=0.75))
                    ax.add_patch(Circle((x + 0.75, y + 0.25), 0.15, facecolor=PLANT_COLORS[PlantType.TOMATO], edgecolor='black', linewidth=0.75))
                    ax.add_patch(Circle((x + 0.25, y + 0.75), 0.15, facecolor=PLANT_COLORS[PlantType.LETTUCE], edgecolor='black', linewidth=0.75))
                    ax.add_patch(Circle((x + 0.75, y + 0.75), 0.15, facecolor='blue', edgecolor='black', linewidth=0.75)) # Could make PlantType -> Consumable and add water to it

                # Plants
                if tile["plant"]:
                    ax.add_patch(Circle((x + 0.5, y + 0.5), 0.15, facecolor=PLANT_COLORS[tile["plant"]], edgecolor='black', linewidth=0.75))

                # Tools
                if state["inventory"]["tool"]:
                    ax.add_patch(Circle((x_position + 0.55, y_position + 0.2), 0.1, facecolor=TOOL_COLORS[state["inventory"]["tool"]], edgecolor='black', linewidth=0.5))

                # Position
                ax.add_patch(Circle((x_position + 0.25, y_position + 0.25), 0.175, facecolor=Color.PLAYER.value)) # could make it a square to better differentiate

        # Draw vertical lines
        ax.vlines(x=range(1, 12), ymin=0, ymax=6, color='black')

        # Draw horizontal lines
        ax.hlines(y=range(0,6), xmin=0, xmax=12, color='black')


        base_dir = Path(__file__).parent
        plot_dir = base_dir / "plots"

        # Saves new plot
        filename = plot_dir / f"output_plot_{int(time.time() * 1000)}.png"

        # Removes old
        for old_plot in plot_dir.glob("output_plot_*.png"):
            old_plot.unlink()

        plt.savefig(filename)
        plt.close(fig)
        
        return str(filename)

