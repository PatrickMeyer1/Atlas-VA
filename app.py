from flask import Flask, render_template, request, jsonify, send_file
import os
import glob
from src.nlu.intent_detection.inference import VoiceAssistantNLU
from src.generation.answer_generator import AnswerGenerator
from src.fulfillment.dispatcher import FulfillmentDispatcher

app = Flask(__name__)

# Components
nlu = VoiceAssistantNLU()
dispatcher = FulfillmentDispatcher()
generator = AnswerGenerator()

# global state for UI
ui_state = {
    "is_locked": True,
    "is_listening": False,
    "active_timers": []
}

@app.route('/')
def index():
    return render_template('index.html')

# Receive audio data and return a response (now just text) TO CHANGE TO AUDIO
@app.route('/chat', methods=['POST'])
def chat():
    user_text = request.json.get('text', '')
    use_llm = request.json.get('use_llm', False)

    # NLU
    intent_result = nlu.process_utterance(user_text)

    # Fulfillment
    fulfillment_result = dispatcher.dispatch(intent_result)

    # Generation
    response_text = generator.generate_answer(fulfillment_result, use_llm=use_llm)

    if fulfillment_result.get("intent") == "timer" and fulfillment_result.get("success"):
        ui_state["active_timers"].append(fulfillment_result["data"])

    return jsonify({
        "response": response_text,
        "intent": intent_result.get("intent"),
        "state": ui_state,
        "image_updated": fulfillment_result.get("is_changed", False)
    })

# Fetch last image generated
@app.route('/latest_image')
def latest_image():

    plot_dir = os.path.join("src", "control_system", "plots")
    image_files = glob.glob(os.path.join(plot_dir, "output_plot_*.png"))

    if not image_files:
        return jsonify({"error": "No image found"}), 204

    latest_image = max(image_files, key=os.path.getctime)

    return send_file(latest_image, mimetype='image/png')

@app.route('/state', methods=['GET'])
def get_state():
    return jsonify(ui_state)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)

