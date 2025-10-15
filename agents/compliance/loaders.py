import os, glob
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

load_dotenv()

def build_domain_index(chroma_dir: str, rules_dir: str):
    paths = glob.glob(os.path.join(rules_dir, "**/*.*"), recursive=True)
    docs = []
    for p in paths:
        try:
            docs += TextLoader(p, encoding="utf-8").load()
        except Exception:
            pass
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBED_MODEL"))
    vs = Chroma.from_documents(chunks, embedding=embeddings, persist_directory=chroma_dir)
    vs.persist()
    return True
