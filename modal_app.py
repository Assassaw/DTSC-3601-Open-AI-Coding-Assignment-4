import modal

image = modal.Image.debian_slim().pip_install(
    "streamlit", "plotly", "pandas", "supabase", "pdfplumber"
)

app = modal.App("gdp-dashboard", image=image)

@app.function()
@modal.fastapi_endpoint()
def run():
    import streamlit.web.cli as stcli
    import sys

    sys.argv = [
        "streamlit",
        "run",
        "streamlit_app.py",
        "--server.port",
        "8080",
        "--server.address",
        "0.0.0.0",
    ]
    stcli.main()
