import yaml, os
from crewai_tools import tool
from .crawler import fetch

@tool("crawl_sources", return_direct=False)
def crawl_sources() -> str:
    """Crawl configured regulation sources and return concatenated texts."""
    cfg_path = os.path.join(os.path.dirname(__file__), "sources.yml")
    cfg = yaml.safe_load(open(cfg_path))
    docs = []
    for s in cfg["sources"]:
        uid, text = fetch(s["url"], s.get("selector","body"))
        docs.append(f"[{uid}] {s['name']} :: {s['url']}\n{text}")
    return "\n\n---DOC---\n\n".join(docs)
