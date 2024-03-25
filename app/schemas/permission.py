from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel

# Permission Start
class PermissionBaseSchema(BaseModel):
    name: str
    code: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class CreatePermissionSchema(BaseModel):
    name: str
    code: str
    class Config:
        orm_mode = True

class PermissionResponse(PermissionBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

class PermissionRoleResponse(PermissionBaseSchema):
    id: UUID
    role_names: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

class PermissionLitleResponse(PermissionBaseSchema):
    id: UUID

class UpdatePermissionSchema(BaseModel):
    name: str
    code: str
    class Config:
        orm_mode = True

class ListPermissionResponse(BaseModel):
    status: str
    count_all: int
    results: int
    permissions: List[PermissionRoleResponse]
    
class ListPermissionLiteResponse(BaseModel):
    status: str
    results: int
    permissions: List[PermissionLitleResponse]
# Permission End

