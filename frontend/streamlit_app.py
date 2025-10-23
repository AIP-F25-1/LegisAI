import streamlit as st
import requests

# -----------------------------------
# ⚖️ LegisAI Frontend App
# -----------------------------------

st.set_page_config(
    page_title="LegisAI – Consistency Checker",
    page_icon="⚖️",
    layout="centered",
)

# ---------- Header ----------
st.title("⚖️ LegisAI – Reasoning & Self-Consistency Module")
st.markdown("""
Welcome to **LegisAI’s Consistency Checker** – this interface connects to your FastAPI backend
and evaluates how multiple legal AI agents interpret the same clause.
""")

# ---------- Backend URL ----------
backend_url = st.text_input(
    "🔗 Backend URL (FastAPI endpoint):",
    "http://127.0.0.1:8000",
    help="Keep this default if your backend runs locally on port 8000.",
)

# ---------- Clause Input ----------
clause = st.text_area(
    "📜 Enter a Legal Clause to Analyze",
    "The supplier shall not be liable for any damages exceeding $10,000 regardless of cause.",
    height=150,
)

# ---------- Run Button ----------
if st.button("🚀 Run Consistency Check"):
    if not clause.strip():
        st.warning("Please enter a clause before running the check.")
    else:
        try:
            with st.spinner("Running 5 agents and analyzing consistency... ⏳"):
                res = requests.post(
                    f"{backend_url}/api/check-consistency",
                    json={"clause": clause},
                    timeout=60
                )
            if res.status_code == 200:
                data = res.json()

                # ----- Agent Outputs -----
                st.subheader("🤖 Agent Outputs")
                for name, text in data["agents"].items():
                    st.markdown(f"**{name.capitalize()} Agent:**")
                    st.write(text)
                    st.divider()

                # ----- Consistency Analysis -----
                st.subheader("🧠 Consistency Analysis")
                conflicts = data["consistency"]["conflicts"]
                if conflicts:
                    st.error("⚠️ Conflicts Detected:")
                    for c in conflicts:
                        st.write(f"- {c}")
                else:
                    st.success("✅ No conflicts detected. Agents are aligned.")

                st.info("**Harmonized Conclusion:**")
                st.markdown(f"> {data['consistency']['harmonized_conclusion']}")

            else:
                st.error(f"Backend returned status {res.status_code}")
                st.text(res.text)

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {e}")

# ---------- Footer ----------
st.markdown("---")
st.caption("Built by **Team LegisAI** – Multi-Agent Legal Research & Drafting Assistant ⚖️")
