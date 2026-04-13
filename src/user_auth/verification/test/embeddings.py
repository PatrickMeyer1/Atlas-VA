import numpy as np
from numpy.linalg import norm
import soundfile as sf
import torch

TARGET_SR = 16000

def cosine_similarity(A, B):
    return np.dot(A, B) / (norm(A) * norm(B))

def load_audio(file_path):
    y, sr = sf.read(file_path)

    if y.ndim > 1:
        y = y.mean(axis=1)
    return torch.from_numpy(y).float().unsqueeze(0), sr

def compute_embedding_nemo(file_path, speaker_model):
    embedding = speaker_model.get_embedding(str(file_path))
    return np.array(embedding.squeeze().cpu().tolist())

def compute_embedding_ecapa(file_path, classifier):
    signal, sr = load_audio(file_path)

    if sr == TARGET_SR:
        # Compute embedding
        with torch.no_grad():
            embedding = classifier.encode_batch(signal)
        return np.array(embedding.squeeze().cpu().tolist())

    return None

