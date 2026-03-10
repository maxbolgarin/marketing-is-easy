"""Create or update the API admin user.

Usage:
    python -m scripts.create_admin [username] [password]
    # Or uses API_DEFAULT_ADMIN_USERNAME / API_DEFAULT_ADMIN_PASSWORD from .env
"""

from __future__ import annotations

import asyncio
import sys
import uuid

from sqlalchemy import select

from src.api.auth import hash_password
from src.config.settings import settings
from src.db.models import ApiUser, async_session


async def main():
    username = sys.argv[1] if len(sys.argv) > 1 else settings.api_default_admin_username
    password = sys.argv[2] if len(sys.argv) > 2 else settings.api_default_admin_password

    if not password:
        print("Error: No password provided. Set API_DEFAULT_ADMIN_PASSWORD or pass as argument.")
        sys.exit(1)

    async with async_session() as session:
        stmt = select(ApiUser).where(ApiUser.username == username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            user.password_hash = hash_password(password)
            await session.commit()
            print(f"Updated password for user '{username}'")
        else:
            user = ApiUser(
                id=uuid.uuid4(),
                username=username,
                password_hash=hash_password(password),
                display_name="Admin",
            )
            session.add(user)
            await session.commit()
            print(f"Created admin user '{username}'")


if __name__ == "__main__":
    asyncio.run(main())
