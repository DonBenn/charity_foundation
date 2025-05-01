from fastapi import APIRouter, HTTPException

from app.crud.charity_project import create_charity_project, get_charity_project_by_name
from app.schemas.charity_project import CharityProjectCreate

router = APIRouter()


@router.post("/charity_project/")
async def create_charity_project(
        charity_project: CharityProjectCreate
):
    new_project = await get_charity_project_by_name(charity_project)
    if new_project is not None:
        raise HTTPException(
            status_code=422,
            detail='Проект с таким именем уже существует!',
        )
    new_project = await create_charity_project(charity_project)
    return new_project

