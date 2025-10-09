import streamlit as st
from src.pipelines.review_clause import run_cross_consistency

st.set_page_config(page_title="LegisAI – Cross-Consistency", layout="centered")

st.title("LegisAI – Reasoning & Self-Consistency (CrewAI)")
st.write("Run multiple specialized agents on the same clause and compare their outputs.")

default_clause = "The employee shall not compete with the employer for two (2) years after termination within North America."
clause = st.text_area("Clause to Review", value=default_clause, height=120)

if st.button("Run Cross-Consistency"):
    with st.spinner("Evaluating with multiple agents..."):
        res = run_cross_consistency(clause)

    cc = res["cross_consistency"]
    st.subheader("Consensus")
    c1, c2, c3 = st.columns(3)
    c1.metric("Winner Verdict", cc["winner_verdict"])
    c2.metric("Consistency", cc["consistency"])
    c3.metric("Avg Confidence", cc["confidence_avg"])

    st.markdown("### Per-Agent Outputs")
    for i, pa in enumerate(res["per_agent"], 1):
        with st.expander(f"Agent {i} result"):
            st.json(pa)

    st.markdown("### Citations")
    if not res["citations"]:
        st.info("No citations returned.")
    else:
        for c in res["citations"]:
            st.write(f"- **{c.get('title')}** ({c.get('jurisdiction')}) — {c.get('url')}")
