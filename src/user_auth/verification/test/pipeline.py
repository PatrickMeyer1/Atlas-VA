from pathlib import Path
import os

from preprocessing import preprocess_audio
from evaluation import evaluate_embeddings

TARGET_SR = 16000

def run_pipeline(names, model_type):
    base_dir = Path(__file__).parent
    recording_dir = Path(__file__).parent.parent.parent / "wake_word_detection" / "training" / "data" / "Preprocessed"

    ############################################
    ## STEP 1: Preprocess audio files into .wav
    ############################################
    # Flag to skip preprocessing
    SKIP = False

    print("1. Preprocess audio files into .wav\n")

    raw_recordings_path = base_dir / "data" / "Original"
    preprocessed_recordings_path = base_dir / "data" / "Preprocessed"
    # Make preprocessed folder if it doesn't exist
    os.makedirs(preprocessed_recordings_path, exist_ok=True)

    if not SKIP:
        preprocess_audio(raw_recordings_path, preprocessed_recordings_path, TARGET_SR)
    else:
        print("Skipping conversion.")
    print()

    ############################################
    ## STEP 2: Run classifiers and evaluate
    ############################################

    print("2. Run the classification on the selected file and evalute results\n")

    # Initialize classifier
    if model_type == "ECAPA":
        from speechbrain.inference.speaker import EncoderClassifier
        classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")

        # Classify and Evaluate
        for name in names:
            filename = name + ".wav"
            print(f"Running on {filename}")
            file_path = preprocessed_recordings_path / filename
            evaluate_embeddings(name, file_path, recording_dir, classifier, model_type)
            print()
    else:
        import nemo.collections.asr as nemo_asr
        speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained("nvidia/speakerverification_en_titanet_large")

        # Classify and Evaluate
        for name in names:
            filename = name + ".wav"
            print(f"Running on {filename}")
            file_path = preprocessed_recordings_path / filename
            evaluate_embeddings(name, file_path, recording_dir, speaker_model, model_type)
            print()

run_pipeline(["Patrick", "Palmer", "Rosenblatt"], "NEMO")
