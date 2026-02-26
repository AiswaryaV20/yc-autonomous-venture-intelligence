import numpy as np
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from db.database import SessionLocal
from db.models import Company

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("embeddings/company_index.faiss")

with open("embeddings/id_map.pkl", "rb") as f:
    id_map = pickle.load(f)


def compute_score(company_name, query_text):
    query_vector = model.encode(query_text).astype("float32")
    D, I = index.search(np.array([query_vector]), 10)

    score = 0
    for pos in I[0]:
        if pos == -1:
            continue
        if id_map[pos]:
            score += 1

    return min(score * 10, 100)


def score_company(company):
    growth_score = compute_score(company.name, "high growth startup")
    innovation_score = compute_score(company.name, "innovative technology company")
    risk_score = 100 - compute_score(company.name, "stable profitable company")

    explanation = (
        f"Growth score derived from semantic similarity to growth-oriented queries.\n"
        f"Innovation score derived from similarity to innovation queries.\n"
        f"Risk score inversely related to stability similarity."
    )

    return growth_score, innovation_score, risk_score, explanation