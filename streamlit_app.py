# chatbot/streamlit_app.py
import os, sys, streamlit as st
from pathlib import Path

# ---- Guarantee local imports work everywhere ----
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from chatbot_service import send_message_to_backend
from config import APP_TITLE, APP_DESCRIPTION

# ---- Streamlit page setup ----
st.set_page_config(page_title=APP_TITLE, page_icon="⚖️", layout="centered")
st.title(f"🤖 {APP_TITLE}")
st.caption(APP_DESCRIPTION)
st.divider()

# ---- Chat history ----
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# ---- Input box ----
if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    reply = send_message_to_backend(user_input)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").markdown(reply)
