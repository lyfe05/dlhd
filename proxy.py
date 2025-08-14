from flask import Flask, request, Response
import requests
import base64
import os

app = Flask(__name__)

@app.route("/")
def proxy():
    # Extract query parameters
    url = request.args.get("url")
    data = request.args.get("data")

    if not url or not data:
        return "Missing 'url' or 'data' parameter", 400

    # Decode headers from base64
    try:
        decoded = base64.b64decode(data).decode("utf-8")
        headers = {}
        for pair in decoded.split("|"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                headers[key.strip()] = value.strip()
    except Exception as e:
        return f"Header decode error: {str(e)}", 400

    # Forward request with injected headers
    try:
        upstream = requests.get(url, headers=headers, stream=True, timeout=10)
        return Response(
            upstream.iter_content(chunk_size=1024),
            status=upstream.status_code,
            content_type=upstream.headers.get("Content-Type", "application/octet-stream")
        )
    except requests.exceptions.RequestException as e:
        return f"Upstream fetch error: {str(e)}", 502

# Required for Render deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
