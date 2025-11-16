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

        raw_key = "api_" + secrets.token_urlsafe(32)
        hashed = bcrypt.hashpw(raw_key.encode(), bcrypt.gensalt()).decode()
        api_key = APIKey(id=str(uuid.uuid4()), customer_id=customer.id, api_key_hash=hashed)
        session.add(api_key)
        await session.commit()
        print("Created API key (plaintext show once):", raw_key)
        print("Store hashed key in DB only.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_api_key.py alice@example.com")
        sys.exit(1)
    email = sys.argv[1]
    asyncio.run(create_key_for_customer(email))
