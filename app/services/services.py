from datetime import datetime

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject


async def make_donation(donation, session: AsyncSession):
    open_project = await session.execute(
        select(CharityProject)
        .where(CharityProject.fully_invested == False)
        .order_by(CharityProject.create_date.asc())
        .limit(1)
    )
    open_project = open_project.scalars().first()
    if open_project is None:
        return None

    if open_project:
        needed_amount = open_project.full_amount - open_project.invested_amount
        if donation.full_amount >= needed_amount:
            open_project.invested_amount = open_project.full_amount
            open_project.fully_invested = True
            open_project.close_date = datetime.now()
            difference = donation.full_amount - needed_amount
            session.add(open_project)
            # await session.commit()
            # await session.refresh(open_project)
            return difference
        else:
            open_project.invested_amount += donation.full_amount
            session.add(open_project)
            # await session.commit()
            # await session.refresh(open_project)
            return True
        # return None
    return None





