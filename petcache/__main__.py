"""Entry point for running petcache as a module."""

import argparse
import sys
from pathlib import Path

import uvicorn

from .api import create_app


def main():
    """Main entry point for the petcache module."""
    parser = argparse.ArgumentParser(
        description="Run petcache server",
        prog="python -m petcache"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8909,
        help="Port to bind the server to (default: 8909)"
    )
    
    parser.add_argument(
        "--db-path",
        default="petcache.db",
        help="Path to the SQLite database file (default: petcache.db)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    # Validate database path
    db_path = Path(args.db_path)
    if db_path.parent != Path(".") and not db_path.parent.exists():
        print(f"Error: Directory '{db_path.parent}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Create the FastAPI app with the specified database path
    app = create_app(db_path=str(db_path))
    
    print("Starting petcache server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Database: {db_path.absolute()}")
    print(f"API docs: http://{args.host}:{args.port}/docs")
    
    # Run the server
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()