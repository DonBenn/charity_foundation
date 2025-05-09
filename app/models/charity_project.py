from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean

from app.core.constants import (MAX_PROJECT_NAME_LENGTH,
    DEFAULT_INVESTED_AMOUNT_VALUE
)
from app.core.db import Base


class CharityProject(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_PROJECT_NAME_LENGTH), unique=True,
                  nullable=False)
    description = Column(Text, nullable=False)
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=DEFAULT_INVESTED_AMOUNT_VALUE)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)