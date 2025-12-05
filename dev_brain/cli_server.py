import uvicorn
import sys
import argparse

def main():
    """
    Starts the Dev Brain HTTP API server.
    """
    parser = argparse.ArgumentParser(description="Dev Brain API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    args = parser.parse_args()
    
    print(f"Starting Dev Brain API on {args.host}:{args.port}")
    uvicorn.run(
        "dev_brain.server:app",
        host=args.host,
        port=args.port,
        reload=False,
    )

if __name__ == "__main__":
    main()
