"""Seed the tasks table from ``specs/seed-data.json``.

Idempotent: each record carries an explicit ``id``; we skip any record whose
id already exists, so running the script twice creates no duplicates.

Run with:  uv run python seed.py
"""

import asyncio
import json
from datetime import date
from pathlib import Path

from app.database import AsyncSessionLocal
from app.models.task import Task

# specs/ lives at the repo root, one level above backend/.
SEED_FILE = Path(__file__).resolve().parent.parent / "specs" / "seed-data.json"


def _load_records() -> list[dict]:
    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    return data["tasks"]


def _to_task(record: dict) -> Task:
    return Task(
        id=record["id"],
        title=record["title"],
        assigned_role=record["assignedRole"],
        state=record["state"],
        description=record.get("description", ""),
        created_at=date.fromisoformat(record["createdAt"]),
    )


async def seed() -> None:
    records = _load_records()
    inserted = 0
    skipped = 0

    async with AsyncSessionLocal() as session:
        for record in records:
            existing = await session.get(Task, record["id"])
            if existing is not None:
                skipped += 1
                continue
            session.add(_to_task(record))
            inserted += 1
        await session.commit()

    print(f"Seed complete: {inserted} inserted, {skipped} skipped (already present).")


if __name__ == "__main__":
    asyncio.run(seed())
