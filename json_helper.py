import json

def make_json_sender(handler):
    def send_json(status_code, data_dict):
        body_bytes = json.dumps(data_dict, ensure_ascii=False).encode('utf-8')
        handler.send_response(status_code)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Content-Length", str(len(body_bytes)))
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        handler.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
        handler.send_header("Pragma", "no-cache")
        handler.send_header("Expires", "0")
        handler.end_headers()
        handler.wfile.write(body_bytes)
        handler.wfile.flush()
    return send_json
