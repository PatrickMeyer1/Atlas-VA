from pathlib import Path
import os
import numpy as np
from sklearn.model_selection import train_test_split
import time
import random
import tensorflow as tf
import itertools
import pandas as pd

from preprocess import print_file_count, preprocess_audio
from prepare_dataset import label_dataset, extract_validation_test_features, extract_train_features
from model import train_model, create_confusion_matrix, report_metrics, show_misclassifications

# Helper adapted from Brent's CSI4106 A3
def set_seed(seed=42):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)
    tf.config.experimental.enable_op_determinism()

def run_pipeline(train_augments, model_number, testing=False):
    set_seed(42)
    base_dir = Path(__file__).parent

    ############################################
    ## STEP 1: Preprocess audio files into .wav
    ############################################
    # Flag to skip preprocessing
    SKIP = True

    print("1. Preprocess audio files into .wav\n")

    raw_recordings_path = base_dir / "data" / "Original"
    preprocessed_recordings_path = base_dir / "data" / "Preprocessed"

    # Make preprocessed folder if it doesn't exist
    os.makedirs(preprocessed_recordings_path, exist_ok=True)
    for label in ["positive", "other", "near"]:
        os.makedirs(os.path.join(preprocessed_recordings_path, label), exist_ok=True)

    # Print count of currently existing files
    print_file_count(raw_recordings_path)
    print_file_count(preprocessed_recordings_path)

    # Convert files to .wav
    TARGET_SR = 16000
    DURATION = 2.5
    NUM_SAMPLES = int(TARGET_SR * DURATION)
    if not SKIP:
        preprocess_audio(raw_recordings_path, preprocessed_recordings_path, TARGET_SR, NUM_SAMPLES)

        # Print count after preprocessing
        print_file_count(preprocessed_recordings_path)
    else:
        print("Skipping conversion.")
    print()

    ############################################
    ## STEP 2: Label data
    ############################################

    print("2. Label dataset\n")

    file_paths, y_labels = label_dataset(preprocessed_recordings_path)
    print("Finished labelling the dataset.")
    print()

    ############################################
    ## STEP 3: Split data
    ############################################

    # 80 Train, 10 Validation, 10 Test
    test_size = 0.2

    print("3. Split dataset\n")

    X_train_files, X_temp, y_train, y_temp = train_test_split(
        file_paths,
        y_labels,
        test_size=test_size,
        random_state=42,
        stratify=y_labels
    )

    X_validation_files, X_test_files, y_validation, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.5,
        random_state=42,
        stratify=y_temp
    )

    print(f"Train: {len(X_train_files)} | Val: {len(X_validation_files)} | Test: {len(X_test_files)}")
    print("Finished splitting the dataset.")
    print()

    ############################################
    ## STEP 4: Augment and extract features
    ############################################

    print("4. Augment dataset and extract features\n")

    print("Augment training data and extract training features: ") 
    X_train = extract_train_features(X_train_files, train_augments)
    y_train_augmented = np.repeat(y_train, 1 + len(train_augments))
    print()

    print("Extract validation features: ")
    X_validation = extract_validation_test_features(X_validation_files)
    print()

    print("Extract testing features: ")
    X_test = extract_validation_test_features(X_test_files)
    print()

    print("Finished extracting features.")
    print()

    ############################################
    ## STEP 5: Train model
    ############################################

    print("5. Training model.\n")

    model = train_model(X_train, X_validation, y_train_augmented, y_validation, model_number)

    print("Model training complete.")
    print()

    ############################################
    ## STEP 6: Evaluate model
    ############################################

    print("6. Evaluate model.\n")

    # Make predictions for evaluation
    y_pred_prob = model.predict(X_test).ravel()
    y_pred = (y_pred_prob > 0.5).astype(int)

    metrics = report_metrics(y_test, y_pred, y_pred_prob, "test")
    print()

    # create_confusion_matrix(y_test, y_pred)
    # print()

    show_misclassifications(y_test, y_pred, y_pred_prob, X_test_files)

    print("Model evaluation complete.")

    if testing:
        return metrics
    
    ############################################
    ## STEP 7: Save model
    ############################################

    print("7. Save model.\n")

    save_path = base_dir.parent / "models" / f"run_{int(time.time())}"
    save_path.mkdir(parents=True, exist_ok=True)

    model.save(save_path / "model.keras")
    print(save_path)

    print(f"Pipeline complete. Model weights saved to {save_path}")

TEST = False

###########
# TRAINIING
###########

# Train and save model using best params
if not TEST:
    run_pipeline(["time"], 4)

###########
# TESTING
###########

if TEST:
    # Options
    # models = [0, 1, 2, 3, 4]
    # augments = ["volume", "time", "bg_noise"]

    # Selected options
    models = [0, 1, 2, 3, 4]
    augments = ["volume", "time", "bg_noise"]
    augment_combinations = []

    for i in range(1, len(augments)+1):
        augment_combinations.extend([list(x) for x in itertools.combinations(augments, i)])

    augment_combinations.append([])

    results = []

    for augment_combination in augment_combinations:
        for model in models:
            metrics = run_pipeline(augment_combination, model, True)
            print(metrics)
            result = {
                "Model": model,
                "Augments": ", ".join(augment_combination) if augment_combination else "None",
                **metrics
            }

            results.append(result)

    df = pd.DataFrame(results)
    df = df.sort_values(by="F1-Score", ascending=False).reset_index(drop=True)

    print(df)