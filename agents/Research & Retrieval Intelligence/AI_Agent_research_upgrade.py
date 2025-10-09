import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from transformers import pipeline
import pickle
import os
import torch

class LegalEmbeddingModel:
    def __init__(self, model_name="nlpaueb/legal-bert-base-uncased"):
        self.model = SentenceTransformer(model_name)
        
    def encode(self, text):
        return self.model.encode(text)
    
    def encode_batch(self, texts):
        return self.model.encode(texts)

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
        
        # Setup FAISS index
        print("Building FAISS index...")
        self.faiss_index = self._build_faiss_index()
        
        # Initialize local LLM for summarization
        print("Loading local LLM for summarization...")
        self._setup_local_llm()
        
        print("Agent initialized successfully!")
    
    def _build_faiss_index(self):
        """Build FAISS index from case corpus"""
        # Check if index already exists
        index_file = "faiss_legal_index.idx"
        embeddings_file = "case_embeddings.pkl"
        
        if os.path.exists(index_file) and os.path.exists(embeddings_file):
            print("Loading existing FAISS index...")
            index = faiss.read_index(index_file)
            return index
        
        print("Creating new FAISS index...")
        # Generate embeddings for all cases
        case_embeddings = self.dense_model.encode_batch(self.case_corpus)
        
        # Save embeddings for later use
        with open(embeddings_file, 'wb') as f:
            pickle.dump(case_embeddings, f)
        
        # Create FAISS index
        dimension = case_embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(case_embeddings)
        index.add(case_embeddings.astype('float32'))
        
        # Save index
        faiss.write_index(index, index_file)
        print(f"FAISS index created with {index.ntotal} vectors")
        
        return index
    
    def _setup_local_llm(self):
        """Initialize local LLM for summarization"""
        try:
            # Using a smaller, efficient model for summarization
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",  # Good for legal text
                device=0 if torch.cuda.is_available() else -1
            )
            print("Local LLM loaded successfully!")
        except Exception as e:
            print(f"Error loading LLM: {e}")
            self.summarizer = None
    
    def semantic_retrieve(self, query_text, k=10):
        """FAISS-based semantic retrieval"""
        query_embedding = self.dense_model.encode([query_text])
        faiss.normalize_L2(query_embedding)
        
        # Search FAISS index
        scores, indices = self.faiss_index.search(query_embedding.astype('float32'), k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.case_corpus):
                results.append({
                    'index': int(idx),
                    'text': self.case_corpus[idx],
                    'semantic_score': float(score),
                    'rank': i + 1
                })
        
        return results
    
    def hybrid_retrieve(self, query_text, k=10, alpha=0.5):
        """Enhanced hybrid retrieval with FAISS + BM25"""
        print(f"Performing hybrid retrieval for: '{query_text}'")
        
        # Semantic retrieval (FAISS)
        semantic_results = self.semantic_retrieve(query_text, k)
        
        # Sparse retrieval (BM25)
        tokenized_query = query_text.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Normalize BM25 scores
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
        normalized_bm25 = [score / max_bm25 for score in bm25_scores]
        
        # Combine scores
        hybrid_results = {}
        
        # Add semantic results
        for result in semantic_results:
            idx = result['index']
            hybrid_results[idx] = {
                'text': result['text'],
                'semantic_score': result['semantic_score'],
                'bm25_score': normalized_bm25[idx] if idx < len(normalized_bm25) else 0,
                'hybrid_score': 0
            }
        
        # Add top BM25 results
        top_bm25_indices = sorted(range(len(normalized_bm25)), 
                                key=lambda i: normalized_bm25[i], reverse=True)[:k]
        
        for idx in top_bm25_indices:
            if idx not in hybrid_results and idx < len(self.case_corpus):
                hybrid_results[idx] = {
                    'text': self.case_corpus[idx],
                    'semantic_score': 0,
                    'bm25_score': normalized_bm25[idx],
                    'hybrid_score': 0
                }
        
        # Calculate hybrid scores
        for idx in hybrid_results:
            semantic_score = hybrid_results[idx]['semantic_score']
            bm25_score = hybrid_results[idx]['bm25_score']
            hybrid_results[idx]['hybrid_score'] = alpha * semantic_score + (1 - alpha) * bm25_score
        
        # Sort by hybrid score
        sorted_results = sorted(hybrid_results.items(), 
                              key=lambda x: x[1]['hybrid_score'], reverse=True)[:k]
        
        final_results = []
        for idx, data in sorted_results:
            final_results.append({
                'index': idx,
                'text': data['text'][:200] + "...",
                'semantic_score': data['semantic_score'],
                'bm25_score': data['bm25_score'],
                'hybrid_score': data['hybrid_score']
            })
        
        return final_results
    
    def summarize_case_local(self, case_text, max_length=150, min_length=50):
        """Local LLM-based case summarization"""
        if not self.summarizer:
            return self.summarize_case(case_text)  # Fallback to simple summary
        
        try:
            # Truncate text if too long for the model
            max_input_length = 1024
            if len(case_text) > max_input_length:
                case_text = case_text[:max_input_length]
            
            summary = self.summarizer(
                case_text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            
            return {
                "ai_summary": summary[0]['summary_text'],
                "method": "Local LLM (BART)",
                "case_preview": case_text[:200] + "...",
                "legal_analysis": self._extract_legal_elements(case_text)
            }
        
        except Exception as e:
            print(f"LLM summarization failed: {e}")
            return self.summarize_case(case_text)
    
    def _extract_legal_elements(self, case_text):
        """Simple rule-based legal element extraction"""
        legal_keywords = {
            'liability': ['liable', 'liability', 'responsible', 'fault'],
            'damages': ['damages', 'compensation', 'award', 'monetary'],
            'duty': ['duty', 'obligation', 'responsibility', 'care'],
            'breach': ['breach', 'violation', 'failed', 'negligent']
        }
        
        found_elements = {}
        case_lower = case_text.lower()
        
        for element, keywords in legal_keywords.items():
            for keyword in keywords:
                if keyword in case_lower:
                    found_elements[element] = True
                    break
        
        return found_elements
    
    def summarize_case(self, case_text):
        """Fallback simple summarization"""
        return {
            "summary": f"Summary of case (first 200 chars): {case_text[:200]}...",
            "key_points": ["Key point 1", "Key point 2"],
            "legal_principles": ["Principle 1", "Principle 2"]
        }

# Enhanced test function
def test_enhanced_agent():
    sample_cases = [
        "The defendant breached their duty of care by failing to maintain safe premises. The plaintiff suffered significant damages due to negligence.",
        "Contract interpretation requires examining the intent of the parties at formation. The court found the defendant liable for breach.",
        "Negligence claims require proof of duty, breach, causation, and damages. The plaintiff established all elements successfully.",
        "Constitutional rights must be balanced against compelling state interests. The court awarded monetary compensation.",
        "Corporate liability extends to officers when they personally participate in tortious conduct. Damages were substantial.",
        "Employment contracts must specify termination clauses clearly. The defendant was found negligent in their obligations."
    ]
    
    sample_statutes = [
        "Section 1: All persons have the right to equal protection under law.",
        "Section 2: Contracts must be entered into with mutual consent."
    ]
    
    print("Creating enhanced agent...")
    agent = ResearchRetrievalIntelligenceAgent(sample_cases, sample_statutes)
    
    print("\n" + "="*50)
    print("TESTING SEMANTIC RETRIEVAL (FAISS)")
    print("="*50)
    semantic_results = agent.semantic_retrieve("negligence duty of care")
    for i, result in enumerate(semantic_results[:3]):
        print(f"{i+1}. Semantic Score: {result['semantic_score']:.3f}")
        print(f"   Text: {result['text'][:100]}...")
        print()
    
    print("="*50)
    print("TESTING HYBRID RETRIEVAL (FAISS + BM25)")
    print("="*50)
    hybrid_results = agent.hybrid_retrieve("contract breach liability")
    for i, result in enumerate(hybrid_results[:3]):
        print(f"{i+1}. Hybrid Score: {result['hybrid_score']:.3f} "
              f"(Semantic: {result['semantic_score']:.3f}, BM25: {result['bm25_score']:.3f})")
        print(f"   Text: {result['text']}")
        print()
    
    print("="*50)
    print("TESTING LOCAL LLM SUMMARIZATION")
    print("="*50)
    test_case = sample_cases[0]
    summary = agent.summarize_case_local(test_case)
    print(f"Original: {test_case}")
    print(f"AI Summary: {summary.get('ai_summary', 'N/A')}")
    print(f"Legal Elements: {summary.get('legal_analysis', {})}")

if __name__ == "__main__":
    test_enhanced_agent()
