from flask import Flask, request, Response
import requests
import base64

app = Flask(__name__)

@app.route('/')
def proxy():
    stream_url = request.args.get('url')
    data = request.args.get('data')

    if not stream_url or not data:
        return "Missing url or data", 400

    headers_raw = base64.b64decode(data).decode()
    headers = {}
    for pair in headers_raw.split('|'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            headers[key.strip()] = value.strip()

    try:
        r = requests.get(stream_url, headers=headers, stream=True)
        return Response(r.iter_content(chunk_size=8192), content_type=r.headers.get('Content-Type'))
    except Exception as e:
        return f"Fetch failed: {str(e)}", 500
