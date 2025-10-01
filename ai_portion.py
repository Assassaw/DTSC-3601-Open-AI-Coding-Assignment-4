import argparse, os, json, time, uuid, pathlib, pandas as pd
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from openai import OpenAI

import requests
from bs4 import BeautifulSoup
import pdfplumber

ENDPOINT = "https://cdong1--azure-proxy-web-app.modal.run"
API_KEY = "supersecretkey"
DEPLOYMENT = "gpt-4o"

class Row(BaseModel):
    id: str
    title: str
    summary: str
    source_url: Optional[str] = None
    extracted_at: datetime
    topic: str = "custom"
    keywords: List[str] = Field(default_factory=list)

# --- Collectors ---
def collect_web(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()

    # Special case: Wikipedia GDP table
    if "wikipedia.org/wiki/List_of_countries_by_GDP" in url:
        dfs = pd.read_html(r.text)
        df = dfs[0]   # first table has GDP data
        return df.to_csv(index=False)

    soup = BeautifulSoup(r.text, "lxml")
    for tag in soup(["script","style","noscript","svg"]):
        tag.decompose()
    main = soup.find("main") or soup.body
    txt = main.get_text(" ", strip=True) if main else soup.get_text(" ", strip=True)
    return " ".join(txt.split())

def collect_pdf(path: str) -> str:
    pages = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            pages.append(p.extract_text() or "")
    return "\n".join(pages).strip()

# --- Utils ---
def ensure_dirs():
    pathlib.Path("data").mkdir(exist_ok=True)
    pathlib.Path("outputs").mkdir(exist_ok=True)

def save_blob(text: str):
    with open("data/raw_blob.txt", "w", encoding="utf-8") as f:
        f.write(text)

def call_llm(blob_text: str, source_url: Optional[str], topic: str) -> dict:
    schema = {
        "type": "object",
        "properties": {
            "id": {"type":"string"},
            "title": {"type":"string"},
            "summary": {"type":"string"},
            "source_url": {"type":"string"},
            "extracted_at": {"type":"string"},
            "topic": {"type":"string"},
            "keywords": {"type":"array","items":{"type":"string"}}
        },
        "required": ["id","title","summary","source_url","extracted_at"]
    }
    sys = "Return one valid JSON object only. No markdown."
    usr = f"""
JSON Schema:
{json.dumps(schema, ensure_ascii=False)}

From the text/table, extract:
- id: a new uuid
- title: concise human-readable title
- summary: 3-6 sentence abstract
- source_url: {source_url}
- extracted_at: ISO8601 UTC timestamp
- topic: {topic}
- keywords: 5-12 topical keywords

Text/Table:
{blob_text[:18000]}
"""
    client = OpenAI(base_url=ENDPOINT, api_key=API_KEY)
    resp = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[{"role":"system","content":sys},{"role":"user","content":usr}],
        temperature=0,
        response_format={"type":"json_object"}
    )
    raw = resp.choices[0].message.content.strip()
    data = json.loads(raw)
    if not data.get("id"):
        data["id"] = str(uuid.uuid4())
    if not data.get("extracted_at"):
        data["extracted_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if source_url and not data.get("source_url"):
        data["source_url"] = source_url
    if not data.get("topic"):
        data["topic"] = topic
    return data

def to_dataframe(item: dict) -> pd.DataFrame:
    row = Row(**item).model_dump()
    return pd.DataFrame([row])

# --- Main ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str)
    parser.add_argument("--pdf", type=str)
    parser.add_argument("--source-url", type=str, default=None)
    parser.add_argument("--topic", type=str, default="custom")
    args = parser.parse_args()

    ensure_dirs()

    if args.url and args.pdf:
        raise SystemExit("Provide either --url or --pdf, not both.")
    if not args.url and not args.pdf:
        raise SystemExit("Provide --url or --pdf.")

    if args.url:
        blob = collect_web(args.url)
        src = args.url
    else:
        blob = collect_pdf(args.pdf)
        src = args.source_url or pathlib.Path(args.pdf).name

    save_blob(blob)
    data = call_llm(blob, src, args.topic)
    with open("outputs/structured.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    df = to_dataframe(data)
    df.to_csv("outputs/structured.csv", index=False, encoding="utf-8")
    print(df.head())

if __name__ == "__main__":
    main()
