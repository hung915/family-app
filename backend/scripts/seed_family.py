"""Seed the initial four family members.

Idempotent: each role is inserted only if no member with that role exists yet.

Run from backend/:
    uv run python -m scripts.seed_family
"""

import asyncio
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import select

from src.database import async_session_maker
from src.members.constants import MemberRole
from src.members.models import Member


@dataclass
class _Seed:
    first_name: str
    role: MemberRole
    nickname: str | None = None
    due_date: date | None = field(default=None)


# TODO: replace placeholder names with real ones before running.
_MEMBERS: list[_Seed] = [
    _Seed(first_name='Dad', role=MemberRole.FATHER),
    _Seed(first_name='Mom', role=MemberRole.MOTHER),
    _Seed(first_name='Big Sister', role=MemberRole.CHILD),
    _Seed(
        first_name='Baby',
        role=MemberRole.UNBORN,
        due_date=date(2026, 12, 15),  # TODO: set the real due date
    ),
]


async def seed() -> None:
    async with async_session_maker() as session:
        result = await session.execute(select(Member.role))
        existing: set[MemberRole] = set(result.scalars().all())

        to_add = [s for s in _MEMBERS if s.role not in existing]

        if not to_add:
            print('Nothing to do — all family members already exist.')
            return

        for s in to_add:
            session.add(
                Member(
                    first_name=s.first_name,
                    nickname=s.nickname,
                    role=s.role,
                    due_date=s.due_date,
                )
            )

        await session.commit()

        for s in to_add:
            label = f'{s.first_name} ({s.role})'
            if s.due_date:
                label += f' — due {s.due_date}'
            print(f'  ✓ {label}')

        print(f'\nSeeded {len(to_add)} member(s).')


if __name__ == '__main__':
    asyncio.run(seed())
