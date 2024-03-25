from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel


# Menu Start
class RoleBaseSchema(BaseModel):
    id: Optional[Union[UUID, None]] = None
    name: Optional[Union[str, None]] = None
    code: Optional[Union[str, None]] = None
    icon: Optional[Union[str, None]] = None

class SubMenuBaseSchema(BaseModel):
    id: Optional[Union[UUID, None]] = None
    name: Optional[Union[str, None]] = None
    code: Optional[Union[str, None]] = None
    icon: Optional[Union[str, None]] = None

# Menu Start
class SubjectMenuResponse(BaseModel):
    id: Optional[Union[UUID, None]] = None
    name: Optional[Union[str, None]] = None
    code: Optional[Union[str, None]] = None
    position: Optional[Union[int, None]] = None

# Menu Start
class MenuBaseSchema(BaseModel):
    name: str
    code: str
    icon: Optional[Union[str, None]] = None
    position: int
    subject_menu: Optional[Union[SubjectMenuResponse, None]] = None
    roles: List[Union[RoleBaseSchema, None]] = None
    submenus: List[Union[SubMenuBaseSchema, None]] = None
    class Config:
        orm_mode = True

class ListMenuBaseSchema(BaseModel):
    name: str
    code: str
    icon: Optional[Union[str, None]] = None
    position: int
    subject_menu: Optional[Union[SubjectMenuResponse, None]] = None
    roles: List[Union[RoleBaseSchema, None]] = None
    submenus: List[Union[SubMenuBaseSchema, None]] = None
    class Config:
        orm_mode = True

class MenuUserloginBaseSchema(BaseModel):
    name: str
    code: str
    icon: Optional[Union[str, None]] = None
    position: int
    submenus: List[Union[SubMenuBaseSchema, None]] = None
    class Config:
        orm_mode = True

class CreateMenuSchema(BaseModel):
    name: str
    code: str
    subject_id: Optional[Union[UUID, None]] = None
    icon: Optional[Union[str, None]] = None
    position: int
    role_ids: Optional[List[Union[UUID, None]]] = None
    class Config:
        orm_mode = True

class MenuResponse(MenuBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime


class MenuUserLoginResponse(MenuUserloginBaseSchema):
    id: UUID

class UpdateMenuSchema(BaseModel):
    name: str
    code: str
    icon: Optional[Union[str, None]] = None
    subject_id: Optional[Union[UUID, None]] = None
    position: int
    role_ids: Optional[List[Union[UUID, None]]] = None
    class Config:
        orm_mode = True

class ListMenuResponse(BaseModel):
    status: str
    results: int
    menu: List[MenuResponse]

class PermissionDetailUserLoginResponse(BaseModel):
    id: UUID
    name: str
    code: str

class PermissionUserLoginResponse(BaseModel):
    permission_id: UUID
    permission_name: str
    permission_code: str
    permission_details: Optional[List[Union[PermissionDetailUserLoginResponse, None]]] = None

class RolePermissionUserLoginResponse(BaseModel):
    id: UUID
    name: str
    code: str
    icon: str
    color: str
    permissions: Optional[List[Union[PermissionUserLoginResponse, None]]] = None

class ListMenuUserLoginResponse(BaseModel):
    status: str
    menu: List[MenuUserLoginResponse]
    role_permissions_detail: RolePermissionUserLoginResponse


class MenuAndSubjectBaseSchema(BaseModel):
    name: str
    code: str
    icon: Optional[Union[str, None]] = None
    position: int
    subject_menu: Optional[Union[SubjectMenuResponse, None]] = None
    roles: List[Union[RoleBaseSchema, None]] = None
    submenus: List[Union[SubMenuBaseSchema, None]] = None
    class Config:
        orm_mode = True

class MenuAndSubjectResponse(MenuAndSubjectBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

class ListMenuAndSubjectMenuResponse(BaseModel):
    status: str
    results: int
    menu: List[MenuAndSubjectResponse]