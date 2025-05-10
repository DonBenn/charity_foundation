from datetime import datetime
from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field, validator, root_validator, Extra

from app.core.constants import MAX_PROJECT_NAME_LENGTH, MIN_FULL_AMOUNT_VALUE, \
    MIN_FIELD_LENGTH


class CharityProjectBase(BaseModel):
    name: str = Field(..., max_length=MAX_PROJECT_NAME_LENGTH)
    description: str = Field(...)
    full_amount: int = Field(...)

    @validator('full_amount')
    def check_full_amount(cls, value):
        if value < MIN_FULL_AMOUNT_VALUE:
            raise ValueError(
                'Сумма должна быть больше 1'
            )
        return value

    class Config:
        min_anystr_length = MIN_FIELD_LENGTH
        extra = Extra.forbid


class CharityProjectCreate(CharityProjectBase):
    pass


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: datetime = None

    class Config:
        orm_mode = True


class CharityProjectUpdate(CharityProjectBase):
    name: Optional[str] = Field(None, max_length=MAX_PROJECT_NAME_LENGTH)
    description: Optional[str] = None
    full_amount: Optional[int] = None

    @validator('name')
    def name_cannot_be_null(cls, value):
        if value is None:
            raise ValueError('Имя проекта не может быть пустым!')
        return value

    @root_validator(pre=True)
    def check_forbidden_fields(cls, values):
        forbidden_fields = {
            "invested_amount", "create_date", "close_date", "fully_invested"
        }
        for field in forbidden_fields:
            if field in values:
                raise HTTPException(
                    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                    detail=f'Нельзя изменять поле {field}',
                )
        return values