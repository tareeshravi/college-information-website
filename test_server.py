import urllib.request
import json
import base64
import os

server = "http://127.0.0.1:8000"

# 1-pixel sample JPEG
sample_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9'

payload = {
    "collegeId": "col-1",
    "targetType": "college",
    "imageData": "data:image/jpeg;base64," + base64.b64encode(sample_jpeg).decode("ascii")
}

# Test 1: Upload Image
req = urllib.request.Request(
    f"{server}/api/upload",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode("utf-8"))
    print("Test 1 (Upload Image):", res)
    assert res["success"] == True
    img_path = res["imagePath"]
    full_p = os.path.join(r"C:\Users\TAREESHRAVI\.gemini\antigravity\scratch\tnea-college-explorer", img_path.replace("/", os.sep))
    assert os.path.exists(full_p)
    print("  -> Verified image file created on disk at:", full_p)

# Test 2: Verify GET reflects the image
with urllib.request.urlopen(f"{server}/api/colleges") as resp:
    data = json.loads(resp.read().decode("utf-8"))
    col1 = next(c for c in data["colleges"] if c["id"] == "col-1")
    print("Test 2 (GET reflected):", col1["image"])
    assert col1["image"] == img_path

# Test 3: PUT Fee update
update_payload = {"fees": {"tuition": 60000, "other": 15000, "hostel": 80000}}
put_req = urllib.request.Request(
    f"{server}/api/colleges/col-1",
    data=json.dumps(update_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(put_req) as resp:
    res = json.loads(resp.read().decode("utf-8"))
    print("Test 3 (PUT Fees):", res)

# Test 4: Reset data back to default
reset_req = urllib.request.Request(f"{server}/api/reset", data=b"", headers={"Content-Type": "application/json"})
with urllib.request.urlopen(reset_req) as resp:
    res = json.loads(resp.read().decode("utf-8"))
    print("Test 4 (Reset Data):", res)

# Test 5: Verify default restored
with urllib.request.urlopen(f"{server}/api/colleges") as resp:
    data = json.loads(resp.read().decode("utf-8"))
    col1 = next(c for c in data["colleges"] if c["id"] == "col-1")
    print("Test 5 (Verify default restored):", col1["image"])
    assert col1["image"] == "images/ceg-anna-univ.jpg"

print("\nALL 5 BACKEND API & DISK STORAGE TESTS PASSED 100%!")
