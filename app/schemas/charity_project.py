from datetime import datetime

from pydantic import BaseModel, Field, validator, root_validator


class CharityProjectBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(...)
    full_amount: int = Field(...)

    class Config:
        title = 'Класс для приветствия'
        min_anystr_length = 2

class CharityProjectCreate(CharityProjectBase):
    pass

class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: datetime

    @validator('create_date')
    def check_from_create_date_later_than_now(cls, value):
        if value <= datetime.now():
            raise ValueError(
                'Время создания даты '
                'не может быть меньше текущего времени'
            )
        return value

    @root_validator(skip_on_failure=True)
    def check_from_create_before_to_close(cls, values):
        if values['create_date'] >= values['close_date']:
            raise ValueError(
                'Время начала создания '
                'не может быть больше времени окончания'
            )
        return values

    class Config:
        orm_mode = True

class CharityProjectUpdate(CharityProjectBase):
    pass

    @validator('name')
    def name_cannot_be_null(cls, value):
        if value is None:
            raise ValueError('Имя проекта не может быть пустым!')
        return value