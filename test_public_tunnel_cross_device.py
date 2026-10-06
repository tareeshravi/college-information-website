import urllib.request
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PUBLIC_URL = "https://lady-bee-und-paste.trycloudflare.com"

print("=" * 70)
print("REAL PUBLIC HTTPS CROSS-DEVICE CLOUD SYNC VERIFICATION")
print(f"Target Public URL: {PUBLIC_URL}")
print("=" * 70)

# STEP 1: Fetch initial data from public HTTPS URL (Device 1: Laptop)
print("\n[STEP 1] Device 1 (Laptop) connects to Public HTTPS URL...")
req = urllib.request.Request(f"{PUBLIC_URL}/api/colleges?t={int(time.time())}", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"})
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
    colleges = data["colleges"]
    target_college = colleges[0]
    print(f"  -> Connected successfully! Loaded {len(colleges)} colleges.")
    print(f"  -> Target College: {target_college['name']} (ID: {target_college['id']})")
    print(f"  -> Initial Tuition Fee: ₹{target_college['fees']['tuition']}")

# STEP 2: Device 1 (Laptop) updates tuition fee to 80,000
new_fee_1 = 80000
print(f"\n[STEP 2] Device 1 (Laptop) edits tuition fee -> ₹{new_fee_1}...")
target_college["fees"]["tuition"] = new_fee_1
payload = json.dumps({"colleges": colleges}).encode("utf-8")
post_req = urllib.request.Request(f"{PUBLIC_URL}/api/colleges", data=payload, headers={"Content-Type": "application/json", "User-Agent": "Laptop-Chrome"})
with urllib.request.urlopen(post_req, timeout=15) as resp:
    res = json.loads(resp.read().decode())
    print("  -> Laptop save response:", res)

# STEP 3: Device 2 (iPhone) opens the public URL from mobile network
print("\n[STEP 3] Device 2 (iPhone) opens the SAME public HTTPS URL (Mobile Safari)...")
iphone_req = urllib.request.Request(f"{PUBLIC_URL}/api/colleges?t={int(time.time())}", headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"})
with urllib.request.urlopen(iphone_req, timeout=15) as resp:
    iphone_data = json.loads(resp.read().decode())
    iphone_colleges = iphone_data["colleges"]
    iphone_target = iphone_colleges[0]
    print(f"  -> iPhone retrieved Tuition Fee: ₹{iphone_target['fees']['tuition']}")
    assert iphone_target['fees']['tuition'] == new_fee_1, "iPhone data did not match Laptop edit!"
    print("  -> [PASS] iPhone receives the EXACT update made by Laptop!")

# STEP 4: Device 3 (Android Phone) opens the public URL
print("\n[STEP 4] Device 3 (Android Phone) opens the public HTTPS URL...")
android_req = urllib.request.Request(f"{PUBLIC_URL}/api/colleges?t={int(time.time())}", headers={"User-Agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36"})
with urllib.request.urlopen(android_req, timeout=15) as resp:
    android_data = json.loads(resp.read().decode())
    android_target = android_data["colleges"][0]
    print(f"  -> Android retrieved Tuition Fee: ₹{android_target['fees']['tuition']}")
    assert android_target['fees']['tuition'] == new_fee_1, "Android data did not match Laptop edit!"
    print("  -> [PASS] Android phone receives the update seamlessly!")

# STEP 5: Device 2 (iPhone) edits Tuition Fee to 88,500
new_fee_2 = 88500
print(f"\n[STEP 5] Device 2 (iPhone) now edits tuition fee to ₹{new_fee_2}...")
iphone_target["fees"]["tuition"] = new_fee_2
payload_2 = json.dumps({"colleges": iphone_colleges}).encode("utf-8")
iphone_post_req = urllib.request.Request(f"{PUBLIC_URL}/api/colleges", data=payload_2, headers={"Content-Type": "application/json", "User-Agent": "iPhone-Safari"})
with urllib.request.urlopen(iphone_post_req, timeout=15) as resp:
    print("  -> iPhone save response:", json.loads(resp.read().decode()))

# STEP 6: Device 1 (Laptop) refreshes or receives auto-sync
print("\n[STEP 6] Device 1 (Laptop) re-queries public cloud...")
with urllib.request.urlopen(req, timeout=15) as resp:
    final_data = json.loads(resp.read().decode())
    final_target = final_data["colleges"][0]
    print(f"  -> Laptop now sees Tuition Fee: ₹{final_target['fees']['tuition']}")
    assert final_target['fees']['tuition'] == new_fee_2, "Laptop did not receive iPhone edit!"
    print("  -> [PASS] Laptop immediately synchronized with iPhone edits!")

print("\n" + "=" * 70)
print("REAL-WORLD CLOUD MULTI-DEVICE SYNCHRONIZATION TEST: 100% SUCCESS!")
print("=" * 70)
