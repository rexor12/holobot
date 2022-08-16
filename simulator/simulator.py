import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from json import load
from json.encoder import JSONEncoder
from typing import Any

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def _json(self, json_object: dict[str, Any]):
        # NOTE: must return a bytes object!
        content = JSONEncoder().encode(json_object)
        return content.encode("utf8")

    def do_GET(self):
        self.send_response(429)
        self.send_header("Retry-After", "120")
        self.end_headers()
        return 0

        self._set_headers()
        with open("./simulator/responses/ticker-price.json") as file:
            return self.wfile.write(JSONEncoder().encode(load(file)).encode("utf8"))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write(self._json({ "result": "ok" }))

def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)
