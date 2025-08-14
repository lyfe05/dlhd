import requests
from flask import Flask, request, Response
from urllib.parse import urlparse

app = Flask(__name__)

# Optional: restrict which headers to forward
FORWARD_HEADERS = [
    "User-Agent", "Referer", "Origin", "Range", "Accept", "Accept-Encoding"
]

# Optional: force MIME types
MIME_OVERRIDES = {
    ".m3u8": "application/vnd.apple.mpegurl",
    ".ts": "video/mp2t"
}

def get_mime_type(url):
    for ext, mime in MIME_OVERRIDES.items():
        if url.endswith(ext):
            return mime
    return None

@app.route("/proxy")
def proxy():
    target = request.args.get("url")
    if not target:
        return "Missing 'url' parameter", 400

    try:
        headers = {k: v for k, v in request.headers.items() if k in FORWARD_HEADERS}
        upstream = requests.get(target, headers=headers, stream=True, timeout=10)

        # Log upstream status and headers
        print(f"[{upstream.status_code}] {target}")
        for k, v in upstream.headers.items():
            print(f"{k}: {v}")

        # Force MIME type if needed
        mime = get_mime_type(target) or upstream.headers.get("Content-Type", "application/octet-stream")

        def generate():
            for chunk in upstream.iter_content(chunk_size=8192):
                yield chunk

        resp = Response(generate(), status=upstream.status_code, content_type=mime)
        # Add CORS headers
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    except Exception as e:
        print(f"Error: {e}")
        return f"Proxy error: {str(e)}", 502

if __name__ == "__main__":
    app.run()
