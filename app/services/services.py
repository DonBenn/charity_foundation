from datetime import datetime

from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Donation
from app.models.charity_project import CharityProject
from app.schemas.donation import DonationCreate


async def calculate_donation(
        donation: int,
        session: AsyncSession
):
    open_projects = await session.execute(
        select(CharityProject)
        .where(CharityProject.fully_invested == False)
        .order_by(CharityProject.create_date.asc())
    )
    open_projects = open_projects.scalars().all()
    for open_project in open_projects:
        if open_project:
            needed_amount = open_project.full_amount - open_project.invested_amount
            if donation >= needed_amount:
                open_project.invested_amount = open_project.full_amount
                open_project.fully_invested = True
                open_project.close_date = datetime.now()
                donation -= needed_amount
                session.add(open_project)
            else:
                open_project.invested_amount += donation
                session.add(open_project)
                donation = 0
    return donation


async def add_to_donation(
        new_donation: Donation,
        donation: DonationCreate,
        calculated_donation: int,
        session: AsyncSession
):
    new_donation.invested_amount = donation.full_amount - calculated_donation
    if new_donation.invested_amount >= new_donation.full_amount:
        new_donation.fully_invested = True
        new_donation.close_date = datetime.now()
    session.add(new_donation)
    await session.commit()
    await session.refresh(new_donation)
    return new_donation


async def check_free_donations(
        charity_project: CharityProject,
        session: AsyncSession,
):
    open_donations = await session.execute(
        select(Donation)
        .where(and_(
            Donation.fully_invested == False,
        ))
    )
    open_donations = open_donations.scalars().all()
    for element in open_donations:
        free_donation = (element.full_amount - element.invested_amount)
        charity_project.invested_amount += free_donation

        if charity_project.invested_amount >= charity_project.full_amount:
            element.invested_amount += free_donation - (
                    charity_project.invested_amount - charity_project.full_amount)
            charity_project.invested_amount = charity_project.full_amount
            if element.invested_amount == element.full_amount:
                element.fully_invested = True
                element.close_date = datetime.now()
            charity_project.fully_invested = True
            charity_project.close_date = datetime.now()
            session.add_all([charity_project, element])
            break

        element.invested_amount += free_donation
        if element.invested_amount == element.full_amount:
            element.fully_invested = True
            element.close_date = datetime.now()
        session.add_all([charity_project, element])

    await session.commit()
    await session.refresh(charity_project)
    return charity_project
