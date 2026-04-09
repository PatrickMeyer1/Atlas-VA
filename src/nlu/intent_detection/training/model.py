import torch.nn as nn
from transformers import AutoModel

class JointIntentSlotModel(nn.Module):
    def __init__(self, num_intents, num_slots, model_name="bert-base-uncased"):
        super().__init__()

        self.encoder = AutoModel.from_pretrained(model_name)

        hidden_size = self.encoder.config.hidden_size  # 768

        # Using simple linear layers as they performed best in full fine-tuning.

        # Intent head (sentence-level)
        self.intent_classifier = nn.Linear(hidden_size, num_intents)
        # Slot head (token-level)
        self.slot_classifier = nn.Linear(hidden_size, num_slots)

    def forward(self, input_ids, attention_mask, intent_labels=None, slot_labels=None):

        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        sequence_output = outputs.last_hidden_state
        cls_output = sequence_output[:, 0]   # CLS token

        intent_logits = self.intent_classifier(cls_output)
        slot_logits = self.slot_classifier(sequence_output)

        loss = None

        # Calculate loss
        if intent_labels is not None and slot_labels is not None:

            intent_loss_fn = nn.CrossEntropyLoss()
            slot_loss_fn   = nn.CrossEntropyLoss(ignore_index=-100)

            intent_loss = intent_loss_fn(
                intent_logits,
                intent_labels
            )

            slot_loss = slot_loss_fn(
                slot_logits.view(-1, slot_logits.shape[-1]),
                slot_labels.view(-1)
            )

            loss = intent_loss + slot_loss

        return {
            "loss": loss,
            "intent_logits": intent_logits,
            "slot_logits": slot_logits
        }