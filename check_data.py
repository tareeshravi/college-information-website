import json
import os

data_path = r"C:\Users\TAREESHRAVI\.gemini\antigravity\scratch\tnea-college-explorer\data\colleges.json"
with open(data_path, "r", encoding="utf-8") as f:
    colleges = json.load(f)

print(f"Loaded {len(colleges)} colleges for embedding.")
