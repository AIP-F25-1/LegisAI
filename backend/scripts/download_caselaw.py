"""
Script to download case law from Caselaw Access Project API
"""
import os
import json
import requests
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
CASE_LAW_API_BASE = "https://api.case.law/v1"
# Note: API requires registration for bulk access
# Free tier: 10,000 requests/day
# Register at: https://case.law/api/

def setup_directories():
    """Create necessary directories"""
    directories = [
        CASES_DIR,
        US_FEDERAL_DIR,
        US_STATE_DIR
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def download_cases_from_api(
    jurisdiction: str = "us",
    page_size: int = 100,
    max_cases: int = 1000,
    search_query: str = None
):
    """
    Download cases from Caselaw Access Project API
    
    Args:
        jurisdiction: "us" for federal, state code for state courts
        page_size: Number of cases per page (max 100)
        max_cases: Maximum number of cases to download
        search_query: Optional search query
    """
    print(f"\n📥 Downloading cases from Caselaw Access Project...")
    print(f"   Jurisdiction: {jurisdiction}")
    print(f"   Max cases: {max_cases}")
    
    cases = []
    page = 1
    url = f"{CASE_LAW_API_BASE}/cases/"
    
    params = {
        "jurisdiction": jurisdiction,
        "page_size": min(page_size, 100),
        "ordering": "-decision_date"  # Most recent first
    }
    
    if search_query:
        params["search"] = search_query
    
    # Note: API requires authentication token for bulk access
    # For now, this is a template - you'll need to add your API key
    headers = {
        "Authorization": "Token YOUR_API_KEY_HERE"  # Replace with actual key
    }
    
    try:
        while len(cases) < max_cases:
            params["page"] = page
            print(f"  Fetching page {page}...")
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 401:
                print("❌ Authentication required!")
                print("   Register at: https://case.law/api/")
                print("   Add your API key to this script")
                break
            
            if response.status_code != 200:
                print(f"❌ API error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                break
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                print("  No more cases found")
                break
            
            for case in results:
                case_data = {
                    "case_id": case.get("id", ""),
                    "case_name": case.get("name", ""),
                    "court": case.get("court", {}).get("name", ""),
                    "jurisdiction": case.get("jurisdiction", {}).get("name_long", ""),
                    "date": case.get("decision_date", ""),
                    "citation": case.get("citations", [{}])[0].get("cite", "") if case.get("citations") else "",
                    "opinion_text": case.get("casebody", {}).get("data", {}).get("opinions", [{}])[0].get("text", "") if case.get("casebody", {}).get("data", {}).get("opinions") else "",
                    "topics": [],  # Would need additional processing
                    "source": "Caselaw Access Project"
                }
                cases.append(case_data)
            
            print(f"  ✅ Downloaded {len(cases)} cases so far...")
            
            # Check if there are more pages
            if not data.get("next"):
                break
            
            page += 1
            time.sleep(0.5)  # Rate limiting
            
            if len(cases) >= max_cases:
                break
        
        print(f"✅ Downloaded {len(cases)} cases")
        return cases[:max_cases]
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def save_cases(cases: List[Dict[str, Any]], jurisdiction: str):
    """Save cases to JSON file"""
    if not cases:
        print("⚠️  No cases to save")
        return
    
    output_file = CASES_DIR / f"cases_{jurisdiction}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(cases)} cases to {output_file}")

def main():
    """Main function"""
    print("="*70)
    print("⚖️  CASELAW ACCESS PROJECT DOWNLOADER")
    print("="*70)
    
    print("\n⚠️  NOTE: This script requires API authentication")
    print("   1. Register at: https://case.law/api/")
    print("   2. Get your API key")
    print("   3. Update the 'YOUR_API_KEY_HERE' in this script")
    print("   4. Run again")
    
    setup_directories()
    
    # Example: Download contract-related cases
    print("\n💡 To download cases:")
    print("   1. Get API key from https://case.law/api/")
    print("   2. Update headers in this script")
    print("   3. Run: python download_caselaw.py")
    print("\n   Or use the web interface: https://case.law/")

if __name__ == "__main__":
    main()

