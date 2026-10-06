#!/usr/bin/env python3
"""
TNEA College Explorer - Persistent Backend & Synchronization Server
"""

import os
import sys
import json
import time
import socket
import shutil
import base64
import traceback
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
UPLOADS_DIR = os.path.join(IMAGES_DIR, "uploads")
DATA_FILE = os.path.join(DATA_DIR, "colleges.json")
DEFAULT_DATA_FILE = os.path.join(DATA_DIR, "colleges_default.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

if os.path.exists(DATA_FILE) and not os.path.exists(DEFAULT_DATA_FILE):
    shutil.copyfile(DATA_FILE, DEFAULT_DATA_FILE)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class TNEAApiHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _send_json(self, status_code, data_dict):
        try:
            body_bytes = json.dumps(data_dict, ensure_ascii=False).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body_bytes)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.send_header("Connection", "close")
            super().end_headers()
            self.wfile.write(body_bytes)
            self.wfile.flush()
        except Exception as e:
            print(f"[Error in _send_json] {e}")
            traceback.print_exc()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Connection", "close")
        super().end_headers()

    def do_GET(self):
        try:
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path

            if path == "/" or path == "":
                self.path = "/index.html"
                return super().do_GET()

            if path == "/api/colleges":
                self._handle_get_colleges()
                return

            if path == "/api/status":
                self._handle_get_status()
                return

            return super().do_GET()
        except Exception as e:
            print(f"[Error in do_GET] {e}")
            traceback.print_exc()
            self._send_json(500, {"error": str(e)})

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, must-revalidate")
        super().end_headers()

    def do_POST(self):
        try:
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path

            if path == "/api/upload":
                self._handle_upload_image()
                return

            if path == "/api/colleges":
                self._handle_update_all_colleges()
                return

            if path == "/api/reset":
                self._handle_reset_data()
                return

            self._send_json(404, {"error": "Endpoint not found"})
        except Exception as e:
            print(f"[Error in do_POST] {e}")
            traceback.print_exc()
            self._send_json(500, {"error": str(e)})

    def do_PUT(self):
        try:
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path

            if path.startswith("/api/colleges/"):
                college_id = path.split("/")[-1]
                self._handle_update_single_college(college_id)
                return

            self._send_json(404, {"error": "Endpoint not found"})
        except Exception as e:
            print(f"[Error in do_PUT] {e}")
            traceback.print_exc()
            self._send_json(500, {"error": str(e)})

    # =========================================================================
    # API HANDLERS
    # =========================================================================

    def _read_colleges_data(self):
        if not os.path.exists(DATA_FILE):
            if os.path.exists(DEFAULT_DATA_FILE):
                shutil.copyfile(DEFAULT_DATA_FILE, DATA_FILE)
            else:
                return []
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Error] Failed to read {DATA_FILE}: {e}")
            return []

    def _write_colleges_data(self, data):
        try:
            temp_file = DATA_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(temp_file, DATA_FILE)
            return True
        except Exception as e:
            print(f"[Error] Failed to write {DATA_FILE}: {e}")
            return False

    def _handle_get_colleges(self):
        data = self._read_colleges_data()
        response_payload = {
            "success": True,
            "timestamp": int(time.time() * 1000),
            "count": len(data),
            "colleges": data
        }
        self._send_json(200, response_payload)

    def _handle_get_status(self):
        data = self._read_colleges_data()
        payload = {
            "status": "online",
            "serverTime": int(time.time() * 1000),
            "collegeCount": len(data),
            "uploadsDir": UPLOADS_DIR
        }
        self._send_json(200, payload)

    def _handle_update_all_colleges(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            req_data = json.loads(body)
            colleges_list = req_data.get("colleges", req_data) if isinstance(req_data, dict) else req_data
            if isinstance(colleges_list, list):
                if self._write_colleges_data(colleges_list):
                    self._send_json(200, {"success": True, "message": "All college data updated permanently on server!"})
                    return
            raise ValueError("Expected an array of colleges")
        except Exception as e:
            self._send_json(400, {"success": False, "error": str(e)})

    def _handle_update_single_college(self, college_id):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            update_data = json.loads(body)
            colleges = self._read_colleges_data()
            found = False
            for idx, c in enumerate(colleges):
                if c.get("id") == college_id or c.get("code") == college_id:
                    for key, val in update_data.items():
                        c[key] = val
                    colleges[idx] = c
                    found = True
                    break
            
            if not found and "id" in update_data and "name" in update_data:
                colleges.append(update_data)
                found = True

            if found:
                self._write_colleges_data(colleges)
                self._send_json(200, {"success": True, "message": f"College {college_id} updated permanently on server!"})
            else:
                self._send_json(404, {"success": False, "error": f"College {college_id} not found"})
        except Exception as e:
            self._send_json(400, {"success": False, "error": str(e)})

    def _handle_upload_image(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        content_type = self.headers.get("Content-Type", "")
        
        try:
            college_id = None
            event_id = None
            target_type = "college"
            img_bytes = None
            ext = ".jpg"

            if "application/json" in content_type:
                data = json.loads(body.decode("utf-8"))
                college_id = data.get("collegeId")
                event_id = data.get("eventId")
                target_type = data.get("targetType", "college")
                base64_data = data.get("imageData", "")

                if "," in base64_data:
                    header, base64_data = base64_data.split(",", 1)
                    if "image/png" in header:
                        ext = ".png"
                    elif "image/webp" in header:
                        ext = ".webp"

                img_bytes = base64.b64decode(base64_data)

            elif "multipart/form-data" in content_type:
                boundary = content_type.split("boundary=")[1].encode("utf-8")
                parts = body.split(b"--" + boundary)
                for part in parts:
                    if b'name="collegeId"' in part:
                        college_id = part.split(b"\r\n\r\n")[1].split(b"\r\n")[0].decode("utf-8").strip()
                    elif b'name="eventId"' in part:
                        event_id = part.split(b"\r\n\r\n")[1].split(b"\r\n")[0].decode("utf-8").strip()
                    elif b'name="targetType"' in part:
                        target_type = part.split(b"\r\n\r\n")[1].split(b"\r\n")[0].decode("utf-8").strip()
                    elif b'filename="' in part:
                        if b".png" in part:
                            ext = ".png"
                        elif b".webp" in part:
                            ext = ".webp"
                        img_bytes = part.split(b"\r\n\r\n")[1].rsplit(b"\r\n", 1)[0]

            if not img_bytes or len(img_bytes) < 10:
                raise ValueError("No valid image data received")

            timestamp = int(time.time())
            safe_cid = (college_id or "custom").replace("/", "_").replace("\\", "_")
            if target_type == "event" and event_id:
                safe_eid = event_id.replace("/", "_").replace("\\", "_")
                filename = f"event_{safe_cid}_{safe_eid}_{timestamp}{ext}"
            else:
                filename = f"college_{safe_cid}_{timestamp}{ext}"

            file_path = os.path.join(UPLOADS_DIR, filename)
            relative_url = f"images/uploads/{filename}"

            with open(file_path, "wb") as f:
                f.write(img_bytes)

            print(f"[Upload] Saved image to disk: {file_path} ({len(img_bytes)} bytes)")

            colleges = self._read_colleges_data()
            updated = False
            for c in colleges:
                if c.get("id") == college_id or c.get("code") == college_id:
                    if target_type == "event" and event_id:
                        for ev in c.get("events", []):
                            if ev.get("id") == event_id:
                                ev["photo"] = relative_url
                                ev["image"] = relative_url
                                updated = True
                                break
                    else:
                        c["image"] = relative_url
                        updated = True
                    break

            if updated:
                self._write_colleges_data(colleges)

            response = {
                "success": True,
                "imagePath": relative_url,
                "message": "Image saved as a permanent project file on disk and synchronized with database!"
            }
            self._send_json(200, response)

        except Exception as e:
            print(f"[Upload Error] {e}")
            traceback.print_exc()
            self._send_json(400, {"success": False, "error": str(e)})

    def _handle_reset_data(self):
        if os.path.exists(DEFAULT_DATA_FILE):
            shutil.copyfile(DEFAULT_DATA_FILE, DATA_FILE)
            self._send_json(200, {"success": True, "message": "Reset to default dataset successfully"})
        else:
            self._send_json(500, {"success": False, "error": "Default dataset backup not found"})

def get_local_ip_addresses():
    ip_list = []
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127."):
                ip_list.append(ip)
    except Exception:
        pass
    if not ip_list:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_list.append(s.getsockname()[0])
            s.close()
        except Exception:
            ip_list.append("127.0.0.1")
    return ip_list

def run_server(port=8000):
    server_address = ("", port)
    httpd = ThreadedHTTPServer(server_address, TNEAApiHandler)
    ips = get_local_ip_addresses()

    print("=" * 70)
    print(">> TNEA COLLEGE EXPLORER - PERSISTENT SERVER RUNNING")
    print("=" * 70)
    print(f"[*] Local Laptop URL:        http://localhost:{port}")
    for ip in ips:
        print(f"[*] Mobile Phone / Wi-Fi:    http://{ip}:{port}")
    print("-" * 70)
    print(f"[*] Persistent Data Source:  {DATA_FILE}")
    print(f"[*] Image Storage Folder:    {UPLOADS_DIR}")
    print("=" * 70)
    print("Press Ctrl+C to stop the server.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
