
"""
Import processed legal data into LegisAI
Run this after downloading and processing data
"""
import sys
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.vector_store import VectorStore

def import_clauses():
    """Import processed clauses into vector store"""
    data_dir = Path(__file__).parent
    clauses_file = data_dir / "clauses_processed.json"
    
    if not clauses_file.exists():
        print("❌ clauses_processed.json not found")
        return
    
    print("📥 Loading clauses...")
    with open(clauses_file, 'r', encoding='utf-8') as f:
        clauses = json.load(f)
    
    print(f"📊 Found {len(clauses)} clauses")
    
    # Initialize vector store
    print("🔧 Initializing vector store...")
    vector_store = VectorStore()
    
    # Prepare documents for import
    documents = []
    metadata_list = []
    
    for clause in clauses:
        documents.append(clause['clause_text'])
        metadata_list.append({
            "type": "contract_clause",
            "contract_type": clause.get('contract_type', 'unknown'),
            "source": clause.get('source', 'unknown'),
            "clause_id": clause.get('clause_id', ''),
            **clause.get('metadata', {})
        })
    
    # Import in batches
    print("📤 Importing clauses into vector store...")
    batch_size = 100
    total_batches = (len(documents) + batch_size - 1) // batch_size
    
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_metadata = metadata_list[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"  Importing batch {batch_num}/{total_batches}...")
        vector_store.add_documents(batch_docs, batch_metadata, batch_size=50)
    
    print(f"✅ Successfully imported {len(documents)} clauses!")
    print(f"📊 Vector store now has {vector_store.get_document_count()} documents")

if __name__ == "__main__":
    import_clauses()
