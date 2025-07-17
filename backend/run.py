#!/usr/bin/env python3
"""
Startup script for the Job Dashboard Backend API

This script provides an easy way to start the FastAPI server with proper configuration.
"""

import uvicorn
import argparse
import os
from pathlib import Path

def main():
    """Main function to start the FastAPI server"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Start the Job Dashboard Backend API')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    parser.add_argument('--log-level', default='info', 
                       choices=['critical', 'error', 'warning', 'info', 'debug'],
                       help='Log level (default: info)')
    
    args = parser.parse_args()
    
    # Environment variable overrides
    host = os.getenv('HOST', args.host)
    port = int(os.getenv('PORT', args.port))
    log_level = os.getenv('LOG_LEVEL', args.log_level).lower()
    
    # Ensure we're in the right directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🚀 Starting Job Dashboard Backend API")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"📊 Log Level: {log_level}")
    print(f"🔄 Auto-reload: {'Enabled' if args.reload else 'Disabled'}")
    print("-" * 50)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,  # Workers incompatible with reload
        access_log=True
    )

if __name__ == "__main__":
    main()