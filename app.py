import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

INDEX_HTML = (Path(__file__).parent / "index.html").read_bytes()


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type, include_body=True):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def _route(self, include_body):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self._send(200, INDEX_HTML, "text/html; charset=utf-8", include_body)
        elif path == "/healthz":
            self._send(200, b"ok", "text/plain; charset=utf-8", include_body)
        else:
            self._send(404, b"<h1>404 - Not Found</h1>", "text/html; charset=utf-8", include_body)

    def do_GET(self):
        self._route(include_body=True)

    def do_HEAD(self):
        self._route(include_body=False)


HTTPServer(("", int(os.environ.get("PORT", 8080))), Handler).serve_forever()
