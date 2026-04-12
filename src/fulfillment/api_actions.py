import requests
import os
import random
import re
from text_to_num import text2num
from difflib import SequenceMatcher

from src.fulfillment.constants import PLANT_ENVIRONMENT_MAPPING, NL_MAPPING

class APIFulfillment:
    def __init__(self):
        self.key = os.getenv("PERENUAL_KEY")
        self.BASE_URL = "https://perenual.com/api/"
        self.SPECIES_LIST = "v2/species-list/"
        self.SPECIES_DETAILS = "v2/species/details/"

        self.PLANT_ENVIRONMENT_MAPPING = PLANT_ENVIRONMENT_MAPPING
        self.NL_MAPPING = NL_MAPPING

    # Normalize the plant name so both user and api are talking about the same plant
    def _clean_plant_name(self, plant_name):
        cleaned = re.sub(r'[-_\'/]', ' ', str(plant_name)).lower()

        return " ".join(cleaned.split()) # remove whitespaces and return to string

    def _get_best_match(self, query_name, plant_list):
        best_match = None
        highest_score = 0.0
        THRESHOLD = 0.6

        for plant in plant_list:
            common_name = self._clean_plant_name(plant.get("common_name", ""))
            scientific_name = [self._clean_plant_name(p) for p in plant.get("scientific_name", [])] # array response

            # exact match (priority 1)
            if query_name == common_name or query_name in scientific_name:
                return plant.get("id")
            
            # substrings (priority 2)
            current_score = SequenceMatcher(None, query_name, common_name).ratio()

            if current_score > highest_score and current_score >= THRESHOLD:
                highest_score = current_score
                best_match = plant.get("id")
                
            print(f"{query_name}, {common_name}, {current_score}")
        
        return best_match
        
    def _get_api_data(self, endpoint, parameters=None):
        url = f"{self.BASE_URL}{endpoint}"
        params = {"key": self.key, **(parameters or {})}

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                return None

            return response.json()
        except Exception:
            return None
        
    def _get_species_details(self, plant_name):
        clean_name = self._clean_plant_name(plant_name)
        
        # blueberries, strawberries -> map to end singular with y
        if clean_name.endswith('ies'):
            singular_y = clean_name[:-3] + "y"
            search_res = self._get_api_data(self.SPECIES_LIST, {"q": singular_y})
        else:
            singular_s = clean_name.rstrip('s')
            search_res = self._get_api_data(self.SPECIES_LIST, {"q": singular_s})

        if not search_res or not search_res.get("data"):
            return None
        
        best_match_id = self._get_best_match(clean_name, search_res.get("data"))

        if not best_match_id:
            return None

        return self._get_api_data(f"{self.SPECIES_DETAILS}{best_match_id}")

    def fulfill(self, intent_dict):
        intent = intent_dict["intent"]
        slots = intent_dict.get("slots", {})
        plant_name_raw = slots.get("plantname", None) # This will passed in query

        details = None
        official_name = None

        # If its a get intent
        if intent in ["get_plant_sunlight", "get_plant_watering_care", "get_plant_cycle", "get_plant_edibility"]:
            if not plant_name_raw:
                return {"intent": intent, "success": False, "error_code": "missing_plantname_slot"}

            details = self._get_species_details(plant_name_raw)

            if not details:
                return {"intent": intent, "success": False, "error_code": "plant_not_found", "data": {"plantname": plant_name_raw}}
            
            official_name = details.get("common_name").title()

        match intent:
            case "get_plant_sunlight":
                raw_sun = details.get("sunlight", None)

                if not raw_sun:
                    return {"intent": intent, "success": False, "error_code": "no_sunlight_information"}
                                
                clean_sun = [self.NL_MAPPING["sunlight"].get(i.lower(), "") for i in raw_sun] # map to array

                return {"intent": intent, "success": True, "data": {"plant": official_name, "sunlight": clean_sun}}
            case "get_plant_watering_care":
                raw_water_care = details.get("watering", None)

                if not raw_water_care:
                    return {"intent": intent, "success": False, "error_code": "no_water_care_information", "data": {"plant": official_name}}
                
                raw_water_care = raw_water_care.lower()

                frequency = self.NL_MAPPING["watering"].get(raw_water_care, "")
                benchmark = details.get("watering_general_benchmark", None)
                
                if not benchmark or not benchmark.get("value") or not benchmark.get("unit"):
                    return {"intent": intent, "success": False, "error_code": "no_water_frequency_information", "data": {"plant": official_name}}
                
                value = str(benchmark.get("value")).replace('"', '')
                unit = benchmark.get("unit")
                
                return {"intent": intent, "success": True, "data": {"plant": official_name, "frequency": frequency, "value": value, "unit": unit}}
            case "get_plant_cycle":
                cycle = details.get("cycle", None)

                if not cycle:
                    return {"intent": intent, "success": False, "error_code": "no_cycle_information", "data": {"plant": official_name}}
                
                cycle = cycle.lower()

                return {"intent": intent, "success": True, "data": {"plant": official_name, "cycle": cycle}}
            case "get_plant_edibility":
                is_edible = details.get("edible_fruit") == 1 or details.get("edible_leaf") == 1

                is_edible = "edible" if is_edible == 1 else "inedible"

                return {"intent": intent, "success": True, "data": {"plant": official_name, "is_edible": is_edible}}
            case "search_plants_by_environment":
                environment = slots.get("environment", None)
                quantity = slots.get("quantity", 3)

                if not environment:
                    return {"intent": intent, "success": False, "error_code": "missing_environment_slot"}
                
                environment = environment.lower()
                
                # Maps to either inside/indoor or outside/outdoor
                is_indoor = None
                if environment in self.PLANT_ENVIRONMENT_MAPPING.get("indoor"):
                    is_indoor = 1
                elif environment in self.PLANT_ENVIRONMENT_MAPPING.get("outdoor"):
                    is_indoor = 0

                if is_indoor is None:
                    return {"intent": intent, "success": False, "error_code": "invalid_environment"}

                if isinstance(quantity, str):
                    try:
                        quantity = text2num(quantity, 'en')
                    except Exception:
                        return {"intent": intent, "success": False, "error_code": "quantity_parsing_error"}
                
                quantity = min(5, quantity) # max 5 plants

                # need to get initial list to know how many elems/pages there are. We need this to fetch a random page later on
                initial_list = self._get_api_data(self.SPECIES_LIST, {"indoor": is_indoor})

                if not initial_list or not initial_list.get("data"):
                    return {"intent": intent, "success": False, "error": "api_error"}
                
                last_page = initial_list.get("last_page", 1)
                
                random_page = random.randint(1, max(1, last_page - 1)) # don't consider last page (might not have enough plants)

                # Fetch that specific page
                random_list = self._get_api_data(self.SPECIES_LIST, {"indoor": is_indoor, "page": random_page})

                if not random_list or not random_list.get("data"):
                    data = initial_list.get("data") # fallback
                else:
                    data = random_list.get("data")

                all_names = [p.get("common_name").title() for p in data if p.get("common_name")]
                
                # get unique to prevent duplicates
                unique_names = list(set(all_names))

                # randmly sample
                plant_names = random.sample(unique_names, min(quantity, len(unique_names)))

                return {"intent" : intent, "success": True, "data": {"plants": plant_names, "environment": environment, "quantity": len(plant_names)}}