// frontend/src/lib/api.ts
type OutputKind = "summary" | "compliance" | "risk" | "draft" | "regularize";

/** If you're using the combined backend notebook with /api/chat and /api/process, keep true. */
const USE_GATEWAY = true;

const BASE = import.meta.env.VITE_API ?? "http://localhost:8000";

// ---- Chatbot ----
export async function apiChat(message: string) {
  const fd = new FormData();
  fd.append("message", message);
  const res = await fetch(`${BASE}/api/chat`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as { answer: string };
}

// ---- Upload + radio ----
export async function apiProcess(
  file: File,
  output: OutputKind,
  p_default = 0.05,
  lgd = 0.6
) {
  if (USE_GATEWAY) {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("output", output);
    fd.append("p_default", String(p_default));
    fd.append("lgd", String(lgd));
    const res = await fetch(`${BASE}/api/process`, {
      method: "POST",
      body: fd,
    });
    if (!res.ok) throw new Error(await res.text());
    return await res.json(); // { result: ... }
  }

  // If you later run per-agent notebooks instead of the combined one,
  // flip USE_GATEWAY=false and add the direct calls here.
  throw new Error("Set USE_GATEWAY=true or add per-agent endpoints here.");
}
