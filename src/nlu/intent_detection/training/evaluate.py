import torch
from sklearn.metrics import classification_report as sklearn_classification_report
from seqeval.metrics import classification_report as seq_classification_report
from seqeval.metrics import f1_score as seq_f1_score


def evaluate_intents(model, data_loader, id2intent, device):
    model.eval()
    intent_true = []
    intent_pred = []

    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            intent_labels = batch["intent_label"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs["intent_logits"], dim=1)

            intent_true.extend(intent_labels.cpu().tolist())
            intent_pred.extend(preds.cpu().tolist())

    true_names = [id2intent[i] for i in intent_true]
    pred_names = [id2intent[i] for i in intent_pred]

    acc = sum(t == p for t, p in zip(true_names, pred_names)) / len(true_names)
    
    print("\n" + "="*50)
    print(f"INTENT EVALUATION (Accuracy: {acc:.4f})")
    print("="*50)
    print(sklearn_classification_report(true_names, pred_names))
    
    return acc

def evaluate_slots(model, data_loader, id2slot, device):
    model.eval()
    slot_true = []
    slot_pred = []

    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            slot_labels = batch["slot_labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs["slot_logits"], dim=2)

            for true_seq, pred_seq in zip(slot_labels, preds):
                t_labels = []
                p_labels = []
                for t, p in zip(true_seq, pred_seq):
                    if t.item() != -100:
                        t_labels.append(id2slot[t.item()])
                        p_labels.append(id2slot[p.item()])
                
                slot_true.append(t_labels)
                slot_pred.append(p_labels)

    print("\n" + "="*50)
    f1 = seq_f1_score(slot_true, slot_pred)
    print(f"SLOT EVALUATION (F1 Score: {f1:.4f})")
    print("="*50)
    print(seq_classification_report(slot_true, slot_pred))
    
    return f1

def print_misclassifications(model, data_loader, id2intent, id2slot, tokenizer, device, max_examples=5):
    print("\n" + "="*50)
    print("MISCLASSIFICATION ANALYSIS")
    print("="*50)
    
    model.eval()
    errors_found = 0

    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            intent_labels = batch["intent_label"].to(device)
            slot_labels = batch["slot_labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            
            # Softmax for condidence and argmax for predicted intent label
            intent_probs = torch.softmax(outputs["intent_logits"], dim=1)
            intent_preds = torch.argmax(intent_probs, dim=1)
            
            # Argmax for predictes slot
            slot_preds = torch.argmax(outputs["slot_logits"], dim=2)

            for i in range(len(input_ids)):
                if errors_found >= max_examples:
                    break
                
                intent_wrong = (intent_preds[i] != intent_labels[i]).item()
                
                valid_slots_mask = slot_labels[i] != -100
                slots_wrong = not torch.equal(slot_preds[i][valid_slots_mask], slot_labels[i][valid_slots_mask])
                
                if intent_wrong or slots_wrong:
                    tokens = tokenizer.convert_ids_to_tokens(input_ids[i])
                    
                    true_slots = [
                        id2slot[int(label)] if int(label) != -100 else "-"
                        for label in slot_labels[i]
                    ]
                    
                    pred_slots = [
                        id2slot[int(pred)] if int(label) != -100 else "-"
                        for pred, label in zip(slot_preds[i], slot_labels[i])
                    ]
                    
                    true_intent = id2intent[int(intent_labels[i])]
                    pred_intent = id2intent[int(intent_preds[i])]
                    intent_conf = intent_probs[i, intent_preds[i]].item()
                    
                    print(f"\n--- Error #{errors_found + 1} ---")
                    if intent_wrong and slots_wrong:
                        print("Type: Intent & Slot Misclassification")
                    elif intent_wrong:
                        print("Type: Intent Misclassification")
                    else:
                        print("Type: Slot Misclassification")
                        
                    print("TOKENS     :", tokens)
                    print("TRUE SLOTS :", true_slots)
                    print("PRED SLOTS :", pred_slots)
                    print("TRUE INTENT:", true_intent)
                    print("PRED INTENT:", pred_intent, f"(conf={intent_conf:.3f})\n")
                    
                    errors_found += 1

    if errors_found == 0:
        print("\nNo misclassifications found.")