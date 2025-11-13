import os
import json
import networkx as nx
import re

# 1. Init Graph
G = nx.DiGraph()

# 2. Patterns for Extraction
case_pattern = r"\b([A-Z][a-zA-Z]+ v\. [A-Z][a-zA-Z]+)\b"
statute_patterns = [
    r'\b\d+\sU\.S\.C\.\s§+\s?\d+[a-zA-Z\-]*\b',
    r'\bSection\s\d+[a-zA-Z\-]*\b',
]

# (Optional) clause pattern, e.g., "Clause 12" (customize for your documents)
clause_pattern = r"\bClause\s\d+[a-zA-Z\-]*\b"

# 3. Parse Cases
cases_folder = "D:/AIP/data/"  # Update path if needed

for filename in os.listdir(cases_folder):
    if filename.endswith('.json'):
        with open(os.path.join(cases_folder, filename), 'r', encoding='utf-8') as f:
            case = json.load(f)
        case_name = case.get('name', filename)
        G.add_node(case_name, type='case')

        # Extract case text
        casebody = case.get("casebody", {})
        opinions = casebody.get("opinions", [])
        case_text = opinions[0].get("text", "") if opinions and isinstance(opinions[0], dict) else ""

        # a. Citation Extraction
        cited_cases = re.findall(case_pattern, case_text)
        for cited in set(cited_cases):
            G.add_node(cited, type='case')
            G.add_edge(case_name, cited, relation='cites')
        
        # b. Statute Extraction
        statutes_found = []
        for pattern in statute_patterns:
            statutes_found += re.findall(pattern, case_text)
        for statute in set(statutes_found):
            G.add_node(statute, type="statute")
            G.add_edge(case_name, statute, relation="references")
        
        # c. Clause Extraction (optional)
        clauses_found = re.findall(clause_pattern, case_text)
        for clause in set(clauses_found):
            G.add_node(clause, type="clause")
            G.add_edge(case_name, clause, relation="includes_clause")

# 4. Highlight Most Influential / Cited Cases
page_ranks = nx.pagerank(G)
top_cases = sorted(page_ranks.items(), key=lambda x: x[1], reverse=True)[:10]
print("Most influential cases (PageRank):", [case for case, rank in top_cases])

# Or: Most cited cases by count
cited_case_counts = {}
for _, cited, attr in G.edges(data=True):
    if attr.get("relation") == "cites":
        cited_case_counts[cited] = cited_case_counts.get(cited, 0) + 1

top_cited_cases = sorted(cited_case_counts.items(), key=lambda x: x[1], reverse=True)[:10]
print("Most cited cases (by count):", [case for case, count in top_cited_cases])

# Optional: List all statutes and clauses found
print("Statutes referenced:", [n for n, a in G.nodes(data=True) if a.get("type") == "statute"])
print("Clauses included:", [n for n, a in G.nodes(data=True) if a.get("type") == "clause"])
