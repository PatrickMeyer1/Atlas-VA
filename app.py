from flask import Flask, Response, jsonify, render_template, request, send_file, stream_with_context
import os
import glob
from pathlib import Path
from src.nlu.intent_detection.inference import VoiceAssistantNLU
from src.generation.answer_generator import AnswerGenerator
from src.fulfillment.dispatcher import FulfillmentDispatcher
from src.user_auth import verification
from config import load_env_file

load_env_file()

app = Flask(__name__)

# Components
nlu = VoiceAssistantNLU()
dispatcher = FulfillmentDispatcher()
generator = AnswerGenerator()

# global state for UI
ui_state = {
    "is_locked": True,
    "is_listening": False,
    "tts_enabled": True,
    "active_timers": []
}

@app.route('/')
def index():
    return render_template('index.html')

# Receive audio data and return a response (now just text) TO CHANGE TO AUDIO
@app.route('/chat', methods=['POST'])
def chat():
    req_payload = request.get_json(silent=True) or {}
    user_text = req_payload.get('text', '')
    use_llm = req_payload.get('use_llm', False)

    if "tts_enabled" in req_payload:
        ui_state["tts_enabled"] = bool(req_payload.get("tts_enabled"))

    # NLU
    intent_result = nlu.process_utterance(user_text)

    # Fulfillment
    fulfillment_result = dispatcher.dispatch(intent_result)

    # Generation
    response_text = generator.generate_answer(fulfillment_result, use_llm=use_llm)

    tts = None
    if ui_state.get("tts_enabled"):
        tts = generator.text_to_speech(response_text, intent=fulfillment_result.get("intent"))

    if fulfillment_result.get("intent") == "timer" and fulfillment_result.get("success"):
        ui_state["active_timers"].append(fulfillment_result["data"])

    return jsonify({
        "response": response_text,
        "tts": tts,
        "intent": intent_result.get("intent"),
        "success": fulfillment_result.get("success"),
        "data": fulfillment_result.get("data"),
        "state": ui_state,
        "image_updated": fulfillment_result.get("is_changed", False)
    })


@app.route('/tts/audio', methods=['GET'])
def tts_audio():
    text = request.args.get('text', '')
    intent = request.args.get('intent')

    if not text or not str(text).strip():
        return jsonify({"error": "Missing text"}), 400

    if not generator.server_tts_available():
        return jsonify({"error": "Server-side TTS requires the edge-tts package."}), 503

    tts_payload = generator.text_to_speech(text, intent=intent)

    for field in ("voice", "rate", "pitch", "volume"):
        value = request.args.get(field)
        if value:
            tts_payload[field] = value

    return Response(
        stream_with_context(generator.stream_text_to_speech(tts_payload)),
        mimetype='audio/mpeg',
        headers={
            "Cache-Control": "no-store",
            "Content-Disposition": 'inline; filename="atlas-response.mp3"',
        },
    )

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

