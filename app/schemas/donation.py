from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator, Extra

from app.core.constants import MIN_FULL_AMOUNT_VALUE


class DonationCreate(BaseModel):
    full_amount: int = Field(...)
    comment: Optional[str]

    @validator('full_amount')
    def check_from_create_date_later_than_now(cls, value):
        if value < MIN_FULL_AMOUNT_VALUE:
            raise ValueError(
                'Сумма должна быть больше 1'
            )
        return value

    class Config:
        extra = Extra.forbid


class DonationCreatedResponse(DonationCreate):
    full_amount: int = Field(...)
    comment: Optional[str]
    create_date: datetime
    id: int

    class Config:
        orm_mode = True


class DonationDB(BaseModel):
    id: int
    user_id: Optional[int]
    full_amount: int
    comment: str
    invested_amount: int
    fully_invested: bool
    create_date: datetime

    class Config:
        orm_mode = True
