from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal
from app.models.charity_project import CharityProject
from app.schemas.charity_project import CharityProjectCreate, \
    CharityProjectUpdate, CharityProjectDB


async def create_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession,
) -> CharityProject:
    new_project = charity_project.dict()
    db_project = CharityProject(**new_project)
    session.add(db_project)
    await session.commit()
    await session.refresh(db_project)
    return db_project


async def get_charity_project_by_name(
    project_name: str,
    session: AsyncSession,
) -> Optional[int]:
    db_project_id = await session.execute(
        select(CharityProject.id).where(CharityProject.name == project_name)
    )
    db_project_id = db_project_id.scalar() #.first()
    return db_project_id


async def read_all_charity_projects_from_db(
        session: AsyncSession,
) -> list[CharityProject]:
    charity_projects = await session.execute(select(CharityProject))
    return charity_projects.scalars().all()


async def get_charity_project_by_id(
        session: AsyncSession,
        charity_id: int,
) -> Optional[CharityProject]:
    db_project = await session.execute(select(CharityProject).where(
        CharityProject.id == charity_id)
    )
    db_project = db_project.scalar().first()
    return db_project


async def update_charity_project(
        db_project: CharityProject,
        project_update: CharityProjectUpdate,
        session: AsyncSession,
) -> CharityProject:
    obj_data = jsonable_encoder(db_project)
    update_data = project_update.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_project, field, update_data[field])
    session.add(db_project)
    await session.commit()
    await session.refresh(db_project)
    return db_project


async def delete_charity_project(
        db_project: CharityProject,
        session: AsyncSession,
) -> CharityProject:
    await session.delete(db_project)
    await session.commit()
    return db_project