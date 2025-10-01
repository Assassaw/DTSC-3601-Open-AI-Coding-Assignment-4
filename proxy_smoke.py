# proxy_smoke.py
from openai import OpenAI

BASE_URL = "https://cdong1--azure-proxy-web-app.modal.run" 
API_KEY  = "supersecretkey"
MODEL    = "gpt-4o"

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
 
r = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Answer with one short sentence."},
        {"role": "user", "content": "Say 'proxy ok' if you received this."}
    ],
    temperature=0,
)
print(r.choices[0].message.content)
