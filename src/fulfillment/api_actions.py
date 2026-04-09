

class APIFulfillment:
    def __init__(self):
        #self.api_controller = APIController()
        pass

    def fulfill(self, intent_dict):
        intent = intent_dict["intent"]
        slots = intent_dict.get("slots", {})

        match intent:
            case "get_plant_sunlight":
                pass
            case "get_plant_watering_care":
                pass
            case "get_plant_cycle":
                pass
            case "get_plant_edibility":
                pass
            case "search_plants_by_environment":
                pass