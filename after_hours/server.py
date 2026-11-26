"""Local browser UI for After Hours. Standard library only.

    python -m after_hours.server                          # scripted mode, no model
    python -m after_hours.server --mode agent --provider vertex

Then open http://127.0.0.1:8000. One player per server; the game lives in memory.
"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from .agent import LIVE_PROVIDERS, require_settings
from .night import Night

STATIC = Path(__file__).parent / "static"
STATIC_FILES = {"sound.js": "text/javascript; charset=utf-8"}  # explicit list: nothing else is served


class Game:
    def __init__(self, mode: str, provider: str, truth: str = "A"):
        self.default_mode, self.provider, self.truth = mode, provider, truth
        self.night = Night(mode, provider, truth=truth)

    def handle(self, action: str, body: dict) -> dict:
        n = self.night
        if action == "new":
            self.night = n = Night(body.get("mode", self.default_mode), self.provider, truth=self.truth)
        elif action == "visit":
            n.visit(body["location"])
        elif action == "event":
            n.choose_event(body["choice"])
        elif action == "say":
            n.say(str(body["text"]))
        elif action == "option":
            n.choose_option(int(body["index"]))
        elif action == "deal":
            n.make_deal(body["deal"])
        elif action == "leave":
            n.leave()
        elif action == "finale":
            n.choose_finale(body["choice"])
        elif action != "state":
            raise ValueError("Unknown action.")
        if action in ("new", "state"):
            n.feed = list(n.history)  # redraw the whole night after a page load
        return n.snapshot()


def make_handler(game: Game):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: bytes, kind: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._send(200, (STATIC / "index.html").read_bytes(), "text/html; charset=utf-8")
            elif self.path.lstrip("/") in STATIC_FILES:
                name = self.path.lstrip("/")
                self._send(200, (STATIC / name).read_bytes(), STATIC_FILES[name])
            elif self.path == "/api/state":
                self._send(200, json.dumps(game.handle("state", {})).encode(), "application/json")
            else:
                self._send(404, b"Not found", "text/plain")

        def do_POST(self):
            if not self.path.startswith("/api/"):
                return self._send(404, b"Not found", "text/plain")
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}") if length else {}
                result = game.handle(self.path[5:], body)
                self._send(200, json.dumps(result).encode(), "application/json")
            except (ValueError, KeyError) as error:
                self._send(400, json.dumps({"error": str(error)}).encode(), "application/json")

        def log_message(self, *args):  # keep player text out of the terminal log
            pass

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="After Hours in your browser")
    parser.add_argument("--mode", choices=["agent", "scripted"], default="scripted")
    parser.add_argument("--provider", choices=LIVE_PROVIDERS, default="vertex")
    parser.add_argument("--truth", choices=["A", "B"], default="A",
                        help="mystery variant: A (main game) or B (second playtest night)")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.mode == "agent":
        require_settings(args.provider)
    server = HTTPServer(("127.0.0.1", args.port), make_handler(Game(args.mode, args.provider, args.truth)))
    print(f"After Hours ({args.mode} mode, truth {args.truth}) at http://127.0.0.1:{args.port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
