import os
import json
import networkx as nx
import re

# 1. Init Graph
G = nx.DiGraph()

# 2. Parse Cases
cases_folder = "D:/AIP/data/"  # Change this path to your folder if needed

# Regular expression patterns for statute references
statute_patterns = [
    r'\b\d+\sU\.S\.C\.\s§+\s?\d+[a-zA-Z\-]*\b',   # Matches '42 U.S.C. § 1983'
    r'\bSection\s\d+[a-zA-Z\-]*\b',               # Matches 'Section 1983'
    # Add more patterns here if needed
]

for filename in os.listdir(cases_folder):
    if filename.endswith('.json'):
        with open(os.path.join(cases_folder, filename), 'r', encoding='utf-8') as f:
            case = json.load(f)
        case_name = case.get('name', filename)
        G.add_node(case_name, type='case')

        # Extract main case text
        casebody = case.get("casebody", {})
        opinions = casebody.get("opinions", [])
        case_text = opinions[0].get("text", "") if opinions and isinstance(opinions[0], dict) else ""

        # 3. Statute Extraction (Regex)
        statutes_found = []
        for pattern in statute_patterns:
            statutes_found += re.findall(pattern, case_text)

        for statute in set(statutes_found):
            G.add_node(statute, type="statute")
            G.add_edge(case_name, statute, relation="references")

        # 4. Case Citation Extraction (Existing Logic)
        cited_cases = re.findall(r"\b([A-Z][a-zA-Z]+ v\. [A-Z][a-zA-Z]+)\b", case_text)
        for cited in cited_cases:
            G.add_node(cited, type='case')
            G.add_edge(case_name, cited, relation='cites')

# 5. Analyze Influential Cases
page_ranks = nx.pagerank(G)
top_cases = sorted(page_ranks.items(), key=lambda x: x[1], reverse=True)[:10]
print("Most influential cases:", [case for case, rank in top_cases])

# 6. Statutes referenced (Sample Output)
statute_nodes = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'statute']
print("Statutes referenced:", statute_nodes)

# 7. Visualization (optional—matplotlib, pyvis)
# nx.draw(G, with_labels=True)
