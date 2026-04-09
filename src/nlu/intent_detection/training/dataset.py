import json
import time
import torch
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer

# Load JSON, run AutoTokenizer, align tokens with tags, return pt dataset

class JointDataset(Dataset):
    def __init__(self, encodings, slot_labels, intent_labels):
        self.encodings = encodings
        self.slot_labels = torch.tensor(slot_labels)
        self.intent_labels = torch.tensor(intent_labels)

    def __getitem__(self, idx):
        item = {
            "input_ids": self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "slot_labels": self.slot_labels[idx],
            "intent_label": self.intent_labels[idx],
        }
        return item

    def __len__(self):
        return len(self.intent_labels)

def load_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)
        
def parse_bio_tags(sentence):
    tokens = []
    slots = []

    for word in sentence.split():

        if "/" in word:
            token, slot = word.split("/")
        else:
            token = word
            slot = "O"

        tokens.append(token)
        slots.append(slot)

    return tokens, slots

def align_labels(all_tokens, all_slots, encodings, slot2id):
    aligned_labels = []
    
    for i in range(len(all_tokens)):
        word_ids = encodings.word_ids(batch_index=i)
        previous_word_id = None
        label_ids = []

        for word_id in word_ids:
            if word_id is None:
                label_ids.append(-100)
            elif word_id != previous_word_id:
                label_ids.append(slot2id[all_slots[i][word_id]])
            else:
                label_ids.append(-100)

            previous_word_id = word_id
        aligned_labels.append(label_ids)

    return aligned_labels

def prepare_datasets(json_data_path, model_name="bert-base-uncased", test_size=0.2):
    data = load_data(json_data_path)

    all_tokens, all_slots, all_intents = [], [], []
    seen_sentences = set()
    
    # Retrieve 'O' or 'B/I' for each word
    for intent_name, sentences in data.items():
        for sentence in sentences:
            if sentence in seen_sentences: # in case accidental duplicates
                continue
            seen_sentences.add(sentence.lower())
            
            tokens, slots = parse_bio_tags(sentence)
            all_tokens.append(tokens)
            all_slots.append(slots)
            all_intents.append(intent_name)

    # retrieve unique slots
    unique_slots = set()
    for slot in all_slots:
        unique_slots.update(slot)
    unique_slots = sorted(list(unique_slots))

    # create mappings
    slot2id = {slot: i for i, slot in enumerate(unique_slots)}
    id2slot = {i: slot for slot, i in slot2id.items()}

    # retrieve unique intents
    unique_intents = sorted(list(set(all_intents)))

    # create mappings
    intent2id = {intent: i for i, intent in enumerate(unique_intents)}
    id2intent = {i: intent for intent, i in intent2id.items()}

    # Convert the intents to their respective labels
    intent_labels_ids = [intent2id[i] for i in all_intents]

    # Tokenize data
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    encodings = tokenizer(
        all_tokens,
        is_split_into_words=True,
        padding=True,
        truncation=True,
        max_length=32, # give buffer
        return_tensors="pt"
    )

    # align the slots
    aligned_labels = align_labels(all_tokens, all_slots, encodings, slot2id)

    # train/val split
    indices = list(range(len(intent_labels_ids)))
    train_idx, val_idx = train_test_split(indices, test_size=test_size, random_state=42)

    train_encodings = {
        "input_ids": encodings["input_ids"][train_idx],
        "attention_mask": encodings["attention_mask"][train_idx],
    }

    val_encodings = {
        "input_ids": encodings["input_ids"][val_idx],
        "attention_mask": encodings["attention_mask"][val_idx],
    }

    train_slots = [aligned_labels[i] for i in train_idx]
    val_slots = [aligned_labels[i] for i in val_idx]

    train_intents = [intent_labels_ids[i] for i in train_idx]
    val_intents = [intent_labels_ids[i] for i in val_idx]
    
    train_dataset = JointDataset(train_encodings, train_slots, train_intents)
    val_dataset = JointDataset(val_encodings, val_slots, val_intents)

    return {
        "train_dataset": train_dataset,
        "val_dataset": val_dataset,
        "intent2id": intent2id,
        "id2intent": id2intent,
        "slot2id": slot2id,
        "id2slot": id2slot,
        "tokenizer": tokenizer
    }