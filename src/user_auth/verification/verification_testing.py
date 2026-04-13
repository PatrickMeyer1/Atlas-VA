from pathlib import Path
import torchaudio
from speechbrain.inference.speaker import EncoderClassifier

# Recording DIR
recording_dir = Path(__file__).parent.parent / "wake_word_detection" / "training" / "data" / "Original"

print(recording_dir)


# classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")

# signal, fs = torchaudio.load('tests/samples/ASR/spk1_snt1.wav')
# embeddings = classifier.encode_batch(signal)
# print(embeddings)
