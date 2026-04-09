import time
import torch
from pathlib import Path
from torch.utils.data import DataLoader

from dataset import prepare_datasets
from model import JointIntentSlotModel
from train import train_model
from evaluate import evaluate_intents, evaluate_slots, print_misclassifications

def run_pipeline():
    base_dir = Path(__file__).parent
    data_path = base_dir / "data" / "training_data.json"
    models_dir = base_dir.parent / "models/bert_finetuned"

    # Chose correct device    
    device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
        
    print("1. Preparing datasets")
    data_artifacts = prepare_datasets(json_data_path=str(data_path))
    train_loader = DataLoader(data_artifacts["train_dataset"], batch_size=8, shuffle=True)
    val_loader = DataLoader(data_artifacts["val_dataset"], batch_size=8)

    intent2id = data_artifacts["intent2id"]
    slot2id = data_artifacts["slot2id"]
    id2intent = data_artifacts["id2intent"]
    id2slot = data_artifacts["id2slot"]
    tokenizer = data_artifacts["tokenizer"]

    print("\n2. Initializing Model")
    model = JointIntentSlotModel(num_intents=len(intent2id), num_slots=len(slot2id)).to(device)

    print("\n3. Training Model")
    model = train_model(model, train_loader, device, epochs=20)

    print("\n4. Evaluating Model")
    evaluate_intents(model, val_loader, id2intent, device)
    evaluate_slots(model, val_loader, id2slot, device)
    print_misclassifications(model, val_loader, id2intent, id2slot, tokenizer, device)

    print("\n5. Saving Artifacts/Weights")
    save_path = models_dir / f"run_{int(time.time())}"
    save_path.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), save_path / "pytorch_model.bin")
    torch.save({"intent2id": intent2id, "slot2id": slot2id}, save_path / "label_maps.pt")

    print(f"Pipeline complete. Model weights saved to {save_path}")

if __name__ == "__main__":
    run_pipeline()


        
    