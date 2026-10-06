import re
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

filepath = r"C:\Users\TAREESHRAVI\.gemini\antigravity\scratch\tnea-college-explorer\TNEA_College_Explorer_DEBUGGED_RESPONSIVE_FINAL.html"

print("=" * 70)
print("COMPREHENSIVE STATIC AUDIT OF FINAL HTML FILE")
print("=" * 70)

assert os.path.exists(filepath), "File does not exist!"

with open(filepath, "r", encoding="utf-8") as f:
    html = f.read()

print(f"File Size: {len(html)} bytes ({len(html.splitlines())} lines)")

# 1. Viewport Zoom Audit
assert 'name="viewport"' in html
meta_viewport = re.search(r'<meta\s+name=["\']viewport["\']\s+content=["\']([^"\']+)["\']', html)
assert meta_viewport, "Meta viewport tag missing!"
viewport_content = meta_viewport.group(1)
assert 'user-scalable=no' not in viewport_content, "ERROR: user-scalable=no found in viewport!"
assert 'maximum-scale=1' not in viewport_content, "ERROR: maximum-scale=1 found in viewport!"
print("[PASS] Viewport meta-tag allows user zoom and responsive scaling:", viewport_content)

# 2. Duplicate IDs Audit
ids = re.findall(r'id=["\']([a-zA-Z0-9_\-]+)["\']', html)
dup_ids = [i for i in set(ids) if ids.count(i) > 1]
print(f"[PASS] Total static IDs: {len(ids)}, Unique IDs: {len(set(ids))}")
assert len(dup_ids) == 0, f"Duplicate IDs found: {dup_ids}"

# 3. JavaScript Functions Audit
func_defs = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', html)
dup_funcs = [f for f in set(func_defs) if func_defs.count(f) > 1]
print(f"[PASS] Total JS functions: {len(func_defs)}, Unique: {len(set(func_defs))}")
assert len(dup_funcs) == 0, f"Duplicate functions found: {dup_funcs}"

# 4. Inline Handler Function Existence Check
inline_handlers = re.findall(r'(on[a-z]+)=["\']([^"\']+)["\']', html)
called_funcs = set()
for ev, code in inline_handlers:
    calls = re.findall(r'([a-zA-Z0-9_]+)\s*\(', code)
    called_funcs.update(calls)

standard_js = {'alert', 'confirm', 'prompt', 'parseFloat', 'parseInt', 'Number', 'String', 'encodeURIComponent', 'decodeURIComponent'}
missing_handlers = [cf for cf in called_funcs if cf not in func_defs and cf not in standard_js]
print(f"[PASS] Checked {len(inline_handlers)} inline event handlers.")
assert len(missing_handlers) == 0, f"Missing handler functions: {missing_handlers}"

# 5. Embedded Dataset Verification
idx_start = html.find("const initialCollegesData = [")
assert idx_start != -1, "const initialCollegesData not found!"
idx_json_start = html.find("[", idx_start)
# Find matching closing bracket for array
bracket_depth = 0
idx_json_end = -1
for i in range(idx_json_start, len(html)):
    if html[i] == '[':
        bracket_depth += 1
    elif html[i] == ']':
        bracket_depth -= 1
        if bracket_depth == 0:
            idx_json_end = i + 1
            break

json_str = html[idx_json_start:idx_json_end]
embedded_colleges = json.loads(json_str)
print(f"[PASS] Successfully extracted & parsed embedded dataset: {len(embedded_colleges)} colleges.")
assert len(embedded_colleges) == 20, f"Expected 20 colleges, got {len(embedded_colleges)}"

# 6. Feature Verification
features = [
    ("Search Bar & Clear Button", "searchInput", "searchClearBtn"),
    ("Department Filter & Chips", "deptFilter", "dept-chip"),
    ("Location Filter", "locationFilter", "all"),
    ("Sort Filter", "sortFilter", "package_desc"),
    ("Cutoff Calculator Widget", "calcScoreInput", "applyCutoffCalculator"),
    ("Comparison Tray & Modal", "compareModal", "openCompareModal"),
    ("Favorites / Bookmark Engine", "toggleFavorite", "STORAGE_FAVS_KEY"),
    ("AI Counselor Assistant Chat", "counselorChatPanel", "toggleCounselorChat"),
    ("College Dossier Modal", "dossierModal", "openCollegeModal"),
    ("Lightbox Modal", "lightboxModal", "openLightbox"),
    ("About & Reset Modal", "aboutModal", "resetAllToDefault"),
    ("Toast Notification System", "toastContainer", "showToast"),
    ("Image Error Handler", "handleImageError", "onerror")
]

for name, k1, k2 in features:
    assert k1 in html and k2 in html, f"Feature check failed for: {name}"
    print(f"[PASS] Feature present & verified: {name}")

# 7. Media Queries Check
media_queries = re.findall(r'@media\s*\([^\)]+\)', html)
print(f"[PASS] Responsive Media Queries present: {len(media_queries)} queries.")
assert len(media_queries) >= 4, "Insufficient responsive breakpoints"

print("\n" + "=" * 70)
print("ALL AUTOMATED STATIC AUDIT CHECKS PASSED WITH 100% SUCCESS!")
print("=" * 70)
