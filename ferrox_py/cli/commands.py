import argparse
from typing import Any

from ferrox_py.cli.code_factory import generate_module


def main() -> Any:
    parser = argparse.ArgumentParser(description="Ferrox-Py CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", aliases=["g"], help="Generate a new resource")
    gen_parser.add_argument("type", choices=["module", "controller", "provider"], help="Type[Any] of resource")
    gen_parser.add_argument("name", type=str, help="Name of the resource")

    # Command: serve
    serve_parser = subparsers.add_parser("serve", help="Start the development server")

    args = parser.parse_args()

    if args.command in ["generate", "g"]:
        if args.type == "module":
            generate_module(args.name)
        else:
            print(f"Scaffolding {args.type} {args.name}...")
    elif args.command == "serve":
        import uvicorn
        print("Starting Ferrox-Py server...")
        # Assuming app factory is in ferrox_py.core.builder
        uvicorn.run("ferrox_py.core.builder:create_app", host="0.0.0.0", port=8000, reload=True)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
