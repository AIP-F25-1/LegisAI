import streamlit as st
import requests

st.title("🧠 LegisAI – Cross Consistency Checker")

clause = st.text_area("Enter contract clause:", height=150)

if st.button("Run Cross Consistency"):
    if clause.strip():
        with st.spinner("Running analysis..."):
            response = requests.post("http://127.0.0.1:8000/cross_consistency", json={"clause": clause})
            if response.status_code == 200:
                data = response.json()
                st.success(data["summary"])
                st.write("### Individual Scores")
                for role, score in data["scores"].items():
                    st.progress(int(score))
                    st.text(f"{role}: {score}%")
            else:
                st.error("Backend error, check terminal.")
    else:
        st.warning("Please enter a clause to analyze.")
