import json
import os

base_dir = r"C:\Users\TAREESHRAVI\.gemini\antigravity\scratch\tnea-college-explorer"
data_file = os.path.join(base_dir, "data", "colleges.json")

with open(data_file, "r", encoding="utf-8") as f:
    colleges_data = json.load(f)

print(f"Loaded {len(colleges_data)} colleges from colleges.json.")
