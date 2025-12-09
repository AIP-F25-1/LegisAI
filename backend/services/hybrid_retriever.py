"""
Hybrid Retrieval Service - BM25 + FAISS
Combines semantic search (FAISS) with keyword search (BM25) for better results
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

# BM25 implementation
try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    BM25Okapi = None
    logger.warning("⚠️ rank-bm25 not available. Install with: pip install rank-bm25")

# FAISS Vector Store
try:
    from services.vector_store import VectorStore
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    VectorStore = None


class HybridRetriever:
    """Combines FAISS semantic search with BM25 keyword search"""
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize hybrid retriever
        
        Args:
            vector_store: FAISS vector store instance
        """
        self.vector_store = vector_store
        self.bm25_index = None
        self.documents = []
        self.tokenized_docs = []
        
        if not BM25_AVAILABLE:
            logger.warning("⚠️ BM25 not available, falling back to semantic search only")
    
    def index_documents(self, documents: List[Dict[str, Any]]):
        """
        Index documents for both FAISS and BM25
        
        Args:
            documents: List of documents with 'text' and 'metadata' keys
        """
        self.documents = documents
        
        # Tokenize documents for BM25
        if BM25_AVAILABLE and documents:
            self.tokenized_docs = [self._tokenize(doc.get('text', '')) for doc in documents]
            self.bm25_index = BM25Okapi(self.tokenized_docs)
            logger.info(f"✅ Indexed {len(documents)} documents for BM25 search")
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25"""
        import re
        # Convert to lowercase and split on whitespace/punctuation
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def search(self, query: str, k: int = 10, 
               semantic_weight: float = 0.6,
               keyword_weight: float = 0.4,
               filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Hybrid search combining FAISS semantic + BM25 keyword
        
        Args:
            query: Search query
            k: Number of results to return
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
            filter_metadata: Optional metadata filters
            
        Returns:
            List of documents with combined scores
        """
        results = {}
        
        # 1. Semantic search using FAISS
        semantic_results = []
        if self.vector_store and FAISS_AVAILABLE:
            try:
                semantic_results = self.vector_store.search(query, k=k * 2, filter_metadata=filter_metadata)
                logger.info(f"🔍 Semantic search found {len(semantic_results)} results")
            except Exception as e:
                logger.error(f"Semantic search error: {e}")
        
        # 2. Keyword search using BM25
        keyword_results = []
        if self.bm25_index and BM25_AVAILABLE:
            try:
                query_tokens = self._tokenize(query)
                bm25_scores = self.bm25_index.get_scores(query_tokens)
                
                # Get top k results
                top_indices = np.argsort(bm25_scores)[::-1][:k * 2]
                
                for idx in top_indices:
                    if bm25_scores[idx] > 0:  # Only include documents with positive scores
                        doc = self.documents[idx].copy()
                        doc['bm25_score'] = float(bm25_scores[idx])
                        keyword_results.append(doc)
                
                logger.info(f"🔎 BM25 search found {len(keyword_results)} results")
            except Exception as e:
                logger.error(f"BM25 search error: {e}")
        
        # 3. Combine results with weighted scores
        # Normalize scores to 0-1 range
        if semantic_results:
            max_semantic = max([r.get('score', 0) for r in semantic_results]) or 1
            for result in semantic_results:
                doc_id = result.get('id', 'unknown')
                normalized_score = result.get('score', 0) / max_semantic
                result['semantic_score'] = normalized_score
                result['combined_score'] = normalized_score * semantic_weight
                # Initialize keyword_score to 0 if not present
                if 'keyword_score' not in result:
                    result['keyword_score'] = 0.0
                
                if doc_id not in results:
                    results[doc_id] = result
                else:
                    # Merge scores if document appears in both
                    results[doc_id]['semantic_score'] = normalized_score
                    results[doc_id]['combined_score'] += normalized_score * semantic_weight
        
        if keyword_results:
            max_bm25 = max([r.get('bm25_score', 0) for r in keyword_results]) or 1
            for result in keyword_results:
                doc_id = result.get('id', 'unknown')
                normalized_score = result.get('bm25_score', 0) / max_bm25
                result['keyword_score'] = normalized_score
                # Initialize semantic_score to 0 if not present
                if 'semantic_score' not in result:
                    result['semantic_score'] = 0.0
                
                if doc_id not in results:
                    result['combined_score'] = normalized_score * keyword_weight
                    results[doc_id] = result
                else:
                    # Add keyword score to existing result
                    results[doc_id]['keyword_score'] = normalized_score
                    results[doc_id]['combined_score'] += normalized_score * keyword_weight
        
        # Ensure all results have both scores (set to 0.0 if missing)
        for doc_id, result in results.items():
            if 'semantic_score' not in result:
                result['semantic_score'] = 0.0
            if 'keyword_score' not in result:
                result['keyword_score'] = 0.0
        
        # 4. Sort by combined score and return top k
        final_results = list(results.values())
        final_results.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        
        # Normalize combined scores to 0-1 range
        if final_results:
            max_combined = max([r.get('combined_score', 0) for r in final_results]) or 1
            for result in final_results:
                result['combined_score'] = result.get('combined_score', 0) / max_combined
        
        logger.info(f"✅ Hybrid search returned {len(final_results[:k])} results")
        return final_results[:k]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics"""
        return {
            "bm25_available": BM25_AVAILABLE,
            "faiss_available": FAISS_AVAILABLE and self.vector_store is not None,
            "documents_indexed": len(self.documents),
            "bm25_indexed": self.bm25_index is not None
        }
