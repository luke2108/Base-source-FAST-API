from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel

# Category Start
class CategoryBaseSchema(BaseModel):
    name: str
    code: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class CreateCategorySchema(BaseModel):
    name: str
    code: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class CategoryResponse(CategoryBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

class CategoryRoleResponse(CategoryBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

class CategoryLitleResponse(CategoryBaseSchema):
    id: UUID

class UpdateCategorySchema(BaseModel):
    name: str
    code: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class ListCategoryResponse(BaseModel):
    status: str
    results: int
    categories: List[CategoryRoleResponse]