import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

class LegalEmbeddingModel:
    def __init__(self, model_name="nlpaueb/legal-bert-base-uncased"):
        self.model = SentenceTransformer(model_name)
        
    def encode(self, text):
        return self.model.encode(text)

class ResearchRetrievalIntelligenceAgent:
    def __init__(self, case_corpus, statute_corpus, embeddings_model_name="nlpaueb/legal-bert-base-uncased"):
        print("Initializing Research & Retrieval Intelligence Agent...")
        
        # Store original corpus
        self.case_corpus = case_corpus
        self.statute_corpus = statute_corpus
        
        # Tokenize corpus for BM25
        print("Setting up BM25...")
        self.tokenized_case_corpus = [doc.split() for doc in case_corpus]
        self.bm25 = BM25Okapi(self.tokenized_case_corpus)
        
        # Initialize embedding model
        print("Loading legal embeddings model...")
        self.dense_model = LegalEmbeddingModel(embeddings_model_name)
        
        print("Agent initialized successfully!")
        
    def hybrid_retrieve(self, query_text, k=10):
        print(f"Performing hybrid retrieval for: '{query_text}'")
        
        # Dense retrieval (semantic)
        dense_emb = self.dense_model.encode(query_text)
        print(f"Generated embedding vector of shape: {dense_emb.shape}")
        
        # Sparse retrieval (BM25)
        tokenized_query = query_text.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Get top k results from BM25
        top_bm25_indices = sorted(range(len(bm25_scores)), 
                                key=lambda i: bm25_scores[i], reverse=True)[:k]
        
        results = []
        for idx in top_bm25_indices:
            if idx < len(self.case_corpus):
                results.append({
                    'index': idx,
                    'text': self.case_corpus[idx][:200] + "...",  # Preview
                    'bm25_score': bm25_scores[idx]
                })
        
        return results
    
    def summarize_case(self, case_text):
        # Placeholder - you can implement with your preferred summarization method
        return {
            "summary": f"Summary of case (first 200 chars): {case_text[:200]}...",
            "key_points": ["Key point 1", "Key point 2"],
            "legal_principles": ["Principle 1", "Principle 2"]
        }
    
    def precedent_reasoning(self, position_text):
        # Placeholder for precedent analysis
        return {
            "supporting_cases": ["Case A supports this position", "Case B supports this position"],
            "opposing_cases": ["Case C opposes this position"],
            "strength": "Strong precedent support"
        }

# Simple test function
def test_agent():
    # Sample legal cases for testing
    sample_cases = [
        "The defendant breached their duty of care by failing to maintain safe premises.",
        "Contract interpretation requires examining the intent of the parties at formation.",
        "Negligence claims require proof of duty, breach, causation, and damages.",
        "Constitutional rights must be balanced against compelling state interests."
    ]
    
    sample_statutes = [
        "Section 1: All persons have the right to equal protection under law.",
        "Section 2: Contracts must be entered into with mutual consent."
    ]
    
    print("Creating agent...")
    agent = ResearchRetrievalIntelligenceAgent(sample_cases, sample_statutes)
    
    print("\nTesting retrieval...")
    results = agent.hybrid_retrieve("duty of care negligence")
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results):
        print(f"{i+1}. Score: {result['bm25_score']:.3f} - {result['text']}")
    
    print("\nTesting summarization...")
    summary = agent.summarize_case(sample_cases[0])
    print(f"Summary: {summary}")

if __name__ == "__main__":
    test_agent()
