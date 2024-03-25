from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel

# SubjectMenu Start
class SubjectMenuBaseSchema(BaseModel):
    name: str
    code: Optional[Union[str, None]] = None
    position: Optional[Union[int, None]] = None
    icon: Optional[Union[str, None]] = None
    decscript: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class CreateSubjectMenuSchema(BaseModel):
    name: str
    code: Optional[Union[str, None]] = None
    position: Optional[Union[int, None]] = None
    icon: Optional[Union[str, None]] = None
    decscript: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class SubjectMenuResponse(SubjectMenuBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

class SubjectMenuLitleResponse(SubjectMenuBaseSchema):
    id: UUID

class UpdateSubjectMenuSchema(BaseModel):
    name: str
    code: Optional[Union[str, None]] = None
    position: Optional[Union[int, None]] = None
    icon: Optional[Union[str, None]] = None
    decscript: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class ListSubjectMenuResponse(BaseModel):
    status: str
    results: int
    subject_menus: List[SubjectMenuResponse]