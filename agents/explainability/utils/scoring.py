import difflib

def compare_texts(text_a, text_b):
    ratio = difflib.SequenceMatcher(None, text_a, text_b).ratio()
    return round(ratio * 100, 2)
