import os
import pandas as pd
import streamlit as st
import plotly.express as px
from supabase import create_client
import ast
import pdfplumber


st.subheader("GDP by Country (IMF 2025 Estimates)")

pdf_path = "List of countries by GDP (nominal) - Wikipedia.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    # Parse lines that look like "1  United States 30,507,217 ..."
    rows = []
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) > 3 and parts[0].isdigit():
            rank = int(parts[0])
            country = " ".join(parts[1:-3])  # handle multi-word countries
            try:
                gdp = int(parts[-3].replace(",", ""))
            except:
                continue
            rows.append({"Rank": rank, "Country": country, "GDP (Million US$)": gdp})

    gdp_df = pd.DataFrame(rows)

    if not gdp_df.empty:
        st.dataframe(gdp_df.head(20), use_container_width=True)

        # Pie chart of top 10 GDP
        top10 = gdp_df.sort_values("GDP (Million US$)", ascending=False).head(10)
        fig = px.pie(top10, values="GDP (Million US$)", names="Country",
                     title="Top 10 Countries by Nominal GDP (IMF 2025)")
        st.plotly_chart(fig, use_container_width=True)

        # Optional: group continents if you add a mapping
        # Example: st.bar_chart(top10.set_index("Country")["GDP (Million US$)"])
    else:
        st.error("Could not parse GDP table from PDF.")
except Exception as e:
    st.error(f"Failed to read GDP PDF: {e}")
