"""
Import all legal data (regulations, cases if available) into vector store
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.vector_store import VectorStore
from services.hybrid_retriever import HybridRetriever
import json

def import_regulations():
    """Import regulations from files"""
    print("\n📥 Importing Regulations...")
    
    data_dir = Path(__file__).parent.parent / "legal_data"
    regulations_dir = data_dir / "regulations"
    
    if not regulations_dir.exists():
        print("  ⚠️  Regulations directory not found")
        return []
    
    vs = VectorStore()
    documents = []
    metadata_list = []
    
    # GDPR
    gdpr_file = regulations_dir / "gdpr.txt"
    if gdpr_file.exists():
        with open(gdpr_file, 'r', encoding='utf-8') as f:
            gdpr_text = f.read()
        if len(gdpr_text.strip()) > 100:
            # Split into chunks
            chunk_size = 2000
            chunks = [gdpr_text[i:i+chunk_size] for i in range(0, len(gdpr_text), chunk_size)]
            for chunk in chunks:
                if len(chunk.strip()) > 100:
                    documents.append(chunk)
                    metadata_list.append({
                        "type": "regulation",
                        "regulation_type": "GDPR",
                        "source": "EU Regulation 2016/679",
                        "jurisdiction": "EU"
                    })
            print(f"  ✅ Added {len(chunks)} GDPR chunks")
    
    # CCPA
    ccpa_file = regulations_dir / "ccpa.txt"
    if ccpa_file.exists():
        with open(ccpa_file, 'r', encoding='utf-8') as f:
            ccpa_text = f.read()
        if len(ccpa_text.strip()) > 100:
            chunk_size = 2000
            chunks = [ccpa_text[i:i+chunk_size] for i in range(0, len(ccpa_text), chunk_size)]
            for chunk in chunks:
                if len(chunk.strip()) > 100:
                    documents.append(chunk)
                    metadata_list.append({
                        "type": "regulation",
                        "regulation_type": "CCPA",
                        "source": "California Civil Code",
                        "jurisdiction": "US-CA"
                    })
            print(f"  ✅ Added {len(chunks)} CCPA chunks")
    
    # US Code
    us_code_dir = regulations_dir / "us_code"
    if us_code_dir.exists():
        for code_file in us_code_dir.glob("*.txt"):
            with open(code_file, 'r', encoding='utf-8') as f:
                code_text = f.read()
            if len(code_text.strip()) > 100:
                documents.append(code_text)
                metadata_list.append({
                    "type": "regulation",
                    "regulation_type": "US Code",
                    "source": code_file.stem,
                    "jurisdiction": "US"
                })
        print(f"  ✅ Added {len(list(us_code_dir.glob('*.txt')))} US Code sections")
    
    if documents:
        print(f"\n  📤 Importing {len(documents)} regulation chunks into vector store...")
        vs.add_documents(documents, metadata_list, batch_size=50)
        vs.save()
        print(f"  ✅ Regulations imported!")
        return len(documents)
    else:
        print("  ⚠️  No regulations to import")
        return 0

def import_cases():
    """Import case law if available"""
    print("\n⚖️  Importing Case Law...")
    
    data_dir = Path(__file__).parent.parent / "legal_data"
    cases_dir = data_dir / "cases"
    
    if not cases_dir.exists():
        print("  ⚠️  Cases directory not found")
        return 0
    
    # Look for JSON files with cases
    case_files = list(cases_dir.rglob("*.json"))
    
    if not case_files:
        print("  ⚠️  No case law files found")
        print("     Use download_caselaw.py to download cases (requires API key)")
        return 0
    
    vs = VectorStore()
    documents = []
    metadata_list = []
    
    for case_file in case_files:
        try:
            with open(case_file, 'r', encoding='utf-8') as f:
                cases = json.load(f)
            
            if isinstance(cases, list):
                for case in cases:
                    opinion_text = case.get('opinion_text', '') or case.get('text', '')
                    if opinion_text and len(opinion_text.strip()) > 200:
                        documents.append(opinion_text)
                        metadata_list.append({
                            "type": "case_law",
                            "case_name": case.get('case_name', ''),
                            "court": case.get('court', ''),
                            "jurisdiction": case.get('jurisdiction', ''),
                            "date": case.get('date', ''),
                            "citation": case.get('citation', ''),
                            "source": case.get('source', 'Caselaw Access Project')
                        })
        except Exception as e:
            print(f"  ⚠️  Error processing {case_file.name}: {e}")
    
    if documents:
        print(f"  📤 Importing {len(documents)} cases into vector store...")
        vs.add_documents(documents, metadata_list, batch_size=50)
        vs.save()
        print(f"  ✅ Cases imported!")
        return len(documents)
    else:
        print("  ⚠️  No cases to import")
        return 0

def update_hybrid_index():
    """Update BM25 index after importing new data"""
    print("\n🔄 Updating Hybrid Search Index...")
    
    try:
        from services.vector_store import VectorStore
        from services.hybrid_retriever import HybridRetriever
        
        vs = VectorStore()
        hr = HybridRetriever(vs)
        
        # Get all documents
        all_docs = []
        for i in range(vs.get_document_count()):
            doc = vs.get_document(i)
            if doc:
                all_docs.append(doc)
        
        # Re-index
        hr.index_documents(all_docs)
        print(f"  ✅ BM25 index updated with {len(all_docs)} documents")
        return True
    except Exception as e:
        print(f"  ❌ Error updating index: {e}")
        return False

def main():
    """Import all available data"""
    print("="*70)
    print("📚 IMPORT ALL LEGAL DATA")
    print("="*70)
    
    reg_count = import_regulations()
    case_count = import_cases()
    update_hybrid_index()
    
    print("\n" + "="*70)
    print("✅ IMPORT COMPLETE!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"  • Regulations imported: {reg_count} chunks")
    print(f"  • Cases imported: {case_count}")
    print(f"  • Hybrid search index: Updated")
    
    from services.vector_store import VectorStore
    vs = VectorStore()
    print(f"\n📈 Total documents in vector store: {vs.get_document_count()}")

if __name__ == "__main__":
    main()

