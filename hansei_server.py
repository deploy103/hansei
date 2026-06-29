#!/usr/bin/env python3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
from urllib.parse import unquote, urlsplit


HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "3011"))
ROOT = Path(__file__).resolve().parent

FILES = {
    "/hansei.html": ("hansei.html", "text/html; charset=utf-8"),
    "/hansei.css": ("hansei.css", "text/css; charset=utf-8"),
    "/hansei.js": ("hansei.js", "text/javascript; charset=utf-8"),
    "/hansei.webmanifest": ("hansei.webmanifest", "application/manifest+json; charset=utf-8"),
    "/favicon.svg": ("favicon.svg", "image/svg+xml"),
    "/hansei_logo.jpg": ("hansei_logo.jpg", "image/jpeg"),
}

ROUTES = {
    "/": "/hansei.html",
    "/index.html": "/hansei.html",
    "/hansei": "/hansei.html",
}

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "; ".join(
        [
            "default-src 'self'",
            "script-src 'self' https://unpkg.com",
            "style-src 'self'",
            "img-src 'self' data:",
            "font-src 'self' data:",
            "connect-src 'none'",
            "object-src 'none'",
            "base-uri 'none'",
            "form-action 'none'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests",
        ]
    ),
}


class HanseiHandler(BaseHTTPRequestHandler):
    server_version = "HanseiPortal/1.0"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        self.handle_static(include_body=True)

    def do_HEAD(self):
        self.handle_static(include_body=False)

    def do_POST(self):
        self.method_not_allowed()

    def do_OPTIONS(self):
        self.method_not_allowed()

    def do_PUT(self):
        self.method_not_allowed()

    def do_PATCH(self):
        self.method_not_allowed()

    def do_DELETE(self):
        self.method_not_allowed()

    def method_not_allowed(self):
        self.send_text(HTTPStatus.METHOD_NOT_ALLOWED, "Method Not Allowed")

    def handle_static(self, include_body):
        request_path = self.get_request_path()
        if not request_path:
            self.send_text(HTTPStatus.BAD_REQUEST, "Bad Request")
            return

        if request_path == "/healthz":
            self.send_text(HTTPStatus.OK, "ok", include_body=include_body)
            return

        route = ROUTES.get(request_path, request_path)
        file_info = FILES.get(route)
        if not file_info:
            self.send_text(HTTPStatus.NOT_FOUND, "Not Found", include_body=include_body)
            return

        file_name, content_type = file_info
        file_path = (ROOT / file_name).resolve()
        if ROOT not in file_path.parents and file_path != ROOT:
            self.send_text(HTTPStatus.FORBIDDEN, "Forbidden", include_body=include_body)
            return

        try:
            data = file_path.read_bytes()
        except OSError:
            self.send_text(HTTPStatus.NOT_FOUND, "Not Found", include_body=include_body)
            return

        self.send_response(HTTPStatus.OK)
        self.send_security_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        cache_control = "no-cache" if file_name.endswith(".html") else "public, max-age=300, must-revalidate"
        self.send_header("Cache-Control", cache_control)
        self.end_headers()

        if include_body:
            self.wfile.write(data)

    def get_request_path(self):
        try:
            path = unquote(urlsplit(self.path).path)
        except ValueError:
            return ""

        if "\x00" in path or ".." in path:
            return ""

        return path.rstrip("/") or "/"

    def send_text(self, status, message, include_body=True):
        data = message.encode("utf-8")
        self.send_response(status)
        self.send_security_headers()
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()

        if include_body:
            self.wfile.write(data)

    def send_security_headers(self):
        for name, value in SECURITY_HEADERS.items():
            self.send_header(name, value)

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args), flush=True)

    def version_string(self):
        return self.server_version


def main():
    server = ThreadingHTTPServer((HOST, PORT), HanseiHandler)
    print(f"hansei portal listening on http://{HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
