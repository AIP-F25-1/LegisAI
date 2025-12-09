"""
Vector Store Service - FAISS Integration (Optimized for Large Datasets)
Handles document embeddings and semantic search with scalability optimizations
"""

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for legal documents - Optimized for large datasets"""
    
    def __init__(self, embedding_model: str = 'all-MiniLM-L6-v2', 
                 index_type: str = 'auto', persist_dir: Optional[str] = None):
        """
        Initialize vector store
        
        Args:
            embedding_model: Sentence transformer model name
            index_type: Type of FAISS index to use
                - 'flat': IndexFlatL2 (exact search, slow for >100K docs)
                - 'ivf': IndexIVFFlat (approximate, fast for >100K docs)
                - 'hnsw': IndexHNSWFlat (very fast, good for millions)
                - 'auto': Automatically choose based on dataset size
            persist_dir: Directory to persist index and documents
        """
        logger.info(f"Initializing VectorStore with model: {embedding_model}, index_type: {index_type}")
        
        # Load embedding model
        self.embeddings_model = SentenceTransformer(embedding_model)
        self.dimension = self.embeddings_model.get_sentence_embedding_dimension()
        
        # Persistence directory
        self.persist_dir = persist_dir or "data/vector_store"
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize FAISS index based on type
        self.index_type = index_type
        self.index = None
        self.quantizer = None
        self._initialize_index()
        
        # Store documents and metadata (consider using database for very large datasets)
        self.documents: List[Dict[str, Any]] = []
        
        # Try to load existing index
        self._load_if_exists()
        
        logger.info(f"✅ VectorStore initialized with dimension: {self.dimension}, index_type: {self.index_type}")
    
    def _initialize_index(self):
        """Initialize FAISS index based on type"""
        if self.index_type == 'flat' or self.index_type == 'auto':
            # Start with flat index (will upgrade if needed)
            self.index = faiss.IndexFlatL2(self.dimension)
        elif self.index_type == 'ivf':
            # IVF index for approximate search (faster for large datasets)
            nlist = 100  # Number of clusters
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            self.quantizer = quantizer
        elif self.index_type == 'hnsw':
            # HNSW index for very fast approximate search
            M = 32  # Number of connections per node
            self.index = faiss.IndexHNSWFlat(self.dimension, M)
        else:
            raise ValueError(f"Unknown index type: {self.index_type}")
    
    def _upgrade_index_if_needed(self):
        """Upgrade to faster index type if dataset is large"""
        if self.index_type == 'auto' and self.index.ntotal > 10000:
            logger.info(f"📈 Large dataset detected ({self.index.ntotal} docs), upgrading to IVF index...")
            
            # Save current index
            old_index = self.index
            old_documents = self.documents.copy()
            
            # Create new IVF index
            nlist = min(100, max(10, self.index.ntotal // 1000))  # Adaptive clustering
            quantizer = faiss.IndexFlatL2(self.dimension)
            new_index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            
            # Train the index
            logger.info("Training IVF index...")
            if old_index.ntotal > 0:
                # Get all vectors from old index
                all_vectors = old_index.reconstruct_n(0, old_index.ntotal)
                new_index.train(all_vectors)
                new_index.add(all_vectors)
            
            self.index = new_index
            self.quantizer = quantizer
            self.index_type = 'ivf'
            self.documents = old_documents
            logger.info("✅ Index upgraded to IVF")
    
    def _load_if_exists(self):
        """Load existing index and documents if they exist"""
        index_path = Path(self.persist_dir) / "index.faiss"
        docs_path = Path(self.persist_dir) / "documents.pkl"
        
        if index_path.exists() and docs_path.exists():
            try:
                logger.info(f"📂 Loading existing vector store from {self.persist_dir}...")
                self.index = faiss.read_index(str(index_path))
                
                with open(docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                
                logger.info(f"✅ Loaded {len(self.documents)} documents from disk")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load existing index: {e}")
    
    def add_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Add a document to the vector store
        
        Args:
            text: Document text
            metadata: Optional metadata (source, type, etc.)
            
        Returns:
            Document index
        """
        # Generate embedding
        embedding = self.embeddings_model.encode([text], normalize_embeddings=True)[0]
        
        # Check if index needs training (for IVF)
        if isinstance(self.index, faiss.IndexIVFFlat) and not self.index.is_trained:
            # Need to train first - collect some documents first
            if self.index.ntotal == 0:
                logger.warning("IVF index needs training. Use add_documents() with multiple docs first.")
        
        # Add to FAISS index
        embedding_array = np.array([embedding]).astype('float32')
        self.index.add(embedding_array)
        
        # Store document and metadata
        doc_id = len(self.documents)
        self.documents.append({
            'id': doc_id,
            'text': text,
            'metadata': metadata or {}
        })
        
        # Auto-upgrade index if needed
        if self.index_type == 'auto':
            self._upgrade_index_if_needed()
        
        # Auto-save periodically (every 100 documents)
        if len(self.documents) % 100 == 0:
            self.save()
        
        return doc_id
    
    def add_documents(self, texts: List[str], metadata_list: Optional[List[Dict]] = None, 
                     batch_size: int = 100) -> List[int]:
        """
        Add multiple documents at once (more efficient for large datasets)
        
        Args:
            texts: List of document texts
            metadata_list: Optional list of metadata dicts
            batch_size: Process in batches to manage memory
            
        Returns:
            List of document indices
        """
        total = len(texts)
        logger.info(f"📚 Adding {total} documents in batches of {batch_size}...")
        
        doc_ids = []
        
        # Process in batches to manage memory
        for i in range(0, total, batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadata = metadata_list[i:i + batch_size] if metadata_list else None
            
            # Generate embeddings for batch
            embeddings = self.embeddings_model.encode(
                batch_texts, 
                normalize_embeddings=True, 
                show_progress_bar=(i == 0)  # Show progress only for first batch
            )
            
            # Train index if needed (for IVF)
            if isinstance(self.index, faiss.IndexIVFFlat) and not self.index.is_trained:
                if self.index.ntotal == 0:
                    logger.info("Training IVF index...")
                    # Use a sample for training
                    nlist = min(100, max(10, len(batch_texts) // 10))
                    if len(embeddings) >= nlist:
                        self.index.train(embeddings[:nlist].astype('float32'))
            
            # Add to FAISS index
            self.index.add(embeddings.astype('float32'))
            
            # Store documents
            for j, text in enumerate(batch_texts):
                doc_id = len(self.documents)
                self.documents.append({
                    'id': doc_id,
                    'text': text,
                    'metadata': batch_metadata[j] if batch_metadata else {}
                })
                doc_ids.append(doc_id)
            
            # Progress logging
            if (i + batch_size) % 1000 == 0 or (i + batch_size) >= total:
                logger.info(f"  Progress: {min(i + batch_size, total)}/{total} documents indexed")
        
        # Auto-upgrade index if needed
        if self.index_type == 'auto':
            self._upgrade_index_if_needed()
        
        # Save after batch
        self.save()
        
        logger.info(f"✅ Added {total} documents to vector store")
        return doc_ids
    
    def search(self, query: str, k: int = 5, filter_metadata: Optional[Dict] = None,
               nprobe: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Optional metadata filters
            nprobe: Number of clusters to search (for IVF index, higher = more accurate but slower)
            
        Returns:
            List of matching documents with scores
        """
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Set nprobe for IVF index (controls speed vs accuracy tradeoff)
        if isinstance(self.index, faiss.IndexIVFFlat):
            self.index.nprobe = min(nprobe, self.index.nlist)
        
        # Generate query embedding
        query_embedding = self.embeddings_model.encode([query], normalize_embeddings=True)[0]
        
        # Search FAISS index
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(
            np.array([query_embedding]).astype('float32'), k
        )
        
        # Retrieve documents
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx == -1:  # Invalid index
                continue
            
            doc = self.documents[idx].copy()
            doc['score'] = float(1 / (1 + distance))  # Convert distance to similarity score
            doc['distance'] = float(distance)
            
            # Apply metadata filters if specified
            if filter_metadata:
                doc_metadata = doc.get('metadata', {})
                if all(doc_metadata.get(k) == v for k, v in filter_metadata.items()):
                    results.append(doc)
            else:
                results.append(doc)
        
        logger.info(f"Search returned {len(results)} results for query: {query[:50]}...")
        return results
    
    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        if 0 <= doc_id < len(self.documents):
            return self.documents[doc_id]
        return None
    
    def get_document_count(self) -> int:
        """Get total number of documents"""
        return len(self.documents)
    
    def save(self, path: Optional[str] = None):
        """Save vector store to disk"""
        save_path = path or self.persist_dir
        os.makedirs(save_path, exist_ok=True)
        
        index_path = Path(save_path) / "index.faiss"
        docs_path = Path(save_path) / "documents.pkl"
        
        # Save FAISS index
        faiss.write_index(self.index, str(index_path))
        
        # Save documents (consider using database for very large datasets)
        with open(docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
        
        logger.info(f"💾 Saved vector store to {save_path} ({len(self.documents)} documents)")
    
    def load(self, path: Optional[str] = None):
        """Load vector store from disk"""
        load_path = path or self.persist_dir
        index_path = Path(load_path) / "index.faiss"
        docs_path = Path(load_path) / "documents.pkl"
        
        if not index_path.exists() or not docs_path.exists():
            raise FileNotFoundError(f"Vector store not found at {load_path}")
        
        # Load FAISS index
        self.index = faiss.read_index(str(index_path))
        
        # Load documents
        with open(docs_path, 'rb') as f:
            self.documents = pickle.load(f)
        
        logger.info(f"📂 Loaded vector store from {load_path} ({len(self.documents)} documents)")
    
    def clear(self):
        """Clear all documents"""
        self._initialize_index()
        self.documents = []
        logger.info("Cleared vector store")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            "document_count": len(self.documents),
            "index_type": self.index_type,
            "dimension": self.dimension,
            "index_trained": self.index.is_trained if hasattr(self.index, 'is_trained') else True,
            "persist_dir": self.persist_dir,
            "index_size_mb": os.path.getsize(Path(self.persist_dir) / "index.faiss") / (1024 * 1024) if Path(self.persist_dir).exists() else 0
        }