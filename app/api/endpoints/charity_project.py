from typing import List

from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud.charity_project import (
    create_charity_project,
    get_charity_project_by_name,
    read_all_charity_projects_from_db
)
from app.schemas.charity_project import CharityProjectCreate, CharityProjectDB

router = APIRouter(prefix='/charity_project', tags=['Charity Project'])


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
)
async def create_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    new_project = await get_charity_project_by_name(charity_project, session)
    if new_project is not None:
        raise HTTPException(
            status_code=422,
            detail='Проект с таким именем уже существует!',
        )
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

