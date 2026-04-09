import random
from transformers import GenerationConfig, pipeline
import torch
from collections import defaultdict

from src.intent_constants import BASIC_INTENTS, API_INTENTS, GARDEN_INTENTS
from src.generation.answer_templates import BASIC_TEMPLATES, API_TEMPLATES, GARDEN_TEMPLATES, SYSTEM_PROMPTS

class AnswerGenerator:
    def __init__(self, model_name="meta-llama/Llama-3.2-1B-Instruct"): # We could pass device in since it's also used in inference.py or pass the model from the main pipeline
        self.model = pipeline("text-generation", model=model_name, dtype="auto", device_map=torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")))

    def format_response(self, items):
        if not items:
            return ""
        elif len(items) == 1:
            return str(items[0])
        else:
            return ", ".join(map(str, items[:-1])) + " and " + str(items[-1])

    def generate_answer(self, raw_data, use_llm=False):
        if use_llm:
            return self._generate_with_llm(raw_data)
        
        intent = raw_data.get("intent")
        if intent in BASIC_INTENTS:
            return self._generate_basic_answer(raw_data)
        elif intent in API_INTENTS:
            return self._generate_api_answer(raw_data)
        elif intent in GARDEN_INTENTS:
            return self._generate_garden_answer(raw_data)

    def _generate_with_llm(self, raw_data):
        base_persona = (
            "You are Atlas, a friendly and concise voice assistant. "
            "Use the 'Fulfillment Data' to give a short update in 1-2 sentences. "
            "Refer to the user as 'you'. Never mention JSON or technical error codes.\n\n"
        )

        intent = raw_data.get("intent")

        if intent in GARDEN_INTENTS:
            category = "garden"
        elif intent in API_INTENTS:
            category = "api"
        else:
            category = "basic"

        system_prompt = base_persona + SYSTEM_PROMPTS[category] + "\n\nRespond to this query:"

        # Only important data
        display_data = {
            "INTENT": raw_data.get("intent"),
            "RESULT": "COMMAND_SUCCESSFUL" if raw_data.get("success") else "COMMAND_FAILED_ERROR",
            "ERROR_TYPE": raw_data.get("error_code"),
            **raw_data.get("data", {}) # flatten it out
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": {str(display_data)}}
        ]

        config = GenerationConfig(
            max_length=None,
            max_new_tokens=64,
            do_sample=True,
            temperature=0.4,
            pad_token_id=self.model.tokenizer.eos_token_id
        )

        outputs = self.model(
            messages,
            generation_config=config
        )

        return outputs[0]["generated_text"][-1]["content"].strip()

    def _generate_basic_answer(self, raw_data):
        pass

    def _generate_api_answer(self, raw_data):
        pass

    def _generate_garden_answer(self, raw_data):
        intent = raw_data.get("intent")
        success = raw_data.get("success", False)
        templates_for_intent = GARDEN_TEMPLATES.get(intent, ["Action completed successfully."])

        if success:
            templates = templates_for_intent.get("success")
        else: # Pick based on error code
            error_code = raw_data.get("error_code", "generic_error")
            failure_templates = templates_for_intent.get("failure", {})
            templates = failure_templates.get(error_code, ["I encountered an issue in the garden."])

        template = random.choice(templates)

        details = defaultdict(lambda: "[missing info]", raw_data.get("data", {})) # prevents crashing if slot is wrongly predicted or missing

        for key, value in list(details.items()):
            if isinstance(value, list):
                details[key] = self.format_response(value)

        return template.format_map(details)