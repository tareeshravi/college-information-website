import os
import re
import json

def analyze_file(filepath):
    print("=" * 60)
    print("ANALYZING:", filepath)
    print("=" * 60)
    if not os.path.exists(filepath):
        print("File does not exist:", filepath)
        return

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    print(f"Total Length: {len(content)} characters, {len(content.splitlines())} lines")

    # Extract IDs
    ids = re.findall(r'id=["\']([a-zA-Z0-9_\-]+)["\']', content)
    dup_ids = [i for i in set(ids) if ids.count(i) > 1]
    print(f"Total IDs: {len(ids)}, Unique IDs: {len(set(ids))}")
    if dup_ids:
        print(f"DUPLICATE IDs FOUND: {dup_ids}")
    else:
        print("No duplicate static IDs.")

    # Extract Function definitions
    func_defs = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', content)
    dup_funcs = [f for f in set(func_defs) if func_defs.count(f) > 1]
    print(f"Total Functions: {len(func_defs)}, Unique Functions: {len(set(func_defs))}")
    if dup_funcs:
        print(f"DUPLICATE Functions: {dup_funcs}")

    # Extract all inline event handlers like onclick, onchange, etc.
    inline_handlers = re.findall(r'(on[a-z]+)=["\']([^"\']+)["\']', content)
    print(f"Total inline event handlers: {len(inline_handlers)}")
    called_funcs = set()
    for ev, code in inline_handlers:
        call_matches = re.findall(r'([a-zA-Z0-9_]+)\s*\(', code)
        called_funcs.update(call_matches)

    # Check for missing called functions
    missing_funcs = [cf for cf in called_funcs if cf not in func_defs and cf not in [
        'alert', 'confirm', 'prompt', 'parseFloat', 'parseInt', 'Number', 'String', 'encodeURIComponent', 'decodeURIComponent'
    ]]
    print(f"Potentially undefined functions called inline: {missing_funcs}")

    # Look for chat, AI counselor, compare, bookmark/favorite, cutoff calculator
    features = ['chat', 'compare', 'favorite', 'bookmark', 'calculator', 'cutoff', 'dossier', 'lightbox', 'modal', 'upload', 'filter', 'sort', 'export']
    print("\nFeature keyword checks:")
    for feat in features:
        count = len(re.findall(feat, content, re.IGNORECASE))
        print(f"  - {feat}: {count} occurrences")

analyze_file(r"C:\Users\TAREESHRAVI\Downloads\gemini-code-1787937230222.html")
analyze_file(r"C:\Users\TAREESHRAVI\.gemini\antigravity\scratch\tnea-college-explorer\index.html")
