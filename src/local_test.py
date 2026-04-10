import random
from src.nlu.intent_detection.inference import VoiceAssistantNLU
from src.generation.answer_generator import AnswerGenerator
from src.fulfillment.dispatcher import FulfillmentDispatcher

def test():
    nlu = VoiceAssistantNLU()
    fulfillment = FulfillmentDispatcher()
    generator = AnswerGenerator()
    
    print("\n--- NLU Integration Test Mode ---")
    print("Type a command (or 'exit' to stop):")

    while True:
        text = input("\nUser > ")
        if text.lower() in ['exit', 'quit']:
            break
            
        intent_result = nlu.process_utterance(text)

        raw_data = fulfillment.dispatch(intent_result)

        use_llm = random.choice([True, False])
        response = generator.generate_answer(raw_data, use_llm=use_llm)

        print(f"Atlas > (Using { 'LLM' if use_llm else 'Template-based' }): {response}")

        print(f"[DEBUG] Intent: {intent_result['intent']} | Slots: {intent_result.get('slots', {})}")
        print(f"[DEBUG] Fulfillment Data: {raw_data}")

if __name__ == "__main__":
    test()