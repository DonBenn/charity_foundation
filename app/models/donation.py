from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, \
    ForeignKey

from app.core.constants import DEFAULT_INVESTED_AMOUNT_VALUE
from app.core.db import Base


class Donation(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        'user.id',
                name='fk_donation_user_id_user'))
    comment = Column(Text)
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=DEFAULT_INVESTED_AMOUNT_VALUE)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)