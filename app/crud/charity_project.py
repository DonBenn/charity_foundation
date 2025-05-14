from typing import Optional

from sqlalchemy import select, func
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
    ) -> list[dict[str, int]]:

        duration = func.julianday(CharityProject.close_date) - func.julianday(
            CharityProject.create_date).label('duration')
        query = (
            select(CharityProject)
            .add_columns(duration)
            .where(CharityProject.fully_invested.is_(True))
            .order_by(duration)
        )
        db_objects = await session.execute(query)
        return  db_objects.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)