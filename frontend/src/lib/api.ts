// Output options supported by the backend
export type OutputType = "draft" | "summarize" | "regularize";

const BASE = import.meta.env.VITE_API ?? "http://localhost:8000";

/* ========== CHATBOT API ========== */

export interface ChatResponse {
  answer: string;
  confidence: number; // 0..1
  routed_to_human: boolean; // true if backend thinks confidence < 0.6
}

export async function apiChat(message: string): Promise<ChatResponse> {
  const res = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  return (await res.json()) as ChatResponse;
}

/* ========== CONTRACT / UPLOAD API ========== */

export interface ContractProcessResponse {
  file_name: string;
  output_type: string; // echo of the requested output_type
  summary: string; // LLM summary / analysis
  risk_score: number; // normalized risk 0..1
  incident_rate: number; // Monte Carlo incident rate
  confidence: number; // 0..1 (1 - incident_rate)
  status: "completed" | "needs_review";
}

/**
 * Call FastAPI /api/contracts/analyze
 * - file: uploaded contract PDF/DOCX/TXT
 * - outputType: "draft" | "summarize" | "regularize"
 */
export async function apiProcess(
  file: File,
  outputType: OutputType
): Promise<ContractProcessResponse> {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("output_type", outputType);

  const res = await fetch(`${BASE}/api/contracts/analyze`, {
    method: "POST",
    body: fd,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  return (await res.json()) as ContractProcessResponse;
}
