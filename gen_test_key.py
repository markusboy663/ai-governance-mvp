#!/usr/bin/env python3
"""Generate test API key for staging environment"""
import bcrypt

# Generate a test API key
raw_key = "test_key_staging_12345678901234"
hashed = bcrypt.hashpw(raw_key.encode(), bcrypt.gensalt()).decode()

print("Generated Test API Key")
print("=" * 70)
print(f"Raw Key (use in Bearer):  {raw_key}")
print(f"Hashed (store in DB):     {hashed}")
print("=" * 70)
print()
print("Example curl command:")
print(f'curl -X POST http://127.0.0.1:8000/v1/check \\')
print(f'  -H "Authorization: Bearer {raw_key}" \\')
print(f'  -H "Content-Type: application/json" \\')
print(f"  -d '{{\"model\":\"gpt-4\",\"operation\":\"classify\",\"metadata\":{{}}}}' ")
