from chatbot.llm_connector import call_llm

def process_user_message(user_text: str) -> str:
    """
    Handles incoming user messages from the API.
    """
    reply = call_llm(user_text)
    return reply
