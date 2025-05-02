from typing import Optional

from pydantic import BaseModel, Field, validator


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str]


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(..., min_length=1, max_length=100)


class CharityProjectDB(CharityProjectCreate):
    id: int

    class Config:
        orm_mode = True

class CharityProjectUpdate(CharityProjectBase):
    pass

    @validator('name')
    def name_cannot_be_null(cls, value):
        if value is None:
            raise ValueError('Имя проекта не может быть пустым!')
        return value