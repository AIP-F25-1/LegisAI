"""
Download case law from CourtListener API
Uses the user's API token
"""
import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Setup paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "legal_data"
CASES_DIR = DATA_DIR / "cases"
US_FEDERAL_DIR = CASES_DIR / "us_federal"
US_STATE_DIR = CASES_DIR / "us_state"

# API Configuration
COURTLISTENER_API_BASE = "https://www.courtlistener.com/api/rest/v4"
API_TOKEN = "3558be5dcf356c1ae3edc13061471f67615ef367"  # User's API token

def setup_directories():
    """Create necessary directories"""
    directories = [
        CASES_DIR,
        US_FEDERAL_DIR,
        US_STATE_DIR
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("[OK] Directories created")

def download_cases_from_courtlistener(
    max_cases: int = 5000,
    court_type: str = None,
    search_query: str = None
):
    """
    Download cases from CourtListener API
    
    Args:
        max_cases: Maximum number of cases to download
        court_type: Filter by court type (optional)
        search_query: Search query (optional)
    """
    print(f"\nDownloading cases from CourtListener API...")
    print(f"   Max cases: {max_cases}")
    
    cases = []
    page = 1
    # Use search endpoint for opinions
    url = f"{COURTLISTENER_API_BASE}/search/"
    
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # CourtListener search parameters
    params = {
        "type": "o",  # 'o' for opinions/orders
        "ordering": "-date_filed",  # Most recent first
        "page_size": 100  # Max per page
    }
    
    if search_query:
        params["q"] = search_query
    if court_type:
        params["court"] = court_type
    
    try:
        while len(cases) < max_cases:
            params["page"] = page
            print(f"  Fetching page {page}...")
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 401:
                print("[ERROR] Authentication failed!")
                print("   Check your API token")
                break
            
            if response.status_code == 403:
                print("[ERROR] Access forbidden!")
                print("   Check your API token permissions")
                break
            
            if response.status_code != 200:
                print(f"[ERROR] API error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                break
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                print("  No more cases found")
                break
            
            for result in results:
                # Extract case information
                case_data = {
                    "case_id": result.get("id", ""),
                    "case_name": result.get("caseName", "") or result.get("title", ""),
                    "court": result.get("court", ""),
                    "court_name": result.get("court_name", ""),
                    "jurisdiction": result.get("jurisdiction", ""),
                    "date": result.get("date_filed", "") or result.get("dateFiled", ""),
                    "citation": result.get("citation", ""),
                    "opinion_text": result.get("plain_text", "") or result.get("html", "") or result.get("html_with_citations", ""),
                    "topics": result.get("topics", []),
                    "source": "CourtListener"
                }
                
                # Only add if we have opinion text
                if case_data["opinion_text"] and len(case_data["opinion_text"].strip()) > 200:
                    cases.append(case_data)
            
            print(f"  [OK] Downloaded {len(cases)} cases so far...")
            
            # Check if there are more pages
            if not data.get("next"):
                break
            
            page += 1
            time.sleep(0.5)  # Rate limiting (respect API limits)
            
            if len(cases) >= max_cases:
                break
        
        print(f"[OK] Downloaded {len(cases)} cases")
        return cases[:max_cases]
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_cases(cases: List[Dict[str, Any]], filename: str = "cases_courtlistener.json"):
    """Save cases to JSON file"""
    if not cases:
        print("[WARNING] No cases to save")
        return
    
    output_file = CASES_DIR / filename
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Saved {len(cases)} cases to {output_file}")
    return output_file

def test_api_connection():
    """Test API connection"""
    print("Testing CourtListener API connection...")
    
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test with OPTIONS request (as shown in user's example)
    try:
        response = requests.options(
            f"{COURTLISTENER_API_BASE}/dockets/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200 or response.status_code == 204:
            print("[OK] API connection successful!")
            return True
        elif response.status_code == 401:
            print("[ERROR] Authentication failed!")
            print("   Check your API token")
            return False
        else:
            print(f"[WARNING] Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return True  # Might still work with GET requests
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
        return False

def main():
    """Download case law from CourtListener"""
    import sys
    import io
    # Fix Windows encoding issues
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("="*70)
    print("COURTLISTENER CASE LAW DOWNLOADER")
    print("="*70)
    
    # Test API connection first
    if not test_api_connection():
        print("\n[ERROR] API connection failed. Please check your token.")
        return
    
    setup_directories()
    
    # Download contract-related cases
    print("\nDownloading contract-related cases...")
    contract_cases = download_cases_from_courtlistener(
        max_cases=1000,
        search_query="contract"
    )
    
    if contract_cases:
        save_cases(contract_cases, "cases_contracts.json")
    
    # Download employment-related cases
    print("\nDownloading employment-related cases...")
    employment_cases = download_cases_from_courtlistener(
        max_cases=1000,
        search_query="employment"
    )
    
    if employment_cases:
        save_cases(employment_cases, "cases_employment.json")
    
    # Download general recent cases
    print("\nDownloading recent cases...")
    recent_cases = download_cases_from_courtlistener(
        max_cases=1000
    )
    
    if recent_cases:
        save_cases(recent_cases, "cases_recent.json")
    
    # Summary
    total_cases = len(contract_cases) + len(employment_cases) + len(recent_cases)
    
    print("\n" + "="*70)
    print("[OK] DOWNLOAD COMPLETE!")
    print("="*70)
    print(f"\nSummary:")
    print(f"  - Contract cases: {len(contract_cases)}")
    print(f"  - Employment cases: {len(employment_cases)}")
    print(f"  - Recent cases: {len(recent_cases)}")
    print(f"  - Total: {total_cases} cases")
    print(f"\nNext Steps:")
    print(f"  1. Review the downloaded cases")
    print(f"  2. Run: python scripts/import_all_data.py")
    print(f"  3. Cases will be imported into vector store")

if __name__ == "__main__":
    main()

