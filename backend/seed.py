"""
One-time seed script: creates F3 Growth tenant, admin user, and default config.
Idempotent — safe to run multiple times.

Usage: cd backend && python seed.py
Requires DATABASE_URL environment variable.
"""

import asyncio
import os

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models.tenant import WwTenant, WwUser
from services.seed import seed_f3_growth

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/whitewhale",
)

TENANT_NAME = "F3 Growth"
TENANT_SLUG = "f3-growth"
TENANT_PLAN = "pro"

ADMIN_EMAIL = "rdaggett@f3growth.com"
ADMIN_PASSWORD = "password"
ADMIN_NAME = "R Daggett"
ADMIN_ROLE = "owner"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def run_seed():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Check for existing tenant
        result = await db.execute(select(WwTenant).where(WwTenant.slug == TENANT_SLUG))
        tenant = result.scalar_one_or_none()

        if tenant:
            print(f"Tenant '{TENANT_NAME}' already exists (id={tenant.id})")
        else:
            tenant = WwTenant(name=TENANT_NAME, slug=TENANT_SLUG, plan=TENANT_PLAN)
            db.add(tenant)
            await db.flush()
            print(f"Created tenant '{TENANT_NAME}' (id={tenant.id})")

        # Check for existing user
        result = await db.execute(select(WwUser).where(WwUser.email == ADMIN_EMAIL))
        user = result.scalar_one_or_none()

        if user:
            print(f"Admin user '{ADMIN_EMAIL}' already exists (id={user.id})")
        else:
            user = WwUser(
                tenant_id=tenant.id,
                email=ADMIN_EMAIL,
                hashed_password=hash_password(ADMIN_PASSWORD),
                full_name=ADMIN_NAME,
                role=ADMIN_ROLE,
            )
            db.add(user)
            await db.flush()
            print(f"Created admin user '{ADMIN_EMAIL}' (id={user.id})")

        # Seed F3 Growth config (idempotent — checks handled inside)
        try:
            await seed_f3_growth(db, tenant.id)
            print("Seeded F3 Growth config (ICP, categories, personas, angles, voices, constraints, routing rules)")
        except Exception as e:
            print(f"Seed config skipped or failed: {e}")

        await db.commit()
        print("Done.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_seed())
