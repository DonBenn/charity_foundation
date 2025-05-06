from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import (
    create_charity_project, get_charity_project_by_name,
    get_charity_project_by_id, read_all_charity_projects_from_db,
    update_charity_project, delete_charity_project,
)
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
    return new_project

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

    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)

    charity_project = await check_full_amount(project_id, obj_in.full_amount, session)

    charity_project = await update_charity_project(charity_project, obj_in, session)
    return charity_project


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
        project_id: int,
        full_amount_to_upgrade: int,
        session: AsyncSession
):
    db_project = await session.execute(select(CharityProject).where(
        CharityProject.id == project_id)
    )
    db_project = db_project.scalar()
    if full_amount_to_upgrade < db_project.full_amount:
        raise HTTPException(
            status_code=400,
            detail='Нельзя установить требуемую сумму меньше уже вложенной',
        )
