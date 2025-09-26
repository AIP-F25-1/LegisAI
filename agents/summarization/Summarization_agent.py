from transformers import pipeline
import os
import json

# Initialize Hugging Face summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def chunk_text(text, max_chars=2000):
    """
    Chunk text by max character count (safer for tokenized model input),
    keeps paragraphs together.
    """
    paragraphs = text.split('\n')
    chunks = []
    current = ''
    for para in paragraphs:
        if len(current) + len(para) > max_chars and current:
            chunks.append(current.strip())
            current = ''
        current += para + '\n'
    if current:
        chunks.append(current.strip())
    return chunks

def summarize_case(text):
    summaries = []
    for chunk in chunk_text(text, max_chars=1800):  # Safe margin for BART (max 2000 chars)
        try:
            summary = summarizer(chunk, max_length=120, min_length=30, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        except Exception as e:
            summaries.append(f"Error summarizing chunk: {str(e)}")
    return "\n".join(summaries)

def summarize_case(text):
    summaries = []
    for chunk in chunk_text(text):
        summary = summarizer(chunk, max_length=120, min_length=30, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    return "\n".join(summaries)

def extract_headnotes(text):
    lines = text.split('\n')
    headnote_text = "\n".join(lines[:4]) if len(lines) >= 4 else text
    summaries = []
    for chunk in chunk_text(headnote_text, max_chars=1200):  # safe for short headnotes
        try:
            summary = summarizer(chunk, max_length=60, min_length=20, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        except Exception as e:
            summaries.append(f"Error summarizing chunk: {str(e)}")
    return "\n".join(summaries)

def extract_ratio_obiter(text):
    prompt = "Extract the ratio decidendi (the key legal principle) and any obiter dicta (non-binding remarks) from this case:\n"
    max_chars = 2000  # 1024 BART tokens ≈ 2000-3000 chars, leave margin for prompt
    results = []
    paragraphs = text.split('\n')
    chunk = ""
    for para in paragraphs:
        # Always reserve room for the prompt text by counting total length
        if len(prompt) + len(chunk) + len(para) > max_chars:
            try:
                summary = summarizer(prompt + chunk, max_length=130, min_length=30, do_sample=False)
                results.append(summary[0]['summary_text'])
            except Exception as e:
                results.append(f"Error: {str(e)}")
            chunk = ""
        chunk += para + "\n"
    if chunk:
        try:
            summary = summarizer(prompt + chunk, max_length=130, min_length=30, do_sample=False)
            results.append(summary[0]['summary_text'])
        except Exception as e:
            results.append(f"Error: {str(e)}")
    return "\n".join(results)

def contrastive_summary(text):
    pro_plaintiff = ""
    pro_defendant = ""
    for para in text.split('\n\n'):
        lower = para.lower()
        if "plaintiff" in lower or "appellant" in lower:
            pro_plaintiff += para + "\n"
        elif "defendant" in lower or "appellee" in lower:
            pro_defendant += para + "\n"
    summary_plaintiff = summarize_case(pro_plaintiff) if pro_plaintiff else "No plaintiff/appellant arguments found."
    summary_defendant = summarize_case(pro_defendant) if pro_defendant else "No defendant/appellee arguments found."
    return summary_plaintiff, summary_defendant

# --- Multi-Case Loop ---
cases_folder = "D:/AIP/data/"
for filename in os.listdir(cases_folder):
    if filename.endswith('.json'):
        with open(os.path.join(cases_folder, filename), 'r', encoding='utf-8') as f:
            case = json.load(f)
        casebody = case.get("casebody", {})
        opinions = casebody.get("opinions", [])
        case_text = opinions[0].get("text", "") if opinions and isinstance(opinions[0], dict) else ""
        if not case_text or len(case_text) < 20:
            continue  # skip empty/invalid cases
        print(f"\n=== {filename} ===")
        try:
            print("--- Summary ---")
            print(summarize_case(case_text))
        except Exception as e:
            print(f"Error in summary for {filename}: {str(e)}")
        print("--- Headnotes ---")
        print(extract_headnotes(case_text))
        print("--- Ratio Decidendi & Obiter Dicta ---")
        try:
            print(extract_ratio_obiter(case_text))
        except Exception as e:
            print(f"Error during ratio/obiter extraction: {str(e)}")
        print("--- Contrastive Summarization ---")
        plaintiff_summary, defendant_summary = contrastive_summary(case_text)
        print("Plaintiff/Appellant:\n", plaintiff_summary)
        print("Defendant/Appellee:\n", defendant_summary)
