from datetime import datetime
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal
from app.models import Donation, CharityProject
from app.models.charity_project import CharityProject
from app.schemas.charity_project import CharityProjectCreate, \
    CharityProjectUpdate, CharityProjectDB


async def make_donation(donation, session: AsyncSession):
    open_project = await session.execute(
        select(CharityProject)
        .where(CharityProject.fully_invested == False)
        .order_by(CharityProject.create_date.asc())
        .limit(1)
    )
    open_project = open_project.scalars().first()
    # open_project_id = open_project.scalars().first().id
    if open_project is None:
        close_project = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested == True)
            .order_by(CharityProject.create_date.asc())
            .limit(1)
        )
        close_project = close_project.scalars().first()
        close_project.invested_amount += donation.full_amount
        session.add(close_project)
        await session.commit()
        await session.refresh(close_project)
        return close_project
    open_project_id = open_project.id
    if open_project:
        open_project.invested_amount += donation.full_amount
        if open_project.invested_amount >= open_project.full_amount:
            open_project.fully_invested = True
            open_project.close_date = datetime.now()
            another_open_project = await session.execute(
                select(CharityProject)
                .where(CharityProject.fully_invested == False,
                       CharityProject.id != open_project_id
                       )
                .order_by(CharityProject.create_date.asc())
                .limit(1)
                )
            another_open_project = another_open_project.scalars().first()
            if another_open_project is None:
                session.add(open_project)
                await session.commit()
                await session.refresh(open_project)
                return open_project
            another_open_project.invested_amount += (open_project.invested_amount -
                                                     open_project.full_amount)
            session.add(open_project, another_open_project)
            await session.commit()
            await session.refresh(open_project, another_open_project)
            return open_project, another_open_project

        session.add(open_project)
        await session.commit()
        await session.refresh(open_project)
        return open_project

        return None
    return None





