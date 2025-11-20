"""
Script to download and preprocess legal data for LegisAI
Downloads CUAD dataset, processes contracts, and prepares for import
"""
import os
import json
import subprocess
import sys
import zipfile
from pathlib import Path
import requests
from typing import List, Dict, Any

# Setup paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "legal_data"
CUAD_DIR = DATA_DIR / "cuad"
CONTRACTS_DIR = DATA_DIR / "contracts"
CASES_DIR = DATA_DIR / "cases"
REGULATIONS_DIR = DATA_DIR / "regulations"

def setup_directories():
    """Create necessary directories"""
    directories = [
        DATA_DIR,
        CUAD_DIR,
        CONTRACTS_DIR,
        CASES_DIR,
        REGULATIONS_DIR,
        CONTRACTS_DIR / "software_development",
        CONTRACTS_DIR / "employment",
        CONTRACTS_DIR / "nda",
        CONTRACTS_DIR / "licensing",
        CASES_DIR / "us_federal",
        CASES_DIR / "us_state",
        REGULATIONS_DIR
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def download_cuad_dataset():
    """Download CUAD dataset from GitHub"""
    print("\n📥 Downloading CUAD dataset...")
    
    cuad_repo = "https://github.com/TheAtticusProject/cuad.git"
    cuad_data_dir = CUAD_DIR / "cuad"
    
    if cuad_data_dir.exists() and (cuad_data_dir / "data").exists():
        print("✅ CUAD dataset already exists")
        return True
    
    try:
        # Clone the repository
        print(f"Cloning CUAD repository to {cuad_data_dir}...")
        result = subprocess.run(
            ["git", "clone", cuad_repo, str(cuad_data_dir)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("✅ CUAD dataset downloaded successfully")
            return True
        else:
            print(f"❌ Error downloading CUAD: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Download timeout - CUAD repository is large")
        return False
    except FileNotFoundError:
        print("❌ Git not found. Please install Git or download CUAD manually:")
        print(f"   git clone {cuad_repo} {cuad_data_dir}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def extract_cuad_zip():
    """Extract CUAD data.zip if it exists"""
    zip_path = CUAD_DIR / "cuad" / "cuad" / "data.zip"
    extract_to = CUAD_DIR / "cuad" / "cuad" / "data"
    
    if not zip_path.exists():
        print("⚠️  data.zip not found, checking for existing data directory...")
        return False
    
    if extract_to.exists():
        print("✅ CUAD data already extracted")
        return True
    
    print(f"📦 Extracting {zip_path}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("✅ CUAD data extracted successfully")
        return True
    except Exception as e:
        print(f"❌ Error extracting zip: {e}")
        return False

def process_cuad_data():
    """Process CUAD dataset and extract clauses"""
    print("\n🔄 Processing CUAD data...")
    
    # First, try to extract the zip file
    extract_cuad_zip()
    
    # Try different possible paths
    possible_paths = [
        CUAD_DIR / "cuad" / "cuad" / "data",
        CUAD_DIR / "cuad" / "data",
        CUAD_DIR / "cuad" / "CUAD" / "data",
        CUAD_DIR / "data",
        CUAD_DIR / "cuad"
    ]
    
    cuad_data_dir = None
    for path in possible_paths:
        if path.exists():
            # Check if it has JSON files
            json_files = list(path.rglob("*.json"))
            if json_files:
                cuad_data_dir = path
                print(f"✅ Found CUAD data at: {path} ({len(json_files)} JSON files)")
                break
    
    if cuad_data_dir is None:
        print("❌ CUAD data directory not found")
        print(f"   Checked paths: {[str(p) for p in possible_paths]}")
        return []
    
    clauses = []
    files_to_process = [
        "train.json",
        "val.json",
        "test.json"
    ]
    
    # Also search for JSON files in subdirectories
    json_files = list(cuad_data_dir.rglob("*.json"))
    if json_files:
        print(f"Found {len(json_files)} JSON files in CUAD directory")
        # Use all JSON files found
        files_to_process = [f.name for f in json_files if f.name in ["train.json", "val.json", "test.json"]]
        if not files_to_process:
            # Use first few JSON files if standard names not found
            files_to_process = [str(f.relative_to(cuad_data_dir)) for f in json_files[:3]]
    
    for filename in files_to_process:
        file_path = cuad_data_dir / filename if not Path(filename).is_absolute() else Path(filename)
        if not file_path.exists():
            # Try relative path
            file_path = cuad_data_dir / Path(filename).name
            if not file_path.exists():
                print(f"⚠️  {filename} not found, skipping...")
                continue
        
        print(f"Processing {file_path.name}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # CUAD format: dict with 'data' key containing list of contracts
            contracts = []
            if isinstance(data, dict) and 'data' in data:
                contracts = data['data']
            elif isinstance(data, list):
                contracts = data
            elif isinstance(data, dict):
                # Try other possible keys
                if 'contracts' in data:
                    contracts = data['contracts']
                else:
                    contracts = [data]
            
            for idx, contract in enumerate(contracts):
                # CUAD format: contract has 'title' and 'paragraphs'
                contract_title = contract.get('title', '')
                
                # Extract text from paragraphs
                paragraphs = contract.get('paragraphs', [])
                contract_text_parts = []
                
                for para in paragraphs:
                    if isinstance(para, dict):
                        # Paragraph might have 'context' or be the text itself
                        para_text = para.get('context', '') or para.get('text', '') or str(para)
                        if para_text and len(para_text.strip()) > 20:
                            contract_text_parts.append(para_text.strip())
                    elif isinstance(para, str):
                        if len(para.strip()) > 20:
                            contract_text_parts.append(para.strip())
                
                contract_text = ' '.join(contract_text_parts)
                
                # Fallback: try other fields
                if not contract_text or len(contract_text.strip()) < 50:
                    contract_text = contract.get('contract_text', '') or contract.get('text', '') or contract.get('content', '')
                
                if not contract_text or len(contract_text.strip()) < 50:
                    continue
                
                # Determine contract type from title
                contract_type = 'unknown'
                title_lower = contract_title.lower()
                if 'supply' in title_lower or 'purchase' in title_lower:
                    contract_type = 'supply_agreement'
                elif 'employment' in title_lower or 'employee' in title_lower:
                    contract_type = 'employment'
                elif 'nda' in title_lower or 'confidentiality' in title_lower:
                    contract_type = 'nda'
                elif 'license' in title_lower or 'licensing' in title_lower:
                    contract_type = 'licensing'
                elif 'software' in title_lower or 'development' in title_lower:
                    contract_type = 'software_development'
                else:
                    contract_type = contract.get('contract_type', '') or 'general'
                
                # Extract individual clauses - chunk the contract text
                chunk_size = 1500
                chunks = [contract_text[i:i+chunk_size] for i in range(0, len(contract_text), chunk_size)]
                
                for chunk_idx, chunk in enumerate(chunks[:15]):  # Limit to 15 chunks per contract
                    if len(chunk.strip()) < 50:
                        continue
                    clause_data = {
                        "clause_id": f"cuad_{file_path.name.replace('.json', '')}_{len(clauses)}",
                        "clause_text": chunk.strip(),
                        "contract_type": contract_type,
                        "source": "CUAD",
                        "metadata": {
                            "dataset": file_path.name.replace('.json', ''),
                            "contract_index": idx,
                            "contract_title": contract_title[:100],
                            "chunk_index": chunk_idx,
                            "original_length": len(contract_text)
                        }
                    }
                    clauses.append(clause_data)
            
            print(f"  ✅ Processed {len([c for c in clauses if c['metadata']['dataset'] == file_path.name.replace('.json', '')])} clauses from {file_path.name}")
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON decode error in {file_path.name}: {e}")
        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
    
    return clauses

def download_gdpr():
    """Download GDPR regulation text"""
    print("\n📥 Downloading GDPR text...")
    
    gdpr_file = REGULATIONS_DIR / "gdpr.txt"
    
    if gdpr_file.exists():
        print("✅ GDPR already downloaded")
        return True
    
    try:
        # GDPR full text from official source
        url = "https://gdpr-info.eu/art-1-gdpr/"
        # For now, we'll create a placeholder
        # In production, you'd scrape or use an API
        
        gdpr_text = """
        REGULATION (EU) 2016/679 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL
        of 27 April 2016
        on the protection of natural persons with regard to the processing of personal data
        and on the free movement of such data, and repealing Directive 95/46/EC
        (General Data Protection Regulation)
        
        [Full GDPR text would be downloaded here]
        """
        
        with open(gdpr_file, 'w', encoding='utf-8') as f:
            f.write(gdpr_text)
        
        print("✅ GDPR text saved (placeholder - full text needs manual download)")
        print("   Download from: https://gdpr-info.eu/")
        return True
    except Exception as e:
        print(f"❌ Error downloading GDPR: {e}")
        return False

def download_ccpa():
    """Download CCPA regulation text"""
    print("\n📥 Downloading CCPA text...")
    
    ccpa_file = REGULATIONS_DIR / "ccpa.txt"
    
    if ccpa_file.exists():
        print("✅ CCPA already downloaded")
        return True
    
    try:
        ccpa_text = """
        CALIFORNIA CONSUMER PRIVACY ACT (CCPA)
        
        [Full CCPA text would be downloaded here]
        Download from: https://oag.ca.gov/privacy/ccpa
        """
        
        with open(ccpa_file, 'w', encoding='utf-8') as f:
            f.write(ccpa_text)
        
        print("✅ CCPA text saved (placeholder - full text needs manual download)")
        print("   Download from: https://oag.ca.gov/privacy/ccpa")
        return True
    except Exception as e:
        print(f"❌ Error downloading CCPA: {e}")
        return False

def save_clauses_for_import(clauses: List[Dict[str, Any]]):
    """Save processed clauses in format ready for import"""
    print("\n💾 Saving clauses for import...")
    
    # Save as JSON for easy import
    output_file = DATA_DIR / "clauses_processed.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clauses, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(clauses)} clauses to {output_file}")
    
    # Also save individual files by contract type
    by_type = {}
    for clause in clauses:
        contract_type = clause.get('contract_type', 'other')
        if contract_type not in by_type:
            by_type[contract_type] = []
        by_type[contract_type].append(clause)
    
    for contract_type, type_clauses in by_type.items():
        type_dir = CONTRACTS_DIR / contract_type.lower().replace(' ', '_')
        type_dir.mkdir(exist_ok=True)
        
        type_file = type_dir / "clauses.json"
        with open(type_file, 'w', encoding='utf-8') as f:
            json.dump(type_clauses, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Saved {len(type_clauses)} {contract_type} clauses")
    
    return output_file

def create_import_script():
    """Create a script to import the data into LegisAI"""
    print("\n📝 Creating import script...")
    
    import_script = DATA_DIR / "import_to_legisai.py"
    
    script_content = f"""
\"\"\"
Import processed legal data into LegisAI
Run this after downloading and processing data
\"\"\"
import sys
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from services.vector_store import VectorStore

def import_clauses():
    \"\"\"Import processed clauses into vector store\"\"\"
    data_dir = Path(__file__).parent
    clauses_file = data_dir / "clauses_processed.json"
    
    if not clauses_file.exists():
        print("❌ clauses_processed.json not found")
        return
    
    print("📥 Loading clauses...")
    with open(clauses_file, 'r', encoding='utf-8') as f:
        clauses = json.load(f)
    
    print(f"📊 Found {{len(clauses)}} clauses")
    
    # Initialize vector store
    print("🔧 Initializing vector store...")
    vector_store = VectorStore()
    
    # Prepare documents for import
    documents = []
    metadata_list = []
    
    for clause in clauses:
        documents.append(clause['clause_text'])
        metadata_list.append({{
            "type": "contract_clause",
            "contract_type": clause.get('contract_type', 'unknown'),
            "source": clause.get('source', 'unknown'),
            "clause_id": clause.get('clause_id', ''),
            **clause.get('metadata', {{}})
        }})
    
    # Import in batches
    print("📤 Importing clauses into vector store...")
    batch_size = 100
    total_batches = (len(documents) + batch_size - 1) // batch_size
    
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_metadata = metadata_list[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"  Importing batch {{batch_num}}/{{total_batches}}...")
        vector_store.add_documents(batch_docs, batch_metadata, batch_size=50)
    
    print(f"✅ Successfully imported {{len(documents)}} clauses!")
    print(f"📊 Vector store now has {{vector_store.get_document_count()}} documents")

if __name__ == "__main__":
    import_clauses()
"""
    
    with open(import_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Import script created: {import_script}")
    print("   Run with: python legal_data/import_to_legisai.py")

def main():
    """Main function to download and process legal data"""
    print("="*70)
    print("📚 LEGISAI LEGAL DATA DOWNLOADER & PREPROCESSOR")
    print("="*70)
    
    # Setup
    setup_directories()
    
    # Download CUAD dataset
    if download_cuad_dataset():
        # Process CUAD data
        clauses = process_cuad_data()
        
        if clauses:
            # Save processed clauses
            save_clauses_for_import(clauses)
            
            # Create import script
            create_import_script()
            
            print("\n" + "="*70)
            print("✅ DATA DOWNLOAD & PREPROCESSING COMPLETE!")
            print("="*70)
            print(f"\n📊 Summary:")
            print(f"  • Clauses processed: {len(clauses)}")
            print(f"  • Data location: {DATA_DIR}")
            print(f"\n🚀 Next Steps:")
            print(f"  1. Review the processed data in: {DATA_DIR / 'clauses_processed.json'}")
            print(f"  2. Run import script: python {DATA_DIR / 'import_to_legisai.py'}")
            print(f"  3. Or use the bulk import API endpoint")
        else:
            print("\n⚠️  No clauses processed. Check CUAD data directory.")
    else:
        print("\n⚠️  CUAD download failed. You can:")
        print("  1. Download manually: git clone https://github.com/TheAtticusProject/cuad.git")
        print("  2. Place it in: legal_data/cuad/cuad/")
        print("  3. Run this script again")
    
    # Download regulations (placeholders)
    download_gdpr()
    download_ccpa()
    
    print("\n💡 Note: GDPR and CCPA are placeholders.")
    print("   Download full text manually from:")
    print("   - GDPR: https://gdpr-info.eu/")
    print("   - CCPA: https://oag.ca.gov/privacy/ccpa")

if __name__ == "__main__":
    main()

