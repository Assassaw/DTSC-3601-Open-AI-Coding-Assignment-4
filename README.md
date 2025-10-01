# DTSC 3601 - OpenAI Coding Assignment 4

This repo contains the full pipeline for the assignment:

- **ai_portion.py** → Collects data (URL/PDF), calls LLM, outputs structured JSON/CSV  
- **Supabase_loader.py** → Loads structured data into Supabase  
- **streamlit_app.py** → Streamlit dashboard for visualization (charts, tables)  
- **modal_app.py** → Deployment wrapper for Streamlit (for Modal)  
- **proxy_smoke.py** → Utility for proxy testing

## Running Locally
```bash
python ai_portion.py --pdf "List of countries by GDP (nominal) - Wikipedia.pdf" --topic gdp
python Supabase_loader.py
streamlit run streamlit_app.py
```

## Notes
- Supabase and API keys should be provided via environment variables (`.env`) and **not hard-coded**.
- Modal deployment may fail if free quota is exceeded; Streamlit Cloud is an alternative.


