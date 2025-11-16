import bcrypt
import secrets
import uuid
import asyncio
from sqlmodel import select
from db import AsyncSessionLocal
from models import APIKey, Customer

async def create_key_for_customer(customer_email: str):
    async with AsyncSessionLocal() as session:
        q = await session.exec(select(Customer).where(Customer.email == customer_email))
        customer = q.one_or_none()
        if not customer:
            # opprett kunde
            customer = Customer(id=str(uuid.uuid4()), name=customer_email.split("@")[0], email=customer_email)
            session.add(customer)
            await session.commit()
            await session.refresh(customer)

        # Generate key_id and secret separately
        key_id = str(uuid.uuid4())
        secret = secrets.token_urlsafe(32)
        
        # Only hash the secret part
        secret_hash = bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()
        
        # Full plaintext token: key_id.secret (shown once)
        plaintext_token = f"{key_id}.{secret}"
        
        # Store in DB
        api_key = APIKey(
            id=str(uuid.uuid4()),
            key_id=key_id,
            customer_id=customer.id,
            api_key_hash=secret_hash
        )
        session.add(api_key)
        await session.commit()
        
        print(f"✅ Created API key (plaintext show once): {plaintext_token}")
        print(f"📍 key_id (indexed): {key_id}")
        print(f"🔐 secret (hashed in DB): [bcrypt hash]")
        print(f"📋 Token format: <key_id>.<secret> for O(1) lookup")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_api_key.py alice@example.com")
        sys.exit(1)
    email = sys.argv[1]
    asyncio.run(create_key_for_customer(email))
