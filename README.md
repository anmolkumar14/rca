# AI RCA Generator

A production-grade Streamlit application for generating banking incident RCA documents with AI assistance, local incident history, and export options.

## Folder structure

- app.py — main Streamlit application
- requirements.txt — Python dependencies
- .env.example — sample environment variables
- data/incident_history.json — local JSON history store
- utils/
  - ai_client.py — AI generation and prompt helpers
  - export_utils.py — PDF/Word export helpers
  - history.py — incident history persistence

## Features

- Dark banking-style UI for incident input
- Severity P1–P4 and incident metadata capture
- AI-generated RCA in multiple styles:
  - Blameless
  - SOX Audit
  - Executive Summary
  - Technical Deep-Dive
- Local JSON history store
- PDF and Word export support

## Local setup

1. Create and activate a Python 3.11 environment.
2. Install dependencies:
   pip install -r requirements.txt
3. Copy .env.example to .env and add your Anthropic API key.
4. Run the app:
   streamlit run app.py

## Notes

- The app works without an API key using a professional fallback RCA sample.
- For full AI generation, set ANTHROPIC_API_KEY in .env.
