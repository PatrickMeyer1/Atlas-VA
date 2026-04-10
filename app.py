from flask import Flask, render_template, request, jsonify, send_file
import os
import glob
from pathlib import Path
from src.nlu.intent_detection.inference import VoiceAssistantNLU
from src.generation.answer_generator import AnswerGenerator
from src.fulfillment.dispatcher import FulfillmentDispatcher
from src.user_auth import verification


def _load_env_file() -> None:
    """Load KEY=VALUE pairs from a local .env file (demo convenience).

    This avoids requiring `huggingface-cli login` by letting you set HF_TOKEN in `.env`.
    """

    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file()

app = Flask(__name__)

# Components
nlu = None
dispatcher = FulfillmentDispatcher()
generator = AnswerGenerator()


def _get_nlu() -> VoiceAssistantNLU:
    global nlu
    if nlu is None:
        nlu = VoiceAssistantNLU()
    return nlu

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


@app.route('/verification/audiostream', methods=['POST'])
def verification_audio():
    audio_file = request.files.get('audio')

    if audio_file is None:
        return jsonify({"error": "Missing audio file"}), 400

    chunk_bytes = audio_file.read() or b""
    if not chunk_bytes:
        return jsonify({"error": "Empty audio chunk"}), 400

    stats = verification.ingest_audio_chunk(
        chunk_bytes=chunk_bytes,
        mimetype=audio_file.mimetype,
    )
    
    return jsonify({"ok": True, "verification": stats})

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

