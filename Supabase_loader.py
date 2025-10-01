import pandas as pd
import supabase
from supabase import create_client, Client
import ast  # to safely turn stringified lists back into real lists

# Your Supabase project details (anon key + URL)
SUPABASE_URL = "https://mdjythfmmyqsggvrngzx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1kanl0aGZtbXlxc2dndnJuZ3p4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzMzM5NjEsImV4cCI6MjA3NDkwOTk2MX0.1Rb-GukT8n1T3Q9kBRf4bTLX1M2kathwZfyCBh1fwjM"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upsert_to_supabase(df: pd.DataFrame, table_name: str = "articles"):
    records = df.to_dict(orient="records")

    for r in records:
        kw = r.get("keywords")
        if isinstance(kw, str):
            try:
                # Convert string like "['a','b']" into a Python list
                kw_list = ast.literal_eval(kw)
                if isinstance(kw_list, list):
                    # Format for Postgres array: {a,b,c}
                    r["keywords"] = "{" + ",".join([str(x) for x in kw_list]) + "}"
                else:
                    r["keywords"] = "{}"
            except:
                r["keywords"] = "{}"
        elif isinstance(kw, list):
            r["keywords"] = "{" + ",".join([str(x) for x in kw]) + "}"

    resp = supabase.table(table_name).upsert(records).execute()
    print("Upsert response:", resp)

if __name__ == "__main__":
    # Load the structured CSV that ai_portion.py created
    df = pd.read_csv("outputs/structured.csv")
    upsert_to_supabase(df)
