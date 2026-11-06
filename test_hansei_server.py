"""Verify GET/HEAD representation semantics over the public HTTP interface."""
from http.server import ThreadingHTTPServer
from pathlib import Path
import socket
import threading
import unittest

from hansei_server import HanseiHandler


class HeadResponseTests(unittest.TestCase):
    def test_head_preserves_get_headers_without_wire_body(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), HanseiHandler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        cases = (
            ("/%2e%2e/secret", 400, b"Bad Request", "text/plain; charset=utf-8", "no-store"),
            ("/hansei.html", 200, Path(__file__).with_name("hansei.html").read_bytes(),
             "text/html; charset=utf-8", "no-cache"),
            ("/unknown", 404, b"Not Found", "text/plain; charset=utf-8", "no-store"),
        )
        try:
            for path, status, representation, mime, cache in cases:
                for method in ("GET", "HEAD"):
                    with self.subTest(path=path, method=method):
                        with socket.create_connection(server.server_address, timeout=2) as client:
                            client.sendall(
                                f"{method} {path} HTTP/1.1\r\nHost: localhost\r\n"
                                "Connection: close\r\n\r\n".encode("ascii")
                            )
                            chunks = []
                            while True:
                                chunk = client.recv(8192)
                                if not chunk:
                                    break
                                chunks.append(chunk)
                        head, body = b"".join(chunks).split(b"\r\n\r\n", 1)
                        lines = head.decode("iso-8859-1").split("\r\n")
                        protocol, actual_status, _ = lines[0].split(" ", 2)
                        headers = dict(
                            (name.lower(), value.strip())
                            for name, value in (line.split(":", 1) for line in lines[1:])
                        )
                        self.assertEqual(protocol, "HTTP/1.1")
                        self.assertEqual(int(actual_status), status)
                        self.assertEqual(headers["content-type"], mime)
                        self.assertEqual(headers["cache-control"], cache)
                        self.assertEqual(headers["content-length"], str(len(representation)))
                        self.assertEqual(body, representation if method == "GET" else b"")
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
