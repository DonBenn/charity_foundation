from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator, root_validator, Extra


class CharityProjectBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(...)
    full_amount: int = Field(...)

    @validator('full_amount')
    def check_full_amount(cls, value):
        if value < 1:
            raise ValueError(
                'Сумма должна быть больше 1'
            )
        return value

    class Config:
        min_anystr_length = 2
        extra = Extra.forbid

class CharityProjectCreate(CharityProjectBase):
    pass

class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime

    class Config:
        orm_mode = True

class CharityProjectUpdate(CharityProjectBase):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    full_amount: Optional[int] = None

    @validator('name')
    def name_cannot_be_null(cls, value):
        if value is None:
            raise ValueError('Имя проекта не может быть пустым!')
        return value