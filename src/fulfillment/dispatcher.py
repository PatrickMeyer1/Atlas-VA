from src.fulfillment.garden_actions import GardenFulfillment
from src.intent_constants import BASIC_INTENTS, API_INTENTS, GARDEN_INTENTS

class FulfillmentDispatcher:
    def __init__(self):
        self.garden_fulfillment = GardenFulfillment()

    def dispatch(self, intent_dict):
        intent = intent_dict.get("intent")

        if intent in BASIC_INTENTS:
            return self.fulfill(intent_dict)
        elif intent in API_INTENTS:
            return self.fulfill(intent_dict)
        elif intent in GARDEN_INTENTS:
            return self.fulfill(intent_dict)