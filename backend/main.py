import os
import math
import random
import uuid
from pathlib import Path
from typing import List, Dict, Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from PyPDF2 import PdfReader
import docx2txt

# ---- LLM (LangChain OpenAI-compatible) ----
try:
    from langchain_openai import ChatOpenAI
except Exception:
    from langchain.chat_models import ChatOpenAI

# ---------- ENV / CONFIG ----------
ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR.parent / "ComplianceCrew_StepByStep" / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "llama3.1:8b-instruct")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2048"))

OUTPUT_DIR = ROOT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------- LLM ----------
llm = ChatOpenAI(
    base_url=OPENAI_BASE_URL,
    api_key=OPENAI_API_KEY,
    model=OPENAI_MODEL,
    temperature=OPENAI_TEMPERATURE,
    max_tokens=OPENAI_MAX_TOKENS,
)

def llm_complete(system_prompt: str, user_prompt: str) -> str:
    try:
        res = llm.invoke(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        return getattr(res, "content", str(res))
    except Exception as e:
        return f"[LLM error: {e}]"

# ---------- Utils ----------
def estimate_confidence(text: str) -> float:
    if not text:
        return 0.0
    lowered = text.lower()
    hedges = ["might", "may", "possibly", "unclear", "not sure", "cannot determine", "ambiguous"]
    certs = ["must", "shall", "clearly", "definitely", "is required", "complies", "non-compliant"]
    score = 0.5
    for h in hedges:
        if h in lowered:
            score -= 0.05
    for c in certs:
        if c in lowered:
            score += 0.05
    return max(0.0, min(1.0, score))

def extract_text_from_file(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join([p.extract_text() or "" for p in reader.pages])
    if ext == ".docx":
        return docx2txt.process(str(path)) or ""
    if ext in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError("Unsupported file type, use PDF/DOCX/TXT")

RISK_KEYWORDS = {
    "liability": 2.0,
    "indemnify": 2.5,
    "indemnification": 2.5,
    "penalty": 1.5,
    "termination": 1.8,
    "default": 2.2,
    "breach": 2.0,
    "confidentiality": 1.2,
    "data protection": 2.0,
    "gdpr": 2.0,
    "ccpa": 2.0,
    "hipaa": 2.0,
    "warranty": 1.2,
    "limitation of liability": 2.3,
    "force majeure": 1.0,
    "governing law": 0.8,
    "arbitration": 1.0,
}

def keyword_risk_scan(text: str):
    lowered = text.lower()
    hits, total = {}, 0.0
    for k, w in RISK_KEYWORDS.items():
        c = lowered.count(k)
        if c > 0:
            hits[k] = {"count": c, "weight": w, "weighted": c * w}
            total += c * w
    normalized = 1 - math.exp(-0.1 * total)
    return hits, total, normalized

def monte_carlo_risk(base_risk: float, n: int = 2000):
    rng = random.Random(42)
    incidents = []
    for _ in range(n):
        p = max(0.0, min(1.0, rng.gauss(mu=base_risk, sigma=0.1)))
        incidents.append(1 if rng.random() < p else 0)
    incident_rate = sum(incidents) / n
    return incident_rate

# ---------- FastAPI models ----------
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    confidence: float
    routed_to_human: bool

class ContractResponse(BaseModel):
    file_name: str
    output_type: str
    summary: str
    risk_score: float
    incident_rate: float
    confidence: float
    status: str  # "completed" | "needs_review"

# ---------- FastAPI app ----------
app = FastAPI(title="Legal AI Backend")

# CORS so your React frontend can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHAT_SYSTEM = (
    "You are an AI legal assistant. Answer legal and contract questions in a concise, "
    "non-binding way. Highlight risks and suggest safer alternatives."
)

DOC_SYSTEM = (
    "You are a contract analysis expert. Summarize contracts, identify key obligations, "
    "data protection aspects, risks, and suggest short, concrete clause improvements."
)

# ---------- Endpoints ----------

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    answer = llm_complete(CHAT_SYSTEM, req.message)
    confidence = estimate_confidence(answer)
    routed_to_human = confidence < 0.60
    if routed_to_human:
        answer = (
            answer.strip()
            + f"\n\n— Confidence {confidence*100:.0f}% is below threshold. Redirecting to human agent..."
        )

    return ChatResponse(
        answer=answer,
        confidence=confidence,
        routed_to_human=routed_to_human,
    )


@app.post("/api/contracts/analyze", response_model=ContractResponse)
async def analyze_contract(
    file: UploadFile = File(...),
    output_type: str = Form("summarize"),
):
    # Save temp file
    tmp_name = f"{uuid.uuid4().hex}_{file.filename}"
    tmp_path = OUTPUT_DIR / tmp_name
    with tmp_path.open("wb") as f:
        f.write(await file.read())

    # Extract + summarize
    text = extract_text_from_file(tmp_path)
    prompt = (
        "Provide a concise analysis of this contract:\n"
        f"- Output format requested: {output_type}\n"
        "- 5–8 bullet key points\n"
        "- Obligations & data protection\n"
        "- Major risks / non-compliance\n"
        "- Suggested clause updates\n\n"
        f"---\n{text[:12000]}"
    )
    summary = llm_complete(DOC_SYSTEM, prompt)

    # Risk + simulation
    _, _, norm_risk = keyword_risk_scan(text)
    incident_rate = monte_carlo_risk(norm_risk)
    confidence = 1.0 - incident_rate  # simple mapping: higher risk -> lower confidence

    status = "completed" if confidence >= 0.60 else "needs_review"

    return ContractResponse(
        file_name=file.filename,
        output_type=output_type,
        summary=summary,
        risk_score=norm_risk,
        incident_rate=incident_rate,
        confidence=confidence,
        status=status,
    )
