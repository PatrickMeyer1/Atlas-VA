


class BasicFulfillment:
    def __init__(self):
        pass

    def fulfill(self, intent_dict):
        intent = intent_dict["intent"]
        slots = intent_dict.get("slots", {})

        match intent:
            case "oos":
                pass
            case "greetings":
                pass
            case "goodbye":
                pass
            case "timer":
                pass
            case "weather":
                pass