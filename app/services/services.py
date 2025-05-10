from datetime import datetime
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Donation
from app.models.charity_project import CharityProject


async def invest(
        source: Union[CharityProject, Donation],
        targets: Union[list[CharityProject], list[Donation]],
        session: AsyncSession
):
    for target in targets:
        if source.fully_invested:
            break

        source_remaining = source.full_amount - source.invested_amount
        target_remaining = target.full_amount - target.invested_amount

        if source_remaining > target_remaining:
            target.invested_amount = target.full_amount
            target.fully_invested = True
            target.close_date = datetime.now()
            source.invested_amount += target_remaining
        elif source_remaining == target_remaining:
            target.invested_amount = target.full_amount
            source.invested_amount = source.full_amount
            target.fully_invested = True
            source.fully_invested = True
            target.close_date = datetime.now()
            source.close_date = datetime.now()
        else:
            source.fully_invested = True
            source.invested_amount = source.full_amount
            source.close_date = datetime.now()
            target.invested_amount += source_remaining

    await session.commit()
    await session.refresh(source)

    return source