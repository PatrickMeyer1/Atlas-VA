import warnings
import librosa
import os
import numpy as np
import soundfile as sf

def preprocess_audio(original_folder, processed_folder, target_sr):
    # Ignore warnings
    warnings.filterwarnings(
    "ignore",
    message="PySoundFile failed.*",
    category=UserWarning
    )
    warnings.filterwarnings(
        "ignore",
        message="librosa.core.audio.__audioread_load",
        category=FutureWarning
    )

    print("Beginning preprocessing.")

    for filename in os.listdir(original_folder):     # for filename in os.listdir(input_dir)[:20]:
        try:
            if not filename.endswith(".m4a"):
                print(f"Skipping {filename} (not an .m4a file)")
                continue

            input_path = os.path.join(original_folder, filename)

            # Load + resample
            y, _ = librosa.load(input_path, sr=target_sr, mono=True)

            # Normalize to [-1, 1]
            max_val = np.max(np.abs(y))
            if max_val > 0:
                y = y / max_val

            # Save as WAV
            output_filename = filename.replace(".m4a", ".wav")
            output_path = os.path.join(processed_folder, output_filename)

            sf.write(output_path, y, target_sr)
        except Exception as e:
            print(f"Failed on {input_path}: {e}")

    print("Conversion complete.")