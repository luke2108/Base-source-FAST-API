from datetime import datetime
from typing import List, Optional, Union, Dict
from uuid import UUID
from pydantic import BaseModel, EmailStr, constr

# Role Start
class RoleBaseSchema(BaseModel):
    name: str  
    code: Optional[Union[str, None]] = None
    icon: Optional[Union[str, None]] = None
    color: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class PermissionDetailSchema(BaseModel):
    permission_id: UUID
    permission_details: List[UUID]

class CreateRoleSchema(BaseModel):
    name: str
    code: str
    icon: Optional[Union[str, None]] = None
    color: Optional[Union[str, None]] = None
    permissions: Optional[List[PermissionDetailSchema]] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "string",
                "code": "string",
                "icon": "string",
                "color": "string",
                "permissions": [
                    {
                        "permission_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "permission_details": [
                            "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                            "3fa85f64-5717-4562-b3fc-2c963f66afa5",
                            "3fa85f64-5717-4562-b3fc-2c963f66afa8"
                        ]
                    },
                    {
                        "permission_id": "3fa85f64-5717-4562-b3fc-2c963f66afa9",
                        "permission_details": [
                            "3fa85f64-5717-4562-b3fc-2c963f66afa0",
                            "3fa85f64-5717-4562-b3fc-2c963f66afa1",
                            "3fa85f64-5717-4562-b3fc-2c963f66afa2"
                        ]
                    }
                ]
            }
        }

class PermissionResponse(BaseModel):
    id: UUID
    name: str

class RoleDetaiResponse(BaseModel):
    id: UUID
    name:str
    code: Optional[Union[str, None]] = None
    icon: Optional[Union[str, None]] = None
    color: Optional[Union[str, None]] = None
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse]

class RoleResponse(RoleBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

class RoleLitleResponse(RoleBaseSchema):
    id: UUID


class PermissionDetailResponse(BaseModel):
    id: UUID
    name: str
    code: str
    # created_at: datetime
    # updated_at: datetime

class PermissionDetailFullResponse(BaseModel):
    permission_id: UUID
    permission_name: str
    permission_code: str
    permission_details: List[PermissionDetailResponse]

class RoleDetailResponse(BaseModel):
    id: UUID
    name: str
    code: Optional[Union[str, None]] = None
    icon: Optional[Union[str, None]] = None
    color: Optional[Union[str, None]] = None
    permissions: List[PermissionDetailFullResponse]

class RoleWithUserCountResponse(RoleResponse):
    user_count: int

class ListRoleResponse(BaseModel):
    status: str
    results: int
    roles: List[RoleWithUserCountResponse]
# Role End