from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Donation
from app.schemas.donation import DonationCreate, DonationDB, DonationCreatedResponse


async def create_donation(
        donation: DonationCreate,
        session: AsyncSession,
        user: Optional[User] = None
) -> Donation:
    new_donation = donation.dict()
    if user is not None:
        new_donation['user_id'] = user.id
    db_donation = Donation(**new_donation)
    session.add(db_donation)
    await session.commit()
    await session.refresh(db_donation)
    return db_donation


async def get_by_user(
        session: AsyncSession,
        user: User
):
    donations = await session.execute(
        select(Donation).where(
            Donation.user_id == user.id
        )
    )
    return donations.scalars().all()


async def read_all_donations_from_db(
        session: AsyncSession,
) -> list[DonationDB]:
    donations = await session.execute(select(Donation))
    return donations.scalars().all()