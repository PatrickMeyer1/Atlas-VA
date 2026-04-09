from nlu.intent_detection.inference import VoiceAssistantNLU
from control_system.engine import GardenEngine
from controller import Controller

def manual_test():
    nlu = VoiceAssistantNLU()
    # engine = GardenEngine()
    coordinator = Controller()
    
    print("\n--- NLU Manual Test Mode ---")
    print("Type a command (or 'exit' to stop):")

    while True:
        text = input("\nUser > ")
        if text.lower() in ['exit', 'quit']:
            break
            
        result = nlu.process_utterance(text)

        # message, success, image (for control system) or just message, success (for other intents)
        message = coordinator.cleanup_and_dispatch(result)

        print(f"Atlas > status: {message['success']}, message: {message['tts_message']}")
        
        print("\n--- Debug Info (Intent detection) ---")
        print(f"Intent : {result['intent']}")
        print(f"Slots  : {result['slots']}")
        
        if result.get('timer'):
            print(f"Time   : {result['resolved_time']}")

if __name__ == "__main__":
    manual_test()