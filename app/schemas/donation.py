from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator, root_validator


class DonationCreate(BaseModel):
    full_amount: int = Field(...)
    comment: Optional[str]

    @validator('full_amount')
    def check_from_create_date_later_than_now(cls, value):
        if value < 1:
            raise ValueError(
                'Сумма должна быть больше 1'
            )
        return value


class DonationCreatedResponse(DonationCreate):
    full_amount: int = Field(...)
    comment: Optional[str]

    class Config:
        orm_mode = True


class DonationDB(BaseModel):
    id: int
    user_id: int
    full_amount: int
    comment: str
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: datetime

    class Config:
        orm_mode = True
