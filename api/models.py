from pydantic import BaseModel, Field
from typing import Optional, List, Union

from .objectid import PydanticObjectId

class User(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias='_id')
    name: str
    rollno: str
    email: str
    password: str