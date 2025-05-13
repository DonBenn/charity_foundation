from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_charity_project_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(CharityProject.name == project_name)
        )
        db_project_id = db_project_id.scalars().first()
        return db_project_id


    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession,
    ) -> list[dict[str, str, datetime]]:
        projects = await session.execute(
            select(
                CharityProject
            ).where(
                CharityProject.fully_invested.is_(True)
            )
        )
        projects = projects.scalars().all()
        data = []
        for element in projects:
            difference = element.close_date - element.create_date
            data.append(
                {'name': element.name,
                 'time': difference,
                 'description': element.description
                 }
            )
        data = sorted(data, key=lambda x: x['time'])
        return data


charity_project_crud = CRUDCharityProject(CharityProject)