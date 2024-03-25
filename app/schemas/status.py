from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel

# Status Start
class StatusBaseSchema(BaseModel):
    title: str
    type: Optional[Union[str, None]] = None
    color: Optional[Union[str, None]] = None
    code: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class CreateStatusSchema(BaseModel):
    title: str
    type: Optional[Union[str, None]] = None
    color: Optional[Union[str, None]] = None
    code: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class StatusResponse(StatusBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

class StatusLitleResponse(StatusBaseSchema):
    id: UUID

class UpdateStatusSchema(BaseModel):
    title: str
    type: Optional[Union[str, None]] = None
    color: Optional[Union[str, None]] = None
    code: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class ListStatusResponse(BaseModel):
    status: str
    results: int
    statuses: List[StatusResponse]