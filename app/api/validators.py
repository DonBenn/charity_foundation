from datetime import datetime

from http import HTTPStatus
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MIN_FULL_AMOUNT_VALUE
from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_charity_project_exists(
        charity_project_id: int,
        session: AsyncSession,
) -> CharityProject:
    charity_project = await charity_project_crud.get(charity_project_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден!'
        )
    return charity_project


async def check_name_duplicate(
        charity_project_name: str,
        session: AsyncSession,
) -> None:
    project_id = await charity_project_crud.get_charity_project_by_name(
        charity_project_name, session)
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def check_full_amount(
        db_project: CharityProject,
        full_amount_to_upgrade: int,
        session: AsyncSession
) -> CharityProject:
    if full_amount_to_upgrade < db_project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нельзя установить требуемую сумму меньше уже вложенной',
        )
    if full_amount_to_upgrade == db_project.invested_amount:
        db_project.fully_invested = True
        db_project.close_date = datetime.now()
        session.add(db_project)
    return db_project


async def check_before_deletion(
        charity_project_id: int,
        session: AsyncSession,
) -> CharityProject:
    charity_project = await charity_project_crud.get(charity_project_id,
                                                     session)
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Удаление закрытых проектов запрещено',
        )
    if charity_project.invested_amount > MIN_FULL_AMOUNT_VALUE:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Запрещено удаление проектов, в которые уже внесены средства.',
        )
    return charity_project