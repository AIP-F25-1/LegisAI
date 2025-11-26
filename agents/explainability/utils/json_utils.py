def safe_json(obj):
    try:
        return obj
    except Exception:
        return {"error": "JSON serialization failed"}
