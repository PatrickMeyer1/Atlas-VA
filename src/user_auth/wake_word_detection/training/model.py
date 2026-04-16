from xml.parsers.expat import model

import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix, ConfusionMatrixDisplay
)
from IPython.display import display
import numpy as np

# Reference: Minimally adapted from Brent's CSI4106 A3
def plot_training_and_validation_loss_and_accuracy(history):
  # Save history to a DataFrame and add an epoch feature starting from 1
  history_df = pd.DataFrame(history.history)
  history_df["epoch"] = range(1, len(history_df) + 1)

  # Plot train and validation loss and Accuracy
  history_df.plot(
      figsize=(8,5), x="epoch", y=["loss", "val_loss", "accuracy", "val_accuracy"], grid=True,
      title="Loss and Accuracy vs. Epochs (Training and Validation)", xlabel="Epoch", xlim=[1,len(history_df)], ylim=[0,2]
  )
  plt.show()

def train_model(X_train, X_validation, y_train, y_validation, model_index=0):
    # Initialize the model
    model = get_model(model_index, X_train)
    model.summary()

    # Compile the model
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    # Train the model
    history = model.fit(
        X_train,
        y_train,
        epochs=10,  # We certainly need more epochs with larger dataset
        batch_size=4,
        verbose=1,
        validation_data=(X_validation, y_validation)
    )

    # plot_training_and_validation_loss_and_accuracy(history)

    return model


def get_model(model_index, X_train=None):
    
    if model_index == 0:
        # original model we had
        return models.Sequential([
        layers.Input(shape=X_train.shape[1:]),

        layers.Conv2D(32, (5, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((1,2)),

        layers.Conv2D(64, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((1,2)),

        layers.Conv2D(32, (3, 5), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),

        layers.Flatten(),
        layers.Dense(128),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.6),
        layers.Dense(1, activation='sigmoid')
    ])
    elif model_index == 1:
        return models.Sequential([
        layers.Input(shape=X_train.shape[1:]),

        layers.Conv2D(64, (5, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((1,2)),
        layers.Conv2D(128, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((1,2)),
        layers.Conv2D(64, (3, 5), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Flatten(),
        layers.Dense(256),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')

    ])

    elif model_index == 2:

        
        model = models.Sequential([
       layers.Conv2D(64, (5, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((1,2)),

        layers.Conv2D(128, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((1,2)),

        layers.Conv2D(128, (3, 5), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),

        layers.Flatten(),
        layers.Dense(256),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.3),
        layers.Dense(1, activation='sigmoid')
    ])
        
        return model
    elif model_index == 3:
        return models.Sequential([
        layers.Input(shape=X_train.shape[1:]),
        layers.Conv2D(64, (5, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((1,2)),
        layers.Conv2D(128, (5, 5), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((1,2)),
        layers.Flatten(),
        layers.Dense(256),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.5),
        layers.Dense(128),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])


    else:
        return models.Sequential([
        layers.Input(shape=X_train.shape[1:]),

        layers.Conv2D(32, (5, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((1,2)),

        layers.Conv2D(64, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((1,2)),

        layers.Conv2D(32, (3, 5), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),

        layers.Flatten(),
        layers.Dense(128),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.6),
        layers.Dense(1, activation='sigmoid')
    ])



# Reference: Minimally adapted from Brent's CSI4106 A3 (no adaptation required)
def report_metrics(y_test, y_pred, y_proba, split_name):
    # Calculate metrics
    metrics_dict = {
        "Precision": round(precision_score(y_test, y_pred, average="macro"), 2),
        "Recall": round(recall_score(y_test, y_pred, average="macro"), 2),
        "F1-Score": round(f1_score(y_test, y_pred, average="macro"), 2),
        "ROC/AUC": round(roc_auc_score(y_test, y_proba, average="macro"), 2)
    }

    # Store metrics in a DataFrame
    results_df = pd.DataFrame.from_dict([metrics_dict])

    # Print results
    print(f"Metrics for the {split_name.lower()} set: ")
    display(results_df)

def create_confusion_matrix(y_test, y_pred):
    
    cm = confusion_matrix(y_test, y_pred)

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Not Wake", "Wake"]
    )

    disp.plot(cmap="Blues")
    plt.show()

def show_misclassifications(y_test, y_pred, y_pred_prob, X_test_files):
    print("Example misclassifications include:\n")
    mis_idx = np.where(y_test != y_pred)[0]

    count = 0
    while count < 3 and count < len(mis_idx):
        print(f"Misclassification {count + 1}")
        i = mis_idx[count]

        print("True label:", y_test[i])
        print("Predicted prob:", y_pred_prob[i])
        print("File:", X_test_files[i])

        count += 1
        print()
    if not count:
        print("No misclassifications in test set.")