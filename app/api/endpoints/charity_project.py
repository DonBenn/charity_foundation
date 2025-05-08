from datetime import datetime
from symbol import and_expr
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, and_

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import (
    create_charity_project, get_charity_project_by_name,
    get_charity_project_by_id, read_all_charity_projects_from_db,
    update_charity_project, delete_charity_project,
)
from app.models import Donation
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.models.charity_project import CharityProject


router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    await check_name_duplicate(charity_project.name, session)
    new_project = await create_charity_project(charity_project, session)
    check_donations = await check_donations_condition(new_project, session)
    return check_donations

@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    all_charity_projects = await read_all_charity_projects_from_db(session)
    return all_charity_projects


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    charity_project = await check_charity_project_exists(project_id, session)
    check_project = await check_closed_or_invested_for_upgrade(project_id, session)

    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)

    if obj_in.full_amount is not None:
        charity_project = await check_full_amount(charity_project, obj_in.full_amount, session)

    return await update_charity_project(charity_project, obj_in, session)


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    charity_project = await check_charity_project_exists(project_id, session)

    check_project = await check_closed_or_invested_project_for_deletion(project_id, session)

    charity_project = await delete_charity_project(charity_project, session)
    return charity_project


async def check_charity_project_exists(
        charity_project_id: int,
        session: AsyncSession,
) -> CharityProject:
    charity_project = await get_charity_project_by_id(charity_project_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=404,
            detail='Проект не найден!'
        )
    return charity_project


async def check_name_duplicate(
        charity_project_name: str,
        session: AsyncSession,
) -> None:
    project_id = await get_charity_project_by_name(charity_project_name, session)
    if project_id is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )

async def check_full_amount(
        db_project: CharityProject,
        full_amount_to_upgrade: int,
        session: AsyncSession
):
    if full_amount_to_upgrade < db_project.invested_amount:
        raise HTTPException(
            status_code=400,
            detail='Нельзя установить требуемую сумму меньше уже вложенной',
        )
    if full_amount_to_upgrade == db_project.invested_amount:
        db_project.fully_invested = True
        db_project.close_date = datetime.now()
        session.add(db_project)
    return db_project


async def check_closed_or_invested_project_for_deletion(
        project_id: int,
        session: AsyncSession,
):
    closed_project = await session.execute(select(CharityProject).where(
        CharityProject.id == project_id)
    )
    closed_project = closed_project.scalar()
    if closed_project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Удаление закрытых проектов запрещено',
        )
    if closed_project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail='Запрещено удаление проектов, в которые уже внесены средства.',
        )

async def check_closed_or_invested_for_upgrade(
        project_id: int,
        session: AsyncSession,
):
    closed_project = await session.execute(select(CharityProject).where(
        CharityProject.id == project_id)
    )
    closed_project = closed_project.scalar()
    if closed_project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Нельзя редактировать закрытый проект',
        )

async def check_donations_condition(
        charity_project,
        session: AsyncSession,
):
    free_donations = await session.execute(
        select(Donation)
        .where(and_(
            Donation.fully_invested == False,
        ))
    )
    free_donations = free_donations.scalars().all()
    total = 0
    needed_amount = charity_project.full_amount
    for element in free_donations:
        total = (element.full_amount - element.invested_amount)
        if charity_project.invested_amount == needed_amount or (
                charity_project.invested_amount > needed_amount):
            element.invested_amount += total - (
                    charity_project.invested_amount - charity_project.full_amount)
            charity_project.invested_amount = charity_project.full_amount
            charity_project.fully_invested = True
            charity_project.close_date = datetime.now()
            session.add_all([charity_project, element])
            break
        if charity_project.invested_amount < needed_amount:
            charity_project.invested_amount += total
            element.invested_amount += total
            if element.invested_amount == element.full_amount:
                element.fully_invested = True
                element.close_date = datetime.now()
                session.add(element)

    await session.commit()
    await session.refresh(charity_project)
    return charity_project
