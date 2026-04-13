from pathlib import Path
import torchaudio
from speechbrain.inference.speaker import EncoderClassifier

# Recording DIR
recording_dir = Path(__file__).parent.parent / "wake_word_detection" / "training" / "data" / "Preprocessed"

print(recording_dir)


classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")
signal, fs = torchaudio.load(recording_dir/'Palmer-positive')
embeddings = classifier.encode_batch(signal)
print(embeddings)
