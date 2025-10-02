import os
import re
import json


# Patterns for precedent relationship detection
SUPPORT_PATTERNS = [
    r"\bas held in\b", r"\bfollows\b", r"\bconfirms\b", r"\bin accordance with\b"
]
DISTINGUISH_PATTERNS = [
    r"\bdistinguished in\b", r"\bunlike the facts\b", r"\bcontrary to\b"
]
OVERRULED_PATTERNS = [
    r"\boverruled by\b", r"\bno longer good law\b"
]

def scan_precedent_relations(text):
    support = []
    distinguish = []
    overruled = []
    for line in text.split('\n'):
        for p in SUPPORT_PATTERNS:
            if re.search(p, line, re.IGNORECASE):
                support.append(line)
        for p in DISTINGUISH_PATTERNS:
            if re.search(p, line, re.IGNORECASE):
                distinguish.append(line)
        for p in OVERRULED_PATTERNS:
            if re.search(p, line, re.IGNORECASE):
                overruled.append(line)
    return support, distinguish, overruled

# --- Multi-Case Reasoning ---
cases_folder = "D:/AIP/data/"
for filename in os.listdir(cases_folder):
    if filename.endswith('.json'):
        with open(os.path.join(cases_folder, filename), 'r', encoding='utf-8') as f:
            case = json.load(f)
        casebody = case.get("casebody", {})
        opinions = casebody.get("opinions", [])
        case_text = opinions[0].get("text", "") if opinions and isinstance(opinions[0], dict) else ""
        if not case_text or len(case_text) < 20:
            continue
        print(f"\n=== {filename} ===")
        support, distinguish, overruled = scan_precedent_relations(case_text)
        print("--- Supportive Citations ---")
        for line in support: print(line)
        print("--- Distinguishing/Contrary ---")
        for line in distinguish: print(line)
        print("--- Overruled/Outdated ---")
        for line in overruled: print(line)