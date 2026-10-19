import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class HelloHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"<!doctype html><html><head><title>Hello</title></head><body><h1>Hello, World!</h1></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), HelloHandler)
    print(f"Listening on port {port}", flush=True)
    server.serve_forever()
