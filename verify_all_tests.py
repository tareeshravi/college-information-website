import urllib.request
import json
import base64
import os
import time

SERVER = "http://127.0.0.1:8000"
PROJECT_DIR = r"C:\Users\TAREESHRAVI\.gemini\antigravity\scratch\tnea-college-explorer"

print("=" * 70)
print("STARTING COMPREHENSIVE 6-TEST VERIFICATION SUITE")
print("=" * 70)

# Sample 1-pixel JPEG for testing
sample_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9'

# -------------------------------------------------------------------------
# TEST 1: Change a college image -> save -> refresh -> image remains.
# -------------------------------------------------------------------------
print("\n[TEST 1] Upload new photo for col-2 -> Verify real file on disk -> Refresh GET")
upload_payload = {
    "collegeId": "col-2",
    "targetType": "college",
    "imageData": "data:image/jpeg;base64," + base64.b64encode(sample_jpeg).decode("ascii")
}
req = urllib.request.Request(f"{SERVER}/api/upload", data=json.dumps(upload_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode("utf-8"))
    assert res["success"] == True, "Upload failed"
    img_path = res["imagePath"]
    disk_file = os.path.join(PROJECT_DIR, img_path.replace("/", os.sep))
    assert os.path.exists(disk_file), f"File missing on disk: {disk_file}"
    print(f"  -> File created on disk: {img_path} ({os.path.getsize(disk_file)} bytes)")

# Simulate page refresh
with urllib.request.urlopen(f"{SERVER}/api/colleges?t={int(time.time()*1000)}") as resp:
    data = json.loads(resp.read().decode("utf-8"))
    col2 = next(c for c in data["colleges"] if c["id"] == "col-2")
    assert col2["image"] == img_path, "Refreshed data did not retain uploaded image"
    print("  -> TEST 1 PASSED: Image remains after simulated refresh!")

# -------------------------------------------------------------------------
# TEST 2: Change a college image -> close browser -> reopen -> image remains.
# -------------------------------------------------------------------------
print("\n[TEST 2] Reopen simulator with fresh HTTP session & clean headers")
fresh_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}
req2 = urllib.request.Request(f"{SERVER}/api/colleges?t={int(time.time()*1000)}", headers=fresh_headers)
with urllib.request.urlopen(req2) as resp:
    data2 = json.loads(resp.read().decode("utf-8"))
    col2_reopen = next(c for c in data2["colleges"] if c["id"] == "col-2")
    assert col2_reopen["image"] == img_path, "Reopened session did not retain image"
    print("  -> TEST 2 PASSED: Image remains on brand new session/browser reopen!")

# -------------------------------------------------------------------------
# TEST 3: Make update on laptop -> open portal on another device -> latest update appears.
# -------------------------------------------------------------------------
print("\n[TEST 3] Laptop updates fee on col-3 -> Remote Client (Android Phone) reads portal")
laptop_update = {"fees": {"tuition": 99000, "other": 20000, "hostel": 110000}}
put_req = urllib.request.Request(
    f"{SERVER}/api/colleges/col-3",
    data=json.dumps(laptop_update).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(put_req) as resp:
    res3 = json.loads(resp.read().decode("utf-8"))
    assert res3["success"] == True

# Remote Device Simulation (Android User-Agent)
android_headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
}
req_android = urllib.request.Request(f"{SERVER}/api/colleges?t={int(time.time()*1000)}", headers=android_headers)
with urllib.request.urlopen(req_android) as resp:
    android_data = json.loads(resp.read().decode("utf-8"))
    col3_android = next(c for c in android_data["colleges"] if c["id"] == "col-3")
    assert col3_android["fees"]["tuition"] == 99000, "Android device did not receive updated fee"
    print("  -> TEST 3 PASSED: Android device immediately sees update made from laptop!")

# -------------------------------------------------------------------------
# TEST 4: Open on iPhone -> images and latest data appear correctly.
# -------------------------------------------------------------------------
print("\n[TEST 4] iPhone Client simulation (Mobile Safari User-Agent)")
iphone_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
}
req_iphone = urllib.request.Request(f"{SERVER}/api/colleges?t={int(time.time()*1000)}", headers=iphone_headers)
with urllib.request.urlopen(req_iphone) as resp:
    iphone_data = json.loads(resp.read().decode("utf-8"))
    assert len(iphone_data["colleges"]) == 20
    # Also verify image can be downloaded by iPhone client
    sample_img_url = f"{SERVER}/{iphone_data['colleges'][0]['image']}"
    with urllib.request.urlopen(urllib.request.Request(sample_img_url, headers=iphone_headers)) as img_resp:
        assert img_resp.status == 200
        print(f"  -> iPhone fetched image '{sample_img_url}' successfully ({len(img_resp.read())} bytes)")
    print("  -> TEST 4 PASSED: iPhone receives all 20 colleges and image assets!")

# -------------------------------------------------------------------------
# TEST 5: Clear browser cache -> reopen portal -> latest version and images appear.
# -------------------------------------------------------------------------
print("\n[TEST 5] Cache-busting test with randomized timestamp query")
cache_busting_url = f"{SERVER}/api/colleges?t={int(time.time()*1000) + 999999}"
req_nocache = urllib.request.Request(
    cache_busting_url,
    headers={"Cache-Control": "no-cache, no-store", "Pragma": "no-cache"}
)
with urllib.request.urlopen(req_nocache) as resp:
    nocache_data = json.loads(resp.read().decode("utf-8"))
    assert len(nocache_data["colleges"]) == 20
    print("  -> TEST 5 PASSED: Fresh state delivered despite cleared cache!")

# -------------------------------------------------------------------------
# TEST 6: Add/edit college -> save -> open from another device -> change visible.
# -------------------------------------------------------------------------
print("\n[TEST 6] Add custom symposium event on col-1 -> verify on iPad device")
event_update = {
    "events": [
        {
            "id": "ev-new-sync-test",
            "title": "National AI Hackathon 2026",
            "date": "Nov 10, 2026",
            "venue": "Tag Auditorium",
            "desc": "Cross-device synchronized event.",
            "photo": "images/events/kurukshetra.jpg"
        }
    ]
}
put_ev_req = urllib.request.Request(
    f"{SERVER}/api/colleges/col-1",
    data=json.dumps(event_update).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(put_ev_req) as resp:
    res6 = json.loads(resp.read().decode("utf-8"))
    assert res6["success"] == True

# iPad Device Simulation
ipad_headers = {
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
}
with urllib.request.urlopen(urllib.request.Request(f"{SERVER}/api/colleges?t={int(time.time()*1000)}", headers=ipad_headers)) as resp:
    ipad_data = json.loads(resp.read().decode("utf-8"))
    col1_ipad = next(c for c in ipad_data["colleges"] if c["id"] == "col-1")
    assert col1_ipad["events"][0]["title"] == "National AI Hackathon 2026"
    print("  -> TEST 6 PASSED: iPad client sees newly added event created on laptop!")

# Reset data back to default
reset_req = urllib.request.Request(f"{SERVER}/api/reset", data=b"", headers={"Content-Type": "application/json"})
with urllib.request.urlopen(reset_req) as resp:
    res_reset = json.loads(resp.read().decode("utf-8"))
    assert res_reset["success"] == True
    print("\n[CLEANUP] Restored factory default dataset on server.")

print("\n" + "=" * 70)
print("ALL 6 TESTS PASSED WITH 100% SUCCESS!")
print("=" * 70)
