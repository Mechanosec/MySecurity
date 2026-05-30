#!/usr/bin/env python3
import argparse
from session import SessionManager
from server import TCPServer
from tui import C2App


def main() -> None:
    parser = argparse.ArgumentParser(description="FakeClicker C2 — multi-session reverse shell manager")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=4444, help="Listen port (default: 4444)")
    args = parser.parse_args()

    session_manager = SessionManager()
    app = C2App(session_manager)
    tcp_server = TCPServer(host=args.host, port=args.port, session_manager=session_manager, app=app)

    tcp_server.start()
    print(f"[*] Listening on {args.host}:{args.port}")
    app.run()


if __name__ == "__main__":
    main()
