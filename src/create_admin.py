"""
One-time setup script to create or update the admin user.

Run from the src/ directory:
    python create_admin.py
"""

import asyncio
import getpass
import sys
import bcrypt
from sqlalchemy import select
from db.database import async_session, init_db
from db.models import AdminUser


async def main():
    await init_db()

    async with async_session() as session:
        existing = (await session.execute(
            select(AdminUser).where(AdminUser.username == "admin")
        )).scalar_one_or_none()

        action = "Update" if existing else "Create"
        print(f"{action} admin user")

        password = getpass.getpass("Enter new password: ")
        confirm = getpass.getpass("Confirm password: ")

        if password != confirm:
            print("Passwords do not match.")
            sys.exit(1)

        if len(password) < 8:
            print("Password must be at least 8 characters.")
            sys.exit(1)

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        if existing:
            existing.password_hash = hashed
        else:
            session.add(AdminUser(username="admin", password_hash=hashed))

        await session.commit()
        print(f"Admin user {'updated' if existing else 'created'} successfully.")


if __name__ == "__main__":
    asyncio.run(main())
