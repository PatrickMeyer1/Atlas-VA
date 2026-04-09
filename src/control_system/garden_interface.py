from .engine import GardenEngine
from .renderer import Renderer

# VA will instantiate the GardenController class. THis keeps the control system abstract for the VA
class GardenController:
    def __init__(self):
        # VA creates this once to keep the game's state alive
        self.engine = GardenEngine()
        self.renderer = Renderer()

    def handle_voice_intent(self, intent_dict):
        message, success, is_changed = self.engine.fulfill_intent(intent_dict)

        image_path = None
        # Only draw if necessary
        if is_changed:
            image_path = self.renderer.draw_garden(self.engine.game_state)

        return {"tts_message": message, "success": success, "image_path": image_path}