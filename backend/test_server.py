#!/usr/bin/env python
"""
Simple test server to verify backend works
"""
import uvicorn
import sys

if __name__ == "__main__":
    print("🚀 Starting test server...")
    try:
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n✅ Server stopped gracefully")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
