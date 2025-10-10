import json
from pathlib import Path

def save_feedback(feedback_data):
    feedback_file = Path(__file__).resolve().parent.parent / "feedbackdata" / "feedback_log.json"

    # Load existing feedback
    if feedback_file.exists():
        with open(feedback_file, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    existing.append(feedback_data)

    # Save back
    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4)
