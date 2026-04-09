import torch
from pathlib import Path
from transformers import AutoTokenizer

from .training.model import JointIntentSlotModel

# Calls our model and processes intents/slots
class VoiceAssistantNLU:
    def __init__(self, model_name="bert-base-uncased"): # We could pass device in since it's also used in answer generator
        self.device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))

        base_dir = Path(__file__).parent
        models_path = base_dir / "models" / "bert_finetuned"
        run_dirs = sorted([d for d in models_path.iterdir() if d.is_dir()], reverse=True)
        if not run_dirs:
            raise FileNotFoundError("No trained models found.")
        
        latest_run = run_dirs[0]
        print(f"Loading NLU weights from {latest_run.name}...")

        maps = torch.load(latest_run / "label_maps.pt", map_location=self.device, weights_only=True)
        self.id2intent = {i : intent for intent, i in maps["intent2id"].items()}
        self.id2slot = {i: slot for slot, i in maps["slot2id"].items()}
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = JointIntentSlotModel(len(self.id2intent), len(self.id2slot), model_name)
        self.model.load_state_dict(torch.load(latest_run / "pytorch_model.bin", map_location=self.device, weights_only=True))
        self.model.to(self.device)
        self.model.eval()

    def process_utterance(self, text):
        encodings = self.tokenizer(
            text.split(),
            is_split_into_words=True,
            padding=True,
            truncation=True,
            max_length=32, # give buffer
            return_tensors="pt"
        )

        with torch.no_grad():
            # Do a forward pass for prediction
            input_ids = encodings["input_ids"].to(self.device)
            attention_mask = encodings["attention_mask"].to(self.device)
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

            # Extract classifications
            intent = torch.argmax(outputs["intent_logits"], dim=1).item()
            slots_preds_idx = torch.argmax(outputs["slot_logits"], dim=2)[0].cpu().tolist()

            word_ids = encodings.word_ids(batch_index=0)
            tokens = self.tokenizer.convert_ids_to_tokens(input_ids[0])

            extracted_slots = {}
            last_slot_key = None

            for idx, word_id in enumerate(word_ids):
                if word_id is None:
                    continue # skip [CLS], [SEP], [PAD]

                val = tokens[idx].replace("##", "")

                # is it the start of a new word
                if idx == 0 or word_id != word_ids[idx-1]:

                    slot_label = self.id2slot[slots_preds_idx[idx]] # get slot of curr index

                    if slot_label != "O":
                        clean_key = slot_label.split("-")[1].lower() # Get second part of B-SLOT

                        if clean_key in extracted_slots:
                            extracted_slots[clean_key] += f" {val}" # Merges together B's with I's
                        else:
                            # new entry
                            extracted_slots[clean_key] = val 
                        last_slot_key = clean_key
                    else:
                        last_slot_key = None
                else:
                    if last_slot_key:
                        extracted_slots[last_slot_key] += val # Adds wordpieces to slots even if they're not predicted as slots            
        
        return {"intent": self.id2intent[intent], "slots": extracted_slots}
