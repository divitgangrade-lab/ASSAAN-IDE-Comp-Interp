from __future__ import annotations
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
from .interpreter import run_file, check_file
from .transpiler import compile_file

ROOT = Path(__file__).resolve().parent.parent

def main():
    parser = argparse.ArgumentParser(prog="asaan", description="ASAAN language tools")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="Run an ASAAN source file")
    run.add_argument("file")
    comp = sub.add_parser("compile", help="Transpile ASAAN to Python")
    comp.add_argument("file")
    comp.add_argument("-o", "--output", default="build/output.py")
    chk = sub.add_parser("check", help="Check source syntax and structure")
    chk.add_argument("file")
    ide = sub.add_parser("ide", help="Start the browser IDE")
    ide.add_argument("--host", default="127.0.0.1")
    ide.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if args.command == "run":
        run_file(args.file)
    elif args.command == "compile":
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(compile_file(args.file), encoding="utf-8")
        print(f"Compiled {args.file} -> {out}")
    elif args.command == "check":
        check_file(args.file)
        print(f"OK: {args.file}")
    elif args.command == "ide":
        os.chdir(ROOT / "web")
        server = ThreadingHTTPServer((args.host, args.port), SimpleHTTPRequestHandler)
        print(f"ASAANIDE running at http://{args.host}:{args.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\\nShutting down ASAANIDE.")
        finally:
            server.server_close()

if __name__ == "__main__":
    main()
