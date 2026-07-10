"""
app.db.engine
~~~~~~~~~~~~~

Per-tenant async SQLAlchemy engine factory.

Each tenant's data lives in its own SQLite file under
``{settings.db.data_dir}/{tenant_id}.db``.  Engines are cached in a
module-level dict so repeated calls for the same tenant reuse the
connection pool.

Usage::

    session = get_session("tenant_demo")
    async with session() as s:
        result = await s.execute(select(TransactionRecord))
"""

from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.db.models import Base

logger = logging.getLogger(__name__)

# Cache: tenant_id → engine
_engines: dict[str, AsyncEngine] = {}

# Cache: tenant_id → sessionmaker
_session_factories: dict[str, async_sessionmaker[AsyncSession]] = {}


def _db_path(tenant_id: str) -> Path:
    """Return the SQLite file path for a tenant."""
    return settings.db.data_path / f"{tenant_id}.db"


def _build_engine(tenant_id: str) -> AsyncEngine:
    """Create a new async engine for the given tenant."""
    db_file = _db_path(tenant_id)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    url = f"sqlite+aiosqlite:///{db_file}"
    engine = create_async_engine(
        url,
        echo=settings.db.echo_sql,
        # SQLite doesn't benefit from multiple connections but we keep
        # a small pool to avoid reconnection overhead.
        pool_pre_ping=True,
    )
    logger.info("Created async engine for tenant %s → %s", tenant_id, db_file)
    return engine


def get_engine(tenant_id: str) -> AsyncEngine:
    """Return (or create) the async engine for *tenant_id*."""
    if tenant_id not in _engines:
        _engines[tenant_id] = _build_engine(tenant_id)
    return _engines[tenant_id]


def get_session(tenant_id: str) -> async_sessionmaker[AsyncSession]:
    """Return an async session factory bound to the tenant's engine."""
    if tenant_id not in _session_factories:
        engine = get_engine(tenant_id)
        _session_factories[tenant_id] = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False,
        )
    return _session_factories[tenant_id]


async def init_tenant_db(tenant_id: str) -> None:
    """Create all tables for a tenant's database (idempotent)."""
    engine = get_engine(tenant_id)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Initialised database schema for tenant %s", tenant_id)


async def dispose_all() -> None:
    """Dispose every cached engine — call on shutdown."""
    for tid, engine in _engines.items():
        await engine.dispose()
        logger.debug("Disposed engine for tenant %s", tid)
    _engines.clear()
    _session_factories.clear()
