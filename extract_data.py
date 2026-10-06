import os
import json
import re

base_dir = r"C:\Users\TAREESHRAVI\.gemini\antigravity\scratch\tnea-college-explorer"
html_path = os.path.join(base_dir, "tneaaa.html")

with open(html_path, "r", encoding="utf-8") as f:
    text = f.read()

# Also write index.html
with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(text)

start_tag = "const initialCollegesData = ["
end_tag = "let collegesData = [];"

start = text.find(start_tag) + len("const initialCollegesData = ")
end = text.find(end_tag, start)
raw = text[start:end].strip()
if raw.endswith(";"):
    raw = raw[:-1].strip()

# Replace unquoted keys with double-quoted keys
keys = [
    "id", "code", "name", "location", "category", "seats", 
    "highestPackage", "image", "fees", "tuition", "other", 
    "hostel", "events", "title", "desc", "date", "venue", 
    "photo", "departments", "OC", "BC", "MBC", "SC"
]

for k in keys:
    raw = re.sub(r'(?<!["\w])' + k + r'\s*:', '"' + k + '":', raw)

data = json.loads(raw)
os.makedirs(os.path.join(base_dir, "data"), exist_ok=True)
data_file = os.path.join(base_dir, "data", "colleges.json")

with open(data_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"SUCCESS: Saved {len(data)} colleges to {data_file}")
