from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel

# SubMenu Start
class SubMenuBaseSchema(BaseModel):
    name: str
    code: str
    icon: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class CreateSubMenuSchema(BaseModel):
    name: str
    code: str
    icon: Optional[Union[str, None]] = None
    menu_id: Optional[Union[UUID, None]] = None
    class Config:
        orm_mode = True

class MenuBaseSchema(BaseModel):
    id: UUID
    name: str
    code: str
    icon: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class FilterMenuResponse(MenuBaseSchema):
    id: UUID

class SubMenuResponse(SubMenuBaseSchema):
    id: UUID
    menu: FilterMenuResponse
    created_at: datetime
    updated_at: datetime

class UpdateSubMenuSchema(BaseModel):
    name: str
    code: str
    icon: Optional[Union[str, None]] = None
    menu_id: Optional[Union[UUID, None]] = None
    class Config:
        orm_mode = True

class ListSubMenuResponse(BaseModel):
    status: str
    results: int
    sub_menu: List[SubMenuResponse]

# SubMenu End