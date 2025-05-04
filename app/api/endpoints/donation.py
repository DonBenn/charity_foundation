from typing import List

from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.donation import create_donation, read_all_donations_from_db, get_by_user
from app.models import User, Donation
from app.schemas.donation import DonationCreate, DonationDB, DonationCreatedResponse

router = APIRouter()


@router.post(
    '/',
        response_model=DonationCreatedResponse,
        response_model_exclude_none=True
)
async def create_new_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
):
    new_donation = await create_donation(donation, session)
    return new_donation


@router.get(
    '/',
    response_model=List[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_donations(
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    all_donations = await read_all_donations_from_db(session)
    return all_donations


@router.get(
    '/my',
    response_model=list[DonationCreatedResponse],
    response_model_exclude={'user_id'},
)
async def get_my_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    """Получает список всех пожертвований для текущего пользователя."""
    donations = await get_by_user(
        session=session, user=user
    )
    return donations
