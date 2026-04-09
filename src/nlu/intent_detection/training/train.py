import torch
from torch.optim import AdamW

from dataset import prepare_datasets
from model import JointIntentSlotModel

def train_model(model, train_loader, device, epochs=20, learning_rate=2e-5):
    print(f"Starting Training for {epochs} Epochs")
    optimizer = AdamW(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        model.train()
        total_loss = 0

        # cumulate the loss over batch_size before doing weight adjustments
        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            intent_labels = batch["intent_label"].to(device)
            slot_labels = batch["slot_labels"].to(device)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                intent_labels=intent_labels,
                slot_labels=slot_labels
            )

            loss = outputs["loss"]

            optimizer.zero_grad()   # clear previous gradients
            loss.backward()         # propagate loss with backpropagation
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()        # update the model's parameters

            total_loss += loss.item()

        print(f"Epoch {epoch+1} Loss: {total_loss:.4f}")

    return model