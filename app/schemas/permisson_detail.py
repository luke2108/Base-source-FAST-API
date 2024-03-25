from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel

# PermissionDetail Start

class PermissionDetailBaseSchema(BaseModel):
    name: str
    code: str
    permission_id: UUID
    
    class Config:
        orm_mode = True

class CreatePermissionDetailSchema(BaseModel):
    name: str
    code: str
    permission_id: UUID

    class Config:
        orm_mode = True

class PermissionDetailResponse(PermissionDetailBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

class UpdatePermissionDetailSchema(BaseModel):
    name: str
    code: str
    permission_id: UUID
    class Config:
        orm_mode = True

class ListPermissionDetailResponse(BaseModel):
    status: str
    results: int
    permissions_detail: List[PermissionDetailResponse]
    
# PermissionDetail End

