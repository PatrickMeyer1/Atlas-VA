import json
import numpy as np

with open("enrolment_embeddings.json", "r", encoding="utf-8") as f:
    enrolments = json.load(f)

for name, embedding_list in enrolments.items():
    embedding = np.array(embedding_list, dtype=np.float32)
    print(name)
    print(embedding)
    print(len(embedding))