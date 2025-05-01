from typing import Optional

from pydantic import BaseModel, Field, validator


class CharityProjectCreate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str]