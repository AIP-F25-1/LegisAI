import os, re
from crewai_tools import tool
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

def _vs():
    return Chroma(
        persist_directory=os.getenv("CHROMA_DIR","./vectorstore"),
        embedding_function=HuggingFaceEmbeddings(model_name=os.getenv("EMBED_MODEL"))
    )

@tool("retrieve_rules", return_direct=False)
def retrieve_rules(query: str, k: int = 6) -> str:
    """Search domain packs and return top chunks with sources."""
    res = _vs().similarity_search_with_score(query, k=k)
    out = []
    for doc, score in res:
        out.append(f"[{score:.4f}] {doc.page_content}\nSRC: {doc.metadata.get('source','?')}")
    return "\n\n".join(out)

@tool("extract_clauses", return_direct=False)
def extract_clauses(contract_text: str) -> str:
    """Simple clause segmentation (baseline)."""
    clauses = re.split(r"\n\s*(?:Section|Clause)?\s*\d+[\.:]\s*", contract_text)
    clauses = [c.strip() for c in clauses if c.strip()]
    return "\n\n---CLAUSE---\n\n".join(clauses[:80])
