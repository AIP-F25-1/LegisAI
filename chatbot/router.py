from chatbot.llm_connector import call_llm

def process_user_message(user_text: str) -> str:
    """
    Main router function for chatbot.
    Returns the bot's reply.
    """
    reply = call_llm(user_text)
    return reply
