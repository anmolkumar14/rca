import os
import streamlit as st
from dotenv import load_dotenv

from utils.ai_client import generate_rca
from utils.history import load_history, save_history
from utils.export_utils import export_document

load_dotenv()

st.set_page_config(page_title="AI RCA Generator", page_icon="🧭", layout="wide")

st.markdown(
    """
    <style>
        .stApp { background: linear-gradient(135deg, #07111f 0%, #0d1b2a 45%, #08131f 100%); color: #eff6ff; }
        div.stTextInput>label, div.stSelectbox>label, div.stTextArea>label, div.stNumberInput>label { color: #dbeafe !important; }
        .block-container { padding-top: 1rem; padding-bottom: 2rem; }
        .stButton>button { background: linear-gradient(135deg, #1d4ed8, #2563eb); color: white; border: 1px solid #3b82f6; border-radius: 10px; }
        .stButton>button:hover { background: linear-gradient(135deg, #2563eb, #1e40af); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("AI-Powered RCA Generator for Banking Incidents")
st.caption("Production-grade RCA drafting for UBS/BNY style banking operations, with blameless analysis, SOX-ready wording, and export-ready outputs.")

col_left, col_right = st.columns([1.2, 0.8], gap="large")

with col_left:
    st.subheader("Incident Intake")
    incident_title = st.text_input("Incident title", placeholder="Example: Payment Gateway latency spike in APAC settlement window")
    severity = st.selectbox("Severity", ["P1", "P2", "P3", "P4"])
    systems = st.text_input("Affected systems", placeholder="Core Banking, API Gateway, Databricks ETL")
    description = st.text_area("Incident description", height=120, placeholder="Describe the production impact, user symptoms, and business context.")
    timeline = st.text_area("Timeline", height=120, placeholder="List key events: detection, escalation, mitigation, recovery.")
    root_cause = st.text_area("Root cause", height=110, placeholder="Summarize the likely technical and process causes.")
    fix_applied = st.text_area("Fix applied", height=110, placeholder="Document the mitigation, rollback, or remediation steps performed.")

with col_right:
    st.subheader("Output Style")
    output_style = st.selectbox("RCA format", ["Blameless", "SOX Audit", "Executive Summary", "Technical Deep-Dive"])
    st.info("The app is ready for Anthropic Claude via the Anthropic SDK. If the API key is unavailable, it falls back to a professional banking RCA draft.")
    st.markdown("**Deployment-ready setup**")
    st.markdown("- Streamlit UI")
    st.markdown("- Local JSON history")
    st.markdown("- PDF and Word export")
    st.markdown("- Azure App Service compatible")

    if st.button("Generate RCA", use_container_width=True):
        with st.spinner("Generating RCA draft..."):
            result = generate_rca(
                title=incident_title,
                severity=severity,
                systems=systems,
                description=description,
                timeline=timeline,
                root_cause=root_cause,
                fix_applied=fix_applied,
                output_style=output_style,
            )

        st.session_state['rca_result'] = result
        st.session_state['last_style'] = output_style

        history_entry = {
            "title": incident_title,
            "severity": severity,
            "systems": systems,
            "style": output_style,
            "summary": result['summary'],
        }
        save_history(history_entry)
        st.success("RCA generated and saved to local history.")

    if 'rca_result' in st.session_state:
        st.subheader("Generated RCA")
        result = st.session_state['rca_result']
        st.markdown("### Summary")
        st.write(result['summary'])
        st.markdown("### Full RCA")
        st.write(result['document'])

        export_choice = st.selectbox("Export format", ["PDF", "Word"])
        if st.button("Export document", use_container_width=True):
            export_path = export_document(result['document'], result['summary'], export_choice)
            st.download_button(
                label="Download export",
                data=open(export_path, 'rb').read(),
                file_name=os.path.basename(export_path),
                mime="application/octet-stream",
            )

st.subheader("Incident History")
for item in load_history(limit=8):
    with st.container(border=True):
        st.write(f"**{item['title']}** — {item['severity']} | {item['style']}")
        st.caption(item['summary'])
