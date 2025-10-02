import os
import json
import networkx as nx
import re

# 1. Init Graph
G = nx.DiGraph()

# 2. Parse Cases
cases_folder = "D:/AIP/data/"
for filename in os.listdir(cases_folder):
    if filename.endswith('.json'):
        with open(os.path.join(cases_folder, filename), 'r', encoding='utf-8') as f:
            case = json.load(f)
        case_name = case.get('name', filename)
        G.add_node(case_name, type='case')

        # Extract citations (regex, NLP can be expanded)
        casebody = case.get("casebody", {})
        opinions = casebody.get("opinions", [])
        case_text = opinions[0].get("text", "") if opinions and isinstance(opinions[0], dict) else ""
        # Simple regex for 'cited in X v. Y'
        cited_cases = re.findall(r"\b([A-Z][a-zA-Z]+ v\. [A-Z][a-zA-Z]+)\b", case_text)
        for cited in cited_cases:
            G.add_node(cited, type='case')
            G.add_edge(case_name, cited, relation='cites')

        # TODO: Statute extraction
        # statutes = ... # NLP/statute matching logic

# 3. Analyze Influential Cases
page_ranks = nx.pagerank(G)
top_cases = sorted(page_ranks.items(), key=lambda x: x[1], reverse=True)[:10]
print("Most influential cases:", [case for case, rank in top_cases])

# 4. Visualization (optional—matplotlib, pyvis)
# nx.draw(G, with_labels=True)
