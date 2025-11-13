import os
import glob
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from rank_bm25 import BM25Okapi
import requests

# === 1. Load legal cases from all JSON files in a folder ===
def load_cases_from_folder(folder_path):
    files = glob.glob(os.path.join(folder_path, "*.json"))
    cases = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    cases.extend(data)
                else:
                    cases.append(data)
            except Exception as e:
                print(f"Error loading {file}: {e}")
    return cases

# === 2. Prepare texts and metas for indexing, robust to variant field names ===
def extract_main_text(case):
    # Try common keys in order
    for key in ["text", "body", "case_text", "facts"]:
        text = case.get(key, "")
        if text.strip():
            return text
    return ""  # No main text found

def prepare_texts_and_metas(cases):
    texts, metas = [], []
    for i, case in enumerate(cases):
        text = extract_main_text(case)
        meta = {
            "case_name": case.get("name", ""),
            "citation": case.get("citation", ""),
            "file_index": i + 1,
        }
        if text.strip():
            texts.append(text)
            metas.append(meta)
        else:
            print(f"Warning: No text found for case index {i+1}. Fields available: {list(case.keys())}")
    return texts, metas

# === 3. BM25 index ===
def build_bm25(texts):
    tokenized = [text.split() for text in texts]
    bm25 = BM25Okapi(tokenized)
    return bm25

# === 4. FAISS dense vector index ===
def build_faiss(texts, embedder):
    embeddings = embedder.encode(texts, show_progress_bar=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings.astype("float32"))
    return index, embeddings

# === 5. Hybrid retrieval function ===
def hybrid_search(query, bm25, faiss_index, embeddings, texts, metas, embedder, top_k=5):
    bm25_scores = bm25.get_scores(query.split())
    bm25_indices = np.argsort(bm25_scores)[::-1][:top_k]

    query_vec = embedder.encode([query])[0]
    _, faiss_indices = faiss_index.search(np.array([query_vec]).astype("float32"), top_k)

    # Merge and rank candidates
    candidates = set(list(bm25_indices) + list(faiss_indices[0]))
    ranked = sorted(
        list(candidates),
        key=lambda idx: bm25_scores[idx] + np.dot(query_vec, embeddings[idx]),
        reverse=True
    )
    results = []
    for i in ranked[:top_k]:
        results.append((metas[i], texts[i]))
    return results

# === 6. Ollama LLM summarization ===
def ollama_completion(prompt, model="llama2"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt}
    )
    response.raise_for_status()
    return response.json().get("response", "")

if __name__ == "__main__":
    # === CONFIG ===
    dataset_folder = r"D:\AIP\data"
    ollama_model = "llama2"
    embedder = SentenceTransformer("all-MiniLM-L6-v2")  # Swap for other local HF model if desired

    # === Load & Prepare Data ===
    cases = load_cases_from_folder(dataset_folder)
    print(f"Loaded {len(cases)} cases.")
    texts, metas = prepare_texts_and_metas(cases)
    print(f"Prepared {len(texts)} non-empty case texts for indexing.")

    if not texts:
        raise ValueError("No valid case texts found in your dataset folder. Please check field names and JSON format!")

    bm25 = build_bm25(texts)
    faiss_index, embeddings = build_faiss(texts, embedder)

    # === Run Query ===
    query = "prejudice against minorities in contract law"
    results = hybrid_search(query, bm25, faiss_index, embeddings, texts, metas, embedder, top_k=3)

    # === Summarize with Ollama ===
    print("\nTop Ranked Cases and Summaries:")
    for meta, text in results:
        print(f"\n- {meta['case_name']} ({meta['citation']})")
        excerpt = text[:1000]  # Limit input size to the LLM for summary
        prompt = (
            f"Summarize the following case law text. Extract ratio decidendi, obiter dicta, and headnotes. "
            f"Return key pro-plaintiff and pro-defendant arguments.\n\nCase law:\n{excerpt}"
        )
        summary = ollama_completion(prompt, model=ollama_model)
        print("Summary:")
        print(summary)
        print("-" * 60)
