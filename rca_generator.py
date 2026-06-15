import html
import os

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from utils.ai_client import generate_rca
from utils.export_utils import export_document
from utils.history import (
    compute_history_stats,
    export_history_csv,
    load_incidents,
    load_history,
    save_history,
)

load_dotenv()

st.set_page_config(
    page_title="AK Digital Lab — RCA Generator",
    page_icon="🔍",
    layout="wide",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "AK Digital Lab | AI-Powered Banking Tools | Built by Anmol Kumar",
    },
)

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
[data-testid="stToolbar"] {display: none;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stGitHubButton"] {display: none;}
.viewerBadge_container__1QSob {display: none;}
.styles_viewerBadge__1yB5_ {display: none;}

/* Hide the bottom-right Streamlit status / manage app area */
[data-testid="manage-app-button"] {display: none !important;}
[data-testid="stStatusWidget"] {display: none !important;}
button[data-testid="manage-app-button"] {display: none !important;}
button[kind="secondary"][title*="Manage"] {display: none !important;}
button[kind="secondary"][aria-label*="Manage"] {display: none !important;}
button[title="Manage app"] {display: none !important;}
button[aria-label="Manage app"] {display: none !important;}
#stDecoration {display: none !important;}
.reportview-container .main footer {visibility: hidden;}
section[data-testid="stSidebar"] > div {padding-top: 0rem;}

/* Force hide the bottom-right widget block if it is rendered by the host */
div[data-testid="stStatusWidget"] *,
div[data-testid="stStatusWidget"] {display: none !important; visibility: hidden !important;}
#root > div:last-child > div:last-child > div:last-child > div:last-child > button {display: none !important;}
#root div[style*="position: fixed"][style*="bottom"] button {display: none !important;}

/* Nuclear option for the lower-right area */
.st-emotion-cache-1dp5vir, .st-emotion-cache-15ecox0 {display: none !important;}
iframe[title="streamlit_analytics"] {display: none !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

CUSTOM_CSS = """
<style>
:root {
  --navy: #08111f;
  --navy-deep: #0c2340;
  --navy-soft: #11263b;
  --panel: rgba(10, 24, 40, 0.88);
  --panel-border: rgba(148, 163, 184, 0.18);
  --line: rgba(148, 163, 184, 0.14);
  --text: #edf6ff;
  --muted: #d5e4f5;
  --blue: #60a5fa;
  --gold: #fbbf24;
  --p1: #f87171;
  --p2: #fb923c;
  --p3: #60a5fa;
  --p4: #94a3b8;
}

html, body, [class*="stApp"] { font-family: "Segoe UI", "Inter", Arial, sans-serif; background: linear-gradient(140deg, #04111d 0%, #071a2a 35%, #06111b 100%); color: var(--text); }
[data-testid="stAppViewContainer"] { background: radial-gradient(circle at top, rgba(57, 84, 116, 0.12), transparent 25%), linear-gradient(135deg, #04111d 0%, #071726 55%, #03101b 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #071728 0%, #0c2340 40%, #081b30 100%); border-right: 1px solid rgba(148,163,184,0.15); }
[data-testid="stSidebar"] * { color: #eff6ff !important; }
[data-testid="stSidebar"] .stButton>button { background: transparent; color: #eff6ff; border: 1px solid rgba(148,163,184,0.25); border-radius: 10px; }
[data-testid="stSidebar"] .stButton>button:hover { background: rgba(96,165,250,0.14); border-color: rgba(96,165,250,0.45); }

.block-container { padding-top: 1rem; padding-bottom: 2rem; }

.kicker { display: inline-flex; align-items: center; gap: 8px; font-size: 0.84rem; letter-spacing: 0.18em; text-transform: uppercase; color: #cbd5e1; }
.kicker::before { content: ""; width: 10px; height: 10px; border-radius: 50%; background: linear-gradient(135deg, #fbbf24, #38bdf8); box-shadow: 0 0 0 4px rgba(251,191,36,0.08); }

.hero-card, .panel-card, .history-card { background: linear-gradient(145deg, rgba(9, 18, 30, 0.95), rgba(10, 22, 37, 0.98)); border: 1px solid var(--panel-border); border-radius: 22px; box-shadow: 0 16px 40px rgba(7, 10, 18, 0.45); }

.hero-card { padding: 20px 22px 18px; margin-bottom: 18px; }
.hero-grid { display:flex; align-items:flex-start; justify-content:space-between; gap:14px; flex-wrap:wrap; }
.brand-chip { display:inline-flex; align-items:center; gap:8px; padding:8px 10px; border-radius:999px; background: rgba(96,165,250,0.12); border: 1px solid rgba(96,165,250,0.25); color:#eff6ff; font-weight:600; font-size:0.92rem; }
.brand-chip small { color:#dbeafe; font-weight:500; }
.badge-row { display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }
.badge { display:inline-flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px; font-weight:700; font-size:0.84rem; border: 1px solid rgba(148,163,184,0.18); }
.badge-p1 { background: rgba(248,113,113,0.1); color:#fecaca; border-color: rgba(248,113,113,0.35); }
.badge-p2 { background: rgba(251,146,60,0.12); color:#fed7aa; border-color: rgba(251,146,60,0.35); }
.badge-p3 { background: rgba(96,165,250,0.12); color:#dbeafe; border-color: rgba(96,165,250,0.35); }
.badge-p4 { background: rgba(148,163,184,0.12); color:#e2e8f0; border-color: rgba(148,163,184,0.35); }

h1, h2, h3 { color: #ffffff; letter-spacing: -0.02em; }

div.stTextInput>label, div.stSelectbox>label, div.stTextArea>label { color: #dbeafe !important; font-weight: 600; }
div.stTextInput>div>input, div.stTextArea>div>textarea, div.stSelectbox>div>div { background: rgba(8, 18, 28, 0.95); color: #eff6ff; border: 1px solid rgba(148,163,184,0.18); border-radius: 12px; }
div.stTextInput>div>input:focus, div.stTextArea>div>textarea:focus { border-color: rgba(96,165,250,0.7); box-shadow: 0 0 0 3px rgba(96,165,250,0.15); }

.stAlert { border-radius: 16px; background: rgba(15, 23, 42, 0.96); border: 1px solid rgba(96,165,250,0.2); color: #eff6ff; }

.stButton>button { border-radius: 12px; padding: 0.55rem 0.9rem; border: 1px solid rgba(96,165,250,0.35); background: linear-gradient(135deg, #0f4c81 0%, #2563eb 100%); color: #eff6ff; font-weight: 700; box-shadow: 0 10px 24px rgba(37, 99, 235, 0.25); }
.stButton>button:hover { background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%); border-color: rgba(191,219,254,0.75); }
.stButton>button:focus { box-shadow: 0 0 0 3px rgba(96,165,250,0.24); }

.footer-note { color: #cbd5e1; font-size: 0.95rem; line-height: 1.4; }

.premium-card { background: linear-gradient(145deg, rgba(9, 18, 30, 0.97), rgba(12, 24, 42, 0.98)); border: 1px solid rgba(148,163,184,0.18); border-radius: 18px; padding: 16px; box-shadow: 0 14px 28px rgba(3, 7, 18, 0.45); }
.premium-card h3 { margin: 0 0 4px; font-size: 1rem; }
.premium-card p { color: #dbeafe; font-size: 0.95rem; }
.card-title-row { display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; }
.copy-btn { background: rgba(15,23,42,0.98); color: #eff6ff; border: 1px solid rgba(96,165,250,0.35); border-radius: 10px; padding: 0.45rem 0.65rem; font-weight: 600; cursor: pointer; }
.copy-btn:hover { background: rgba(30,41,59,0.98); }
.rca-body { white-space: pre-wrap; font-family: "Segoe UI", Arial, sans-serif; color: #e5eefb; line-height: 1.5; font-size: 0.94rem; }

@media (max-width: 1100px) {
  .hero-grid { flex-direction: column; }
}

@media (max-width: 768px) {
  .block-container { padding-left: 0.65rem; padding-right: 0.65rem; }
  .hero-card { border-radius: 16px; }
  .premium-card { padding: 12px; }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def severity_badges(selected: str):
    badges = [
        ("P1", "Critical", "badge-p1"),
        ("P2", "High", "badge-p2"),
        ("P3", "Moderate", "badge-p3"),
        ("P4", "Low", "badge-p4"),
    ]
    return "".join(
        f"<span class='badge {cls}'>{label}</span>" if value == selected else f"<span class='badge {cls}'>{label}</span>"
        for value, label, cls in badges
    )


DEFAULT_INCIDENT = {
    "incident_title": "Payment gateway latency spike in settlement window",
    "severity": "P2",
    "systems": "Core Banking, API Gateway, Databricks ETL",
    "description": "Latency increased during the end-of-day settlement window, causing delayed payment confirmations and elevated incident response traffic.",
    "timeline": "10:15 detection, 10:27 incident bridge activated, 10:40 rollback executed, 11:20 stabilization confirmed.",
    "root_cause": "Misconfigured timeout threshold combined with dependency latency saturation and weak deployment validation.",
    "fix_applied": "Rollback of the recent release, increased timeout thresholds, and updated incident runbook guidance.",
    "output_style": "Blameless",
}


def render_sidebar():
    with st.sidebar:
        st.markdown("<div class='kicker'>Financial Sector Platform</div>", unsafe_allow_html=True)
        st.title("AI RCA Generator")
        st.caption("Banking and financial sector incident command center for enterprise RCA workflows.")

        st.markdown("### Workspace")
        st.markdown("- Severity-aware incident intake")
        st.markdown("- Blameless and audit-ready outputs")
        st.markdown("- Local history and PDF/Word export")
        st.markdown("- Azure App Service ready")

        st.markdown("---")
        st.markdown("### Incident History")
        search_query = st.text_input("Search incidents", key="history_search", placeholder="Filter by title, system, or severity")
        stats = compute_history_stats(load_incidents(query=search_query or None))
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("This month", stats["this_month"])
        with col_b:
            st.metric("Avg MTTR", f"{stats['average_mttr']} min")
        st.metric("P1", stats["p1_count"])
        st.metric("P2", stats["p2_count"])

        csv_path = None
        try:
            csv_path = export_history_csv()
        except Exception:
            csv_path = None

        if csv_path:
            with open(csv_path, "rb") as file:
                st.download_button("Export all history to CSV", file.read(), file_name="incidents_export.csv", mime="text/csv", key="export_csv")

        st.markdown("---")
        st.caption("Recent incidents (last 10)")
        incidents = load_incidents(query=search_query or None, limit=10)
        for item in incidents:
            label = f"{item['title']} • {item['severity']} • {item['created_at'][:10]}"
            if st.button(label, key=f"history_item_{item['id']}", use_container_width=True):
                st.session_state.update({
                    "incident_title": item.get("title", ""),
                    "severity": item.get("severity", "P2"),
                    "systems": item.get("systems", ""),
                    "description": item.get("description", ""),
                    "timeline": item.get("timeline", ""),
                    "root_cause": item.get("root_cause", ""),
                    "fix_applied": item.get("fix_applied", ""),
                    "output_style": item.get("style", "Blameless"),
                })
                st.success("Incident loaded from history.")
                st.rerun()

        st.markdown("---")
        st.caption("Powered by Anthropic Claude and Streamlit for enterprise incident review.")


def render_output_card(result, style):
    card = f"""
    <div class="premium-card">
      <div class="card-title-row">
        <div>
          <div class="kicker">Generated RCA</div>
          <h3>Enterprise-ready {style} output</h3>
          <p>Use this card for review, share-out, and export. The copy action uses the browser clipboard.</p>
        </div>
        <button class="copy-btn" onclick="copyRcaText()">Copy RCA</button>
      </div>
      <div class="premium-card" style="margin-top: 12px; background: rgba(5,11,18,0.94);">
        <div class="rca-body">{html.escape(result['document'])}</div>
      </div>
      <textarea id="rca-copy-text" style="position:absolute; left:-9999px; top:-9999px;">{html.escape(result['document'])}</textarea>
    </div>
    <script>
      function copyRcaText() {{
        const text = document.getElementById('rca-copy-text').value;
        navigator.clipboard.writeText(text).then(() => alert('RCA copied to clipboard.'));
      }}
    </script>
    """
    components.html(card, height=640, scrolling=True)


def main():
    render_sidebar()

    st.markdown("<div class='hero-card'>", unsafe_allow_html=True)
    st.markdown("<div class='hero-grid'>", unsafe_allow_html=True)
    st.markdown("<div><div class='kicker'>Financial Sector Platform</div><h1 style='margin: 8px 0 6px; font-size: 2rem;'>AI-Powered RCA Generator</h1><p style='color:#dbeafe; max-width: 720px; margin-bottom: 0;'>A premium enterprise incident analysis workspace for banking production events, with blameless RCA drafting, audit-ready language, and export-ready outputs.</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-chip'>🏦 Financial Sector • <small>Banking and financial services command center</small></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='badge-row'>" + severity_badges("P2") + "</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer-note'>Use this workspace to capture production incidents, generate post-mortem RCA documents, and export them for audit, SRE, or technology leadership review.</div>", unsafe_allow_html=True)

    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown("<div class='panel-card' style='padding: 14px 14px 6px; border-radius: 18px;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin-top: 0; font-size: 1.15rem;'>Incident Intake</h2>", unsafe_allow_html=True)
        incident_title = st.text_input("Incident title", key="incident_title", value=st.session_state.get("incident_title", DEFAULT_INCIDENT["incident_title"]), placeholder="Enter the incident title")
        severity = st.selectbox("Severity", ["P1", "P2", "P3", "P4"], index=["P1", "P2", "P3", "P4"].index(st.session_state.get("severity", DEFAULT_INCIDENT["severity"])), key="severity")
        systems = st.text_input("Affected systems", key="systems", value=st.session_state.get("systems", DEFAULT_INCIDENT["systems"]), placeholder="Enter affected systems")
        description = st.text_area("Incident description", key="description", value=st.session_state.get("description", DEFAULT_INCIDENT["description"]), height=110)
        timeline = st.text_area("Timeline", key="timeline", value=st.session_state.get("timeline", DEFAULT_INCIDENT["timeline"]), height=110)
        root_cause = st.text_area("Root cause", key="root_cause", value=st.session_state.get("root_cause", DEFAULT_INCIDENT["root_cause"]), height=110)
        fix_applied = st.text_area("Fix applied", key="fix_applied", value=st.session_state.get("fix_applied", DEFAULT_INCIDENT["fix_applied"]), height=110)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='panel-card' style='padding: 14px 14px 6px; border-radius: 18px;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin-top: 0; font-size: 1.15rem;'>Output & Controls</h2>", unsafe_allow_html=True)
        output_style = st.selectbox("RCA format", ["Blameless", "SOX Audit", "Executive Summary", "Technical Deep-Dive"], index=["Blameless", "SOX Audit", "Executive Summary", "Technical Deep-Dive"].index(st.session_state.get("output_style", DEFAULT_INCIDENT["output_style"])), key="output_style")

        if st.button("Generate RCA", use_container_width=True):
            with st.spinner("Generating the enterprise RCA draft..."):
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
            save_history({
                'title': incident_title,
                'severity': severity,
                'systems': systems,
                'style': output_style,
                'summary': result['summary'],
            })
            st.success("RCA generated and stored in local history.")

        export_choice = st.selectbox("Export format", ["PDF", "Word"], key="export_choice")
        if 'rca_result' in st.session_state and st.button("Export document", use_container_width=True):
            export_path = export_document(st.session_state['rca_result']['document'], st.session_state['rca_result']['summary'], export_choice)
            with open(export_path, 'rb') as file:
                st.download_button("Download export", file.read(), file_name=os.path.basename(export_path), mime="application/octet-stream")

        st.markdown("</div>", unsafe_allow_html=True)

    if 'rca_result' in st.session_state:
        st.markdown("<div class='panel-card' style='padding: 14px; margin-top: 12px; border-radius: 18px;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin-top: 0; font-size: 1.08rem;'>Generated RCA</h2>", unsafe_allow_html=True)
        result = st.session_state['rca_result']
        st.caption(f"Format: {st.session_state.get('last_style', 'Blameless')}")
        st.markdown(f"<div class='footer-note' style='margin-bottom: 10px;'>{html.escape(result['summary'])}</div>", unsafe_allow_html=True)
        render_output_card(result, st.session_state.get('last_style', 'Blameless'))
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel-card' style='padding: 14px; margin-top: 12px; border-radius: 18px;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='margin-top: 0; font-size: 1.08rem;'>Incident History</h2>", unsafe_allow_html=True)
    for item in load_history(limit=6):
        st.markdown("<div class='history-card' style='padding: 12px; margin-bottom: 10px;'>", unsafe_allow_html=True)
        st.markdown(f"<strong>{html.escape(item['title'])}</strong> — <span style='color:#cbd5e1;'>Severity {html.escape(item['severity'])}</span>", unsafe_allow_html=True)
        st.caption(f"Style: {html.escape(item['style'])}")
        st.write(item['summary'])
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
