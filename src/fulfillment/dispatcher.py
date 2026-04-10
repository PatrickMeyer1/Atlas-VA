from src.fulfillment.garden_actions import GardenFulfillment
from src.fulfillment.basic_actions import BasicFulfillment
from src.fulfillment.api_actions import APIFulfillment
from src.intent_constants import BASIC_INTENTS, API_INTENTS, GARDEN_INTENTS

class FulfillmentDispatcher:
    def __init__(self):
        self.garden_fulfillment = GardenFulfillment()
        self.basic_fulfillment = BasicFulfillment()
        self.api_fulfillment = APIFulfillment()

    def dispatch(self, intent_dict):
        intent = intent_dict.get("intent")

        if intent in BASIC_INTENTS:
            return self.basic_fulfillment.fulfill(intent_dict)
        elif intent in API_INTENTS:
            return self.api_fulfillment.fulfill(intent_dict)
        elif intent in GARDEN_INTENTS:
            return self.garden_fulfillment.fulfill(intent_dict)