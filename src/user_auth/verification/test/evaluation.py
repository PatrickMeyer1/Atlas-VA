from sklearn.metrics import (
    f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix, ConfusionMatrixDisplay
)
from IPython.display import display
import matplotlib.pyplot as plt
import pandas as pd
import os

from embeddings import compute_embedding_ecapa, cosine_similarity, compute_embedding_nemo

# Reference: Minimally adapted from Brent's CSI4106 A3 (no adaptation required)
def report_metrics(y_test, y_pred, y_proba, filename):
    # Calculate metrics
    metrics_dict = {
        "Precision": round(precision_score(y_test, y_pred, zero_division=0), 2),
        "Recall": round(recall_score(y_test, y_pred, zero_division=0), 2),
        "F1-Score": round(f1_score(y_test, y_pred, zero_division=0), 2),
        "ROC/AUC": round(roc_auc_score(y_test, y_proba), 2)
    }

    # Store metrics in a DataFrame
    results_df = pd.DataFrame.from_dict([metrics_dict])

    # Print results
    print(f"Metrics for the {filename} file: ")
    display(results_df)

def create_confusion_matrix(name, y_test, y_pred):
    
    cm = confusion_matrix(y_test, y_pred)

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Not " + name, name]
    )

    disp.plot(cmap="Blues")
    plt.show()

def evaluate_embeddings(name, reference_file_path, recording_dir, classifier, model_type, show_speaker_only=False):
    if model_type == "ECAPA":
        reference_embedding = compute_embedding_ecapa(reference_file_path, classifier)
    elif model_type == "NEMO":
        reference_embedding = compute_embedding_nemo(reference_file_path, classifier)
    else:
        print("Invalid model type.")
        return
    if reference_embedding is None:
        print("Failed to compute reference embedding.")
        return
    print(reference_embedding)

    results = []
    for label in ["positive", "near", "other"]:
        input_folder = os.path.join(recording_dir, label)
        for filename in os.listdir(input_folder):
            input_path = os.path.join(input_folder, filename)
            if os.path.abspath(input_path) == os.path.abspath(reference_file_path):
                continue
            if model_type == "ECAPA":
                current_embedding = compute_embedding_ecapa(input_path, classifier)
            else:
                current_embedding = compute_embedding_nemo(input_path, classifier)
            speaker_name = filename.split("-")[0]
            if current_embedding is not None:
                similarity = cosine_similarity(reference_embedding, current_embedding)
                results.append({
                    "filename": filename,
                    "similarity": similarity,
                    "true value": 1 if name == speaker_name else 0,
                    "classification": similarity > 0.34
                })

    results.sort(key=lambda x: x["similarity"], reverse=True)

    print(
        f"{'Rank':<10} | {'Filename':<29} | {'Similarity':>11} | {'True Value':>9} | {'Classification':<14}"
    )
    print("-" * 80)

    if show_speaker_only:
        for i, item in enumerate(results):
            speaker_name = item['filename'].split("-")[0]
            if name == speaker_name:
                print(f"{i+1:<10} | {item['filename']:<30}| {item['similarity']:>12.2f}| {item['true value']:>11}| {item['classification']:<14}")
    else:
        for i, item in enumerate(results[:20]):
            print(f"{i+1:<10} | {item['filename']:<30}| {item['similarity']:>12.2f}| {item['true value']:>11}| {item['classification']:<14}")

    # Evaluate results
    true_values = [int(item["true value"]) for item in results]
    similarities = [item["similarity"] for item in results]
    classifications = [int(item["classification"]) for item in results]

    create_confusion_matrix(name, true_values, classifications)
    report_metrics(true_values, classifications, similarities, reference_file_path)