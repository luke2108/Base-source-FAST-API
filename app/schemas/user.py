from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel, EmailStr, constr

class RoleBaseSchema(BaseModel):
    name: str  
    code: Optional[Union[str, None]] = None
    icon: Optional[Union[str, None]] = None
    color: Optional[Union[str, None]] = None
    class Config:
        orm_mode = True

class RoleResponse(RoleBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

class RoleLitleResponse(RoleBaseSchema):
    id: UUID

# Start User
class UserBaseSchema(BaseModel):
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)
    passwordConfirm: str
    role_id: str
    is_activate: bool = True

class ResetPasswordUserSchema(BaseModel):
    password: constr(min_length=8)
    passwordConfirm: str
    user_id: UUID

class UpdateUserSchema(UserBaseSchema):
    role_id: str
    is_activate: bool = True

class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class UserResponse(UserBaseSchema):
    id: UUID
    is_activate: Optional[bool] = None
    role: RoleLitleResponse
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class UserMemberResponse(UserBaseSchema):
    id: UUID
    is_activate: Optional[bool] = False
    is_online: Optional[bool] = False
    role: RoleLitleResponse
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ListUserMemberChatResponse(BaseModel):
    status: str
    count_all: int
    results: int
    users: List[UserMemberResponse]

class ListUserResponse(BaseModel):
    status: str
    results: int
    users: List[UserResponse]

class ListUserAllResponse(BaseModel):
    status: str
    users_activate: int
    users_inactivate: int
    count_all: int
    results: int
    users: List[UserResponse]

class ListUserCommentatorResponse(BaseModel):
    status: str
    count_all: int
    results: int
    users: List[UserResponse]    

class PermissionDetailResponse(BaseModel):
    id: UUID
    name: str
    code: str

class PermissionDetailFullResponse(BaseModel):
    permission_id: UUID
    permission_name: str
    permission_code: str
    permission_details: List[PermissionDetailResponse]

class PermissiionDetailUserResponse(BaseModel):
    permissions: List[PermissionDetailFullResponse]


class PermissionDetailFullResponse(BaseModel):
    permission_id: UUID
    permission_name: str
    permission_code: str
    permission_details: List[PermissionDetailResponse]

class RoleDetailResponse(BaseModel):
    id: UUID
    name: str
    code: Optional[Union[str, None]] = None
    permissions: List[PermissionDetailFullResponse]


class ProfileInfoResponse(BaseModel):
    name: str
    email : str
    status : bool
    role_name : str
    avatar : Optional[Union[str, None]] = None

class UserMetaResponse(BaseModel):
    meta_id: UUID
    meta_code : str
    meta_name : str
    meta_detail_id: Optional[Union[UUID, None]] = None
    meta_value : Optional[Union[str, None]] = None

class ProfileResponse(BaseModel):
    info: ProfileInfoResponse
    user_meta: List[UserMetaResponse]

class ProfileInfoUpdateResponse(BaseModel):
    name: str

class UserMetaUpdateResponse(BaseModel):
    meta_id: UUID
    meta_detail_id: Optional[Union[UUID, None]] = None
    meta_value : Optional[Union[str, None]] = None

class ProfileUpdate(BaseModel):
    info: ProfileInfoUpdateResponse
    user_meta: List[UserMetaUpdateResponse]

class UploadAvatarBase(BaseModel):
    # meta_detail_id: Optional[Union[UUID, None]] = None
    avatar_name: str
    avatar_content: str

class AvatarReposnseBase(BaseModel):
    status: str
    message: str
    avatar_url: Optional[Union[str, None]] = None