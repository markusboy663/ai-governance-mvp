#!/usr/bin/env python
"""Start backend server from project root"""
import os
import sys

# Change to backend directory
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

# Add backend to path
sys.path.insert(0, '.')

# Import and run uvicorn
import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        loop='asyncio',
        log_level='info'
    )
