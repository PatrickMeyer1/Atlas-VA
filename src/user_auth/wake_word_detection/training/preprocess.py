import os
import librosa
import soundfile as sf
import numpy as np
import warnings

def print_file_count(folder):
    print("Current files in: " + str(folder))
    for label in ["near", "positive", "other"]:
        type_folder = os.path.join(folder, label)
        print(f"{label.upper()}: {len(os.listdir(type_folder))}")
    print()

def preprocess_audio(original_folder, processed_folder, target_sr, num_samples):
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
    for label in ["positive", "other", "near"]:
        input_folder = os.path.join(original_folder, label)
        output_folder = os.path.join(processed_folder, label)

        for filename in os.listdir(input_folder):     # for filename in os.listdir(input_dir)[:20]:
            try:
                if not filename.endswith(".m4a"):
                    print(f"Skipping {filename} (not an .m4a file)")
                    continue

                input_path = os.path.join(input_folder, filename)

                # Load + resample
                y, _ = librosa.load(input_path, sr=target_sr, mono=True)

                # Normalize to [-1, 1]
                max_val = np.max(np.abs(y))
                if max_val > 0:
                    y = y / max_val

                # Pad or truncate
                if len(y) < num_samples:
                    y = np.pad(y, (0, num_samples - len(y)))
                else:
                    y = y[:num_samples]

                # Save as WAV
                output_filename = filename.replace(".m4a", ".wav")
                output_path = os.path.join(output_folder, output_filename)

                sf.write(output_path, y, target_sr)
            except Exception as e:
                print(f"Failed on {input_path}: {e}")

    print("Conversion complete.")
