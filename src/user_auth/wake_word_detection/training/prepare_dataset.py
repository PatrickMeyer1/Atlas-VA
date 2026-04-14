import librosa
import os
import numpy as np
import torch
import torchaudio

def label_dataset(processed_dir):
    y_labels = []
    file_paths = []

    # positive is 1 (wake), and both other and near become 0 (not wake)
    label_map = {
        "positive": 1,
        "other": 0,
        "near": 0
    }

    for label, class_id in label_map.items():
        folder = os.path.join(processed_dir, label)

        for filename in os.listdir(folder):
            if not filename.endswith(".wav"):
                continue

            path = os.path.join(folder, filename)
            y_labels.append(class_id)
            file_paths.append(path)

    y_labels = np.array(y_labels)
    file_paths = np.array(file_paths)

    print("file_paths shape:", file_paths.shape)
    print("y shape:", y_labels.shape)
    return file_paths, y_labels

# Define the extract_mfcc with default parameters
def extract_mfcc(file_path, sr=16000, window_sec=0.025, hop_sec=0.010, n_mfcc=13):
    """
    file_path: path to .wav file
    sr: sampling rate
    window_sec: window size in seconds (slice)
    hop_sec: hop size in seconds
    n_mfcc: number of MFCC coefficients
    """

    # Load audio
    y, sr = librosa.load(file_path, sr=sr)

    n_fft = int(window_sec * sr)       # window length in samples
    hop_length = int(hop_sec * sr)     # hop length in samples

    # Match the MFCC settings used during training (previously via librosa.feature.mfcc).
    transform = torchaudio.transforms.MFCC(
        sample_rate=sr,
        n_mfcc=n_mfcc,
        dct_type=2,
        norm="ortho",
        log_mels=False,
        melkwargs={
            "n_fft": n_fft,
            "win_length": n_fft,
            "hop_length": hop_length,
            "window_fn": torch.hann_window,
            "n_mels": 128,
            "center": True,
            "pad_mode": "constant",
            "power": 2.0,
            "norm": "slaney",
            "mel_scale": "slaney",
        },
    )

    waveform = torch.as_tensor(y, dtype=torch.float32)
    with torch.inference_mode():
        mfcc = transform(waveform)

    return mfcc.detach().cpu().numpy().astype(np.float32, copy=False)

def extract_train_features(file_paths):
    X = []

    for file_path in file_paths:
        mfcc = extract_mfcc(file_path)
        X.append(mfcc)

    X = np.array(X)
    print("X shape:", X.shape)

    # adds a channel parameter (as they are treated as images)
    X = X[..., np.newaxis]
    print("X shape after channel dimension:", X.shape)
    return X

def extract_validation_test_features(file_paths):
    X = []

    for file_path in file_paths:
        mfcc = extract_mfcc(file_path)
        X.append(mfcc)

    X = np.array(X)
    print("X shape:", X.shape)

    # adds a channel parameter (as they are treated as images)
    X = X[..., np.newaxis]
    print("X shape after channel dimension:", X.shape)
    return X