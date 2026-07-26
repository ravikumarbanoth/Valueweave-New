#!/usr/bin/env python3
"""
Run the ValueWeave API.

    python3 -m api                      # 127.0.0.1:8000
    python3 -m api --port 8080
    python3 -m api --route GET /graph   # invoke one route without binding a socket
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api import API_VERSION                       # noqa: E402
from api.app import Application, create_server    # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(prog="api", description="ValueWeave read-only REST API")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--route", nargs=2, metavar=("METHOD", "PATH"),
                    help="dispatch one request and print the JSON, without serving")
    args = ap.parse_args(argv)

    app = Application()

    if args.route:
        method, path = args.route
        query = path.split("?", 1)[1] if "?" in path else ""
        status, payload = app.handle(method, path.split("?", 1)[0], query)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if status < 400 else 1

    server = create_server(args.host, args.port, app)
    print(f"ValueWeave API {API_VERSION} — http://{args.host}:{args.port}")
    print(f"  {len(app.repo.entities)} entities, {len(app.repo.relationships)} "
          f"relationships, {len(app.repo.packages)} packages")
    print("  read-only; no authentication (see GET /version)")
    print("  routes: " + ", ".join(r.strip("^$").replace("/?", "") for r in app.routes()))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
