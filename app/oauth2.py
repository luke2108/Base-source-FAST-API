import base64
from typing import List
from fastapi import Depends, HTTPException, Query, status
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from fastapi import BackgroundTasks
from app.schemas.enum import UserRoleEnum

from . import models
from .database import get_db
from sqlalchemy.orm import Session
from .config import settings
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from app.logging_config import setup_logging
logger = setup_logging()
class Settings(BaseModel):
    authjwt_algorithm: str = settings.JWT_ALGORITHM
    authjwt_decode_algorithms: List[str] = [settings.JWT_ALGORITHM]
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    authjwt_public_key: str = base64.b64decode(
        settings.JWT_PUBLIC_KEY).decode('utf-8')
    authjwt_private_key: str = base64.b64decode(
        settings.JWT_PRIVATE_KEY).decode('utf-8')

@AuthJWT.load_config
def get_config():
    return Settings()

class NotVerified(Exception):
    pass

class UserNotFound(Exception):
    pass

class UserNotPermission(Exception):
    pass

def require_user(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user or not user.is_activate:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User authentication failed')

        return user

    except Exception as e:
        error = e.__class__.__name__
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='You are not logged in')
        if error == 'UserNotFound':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='User no longer exist')
        if error == 'NotVerified':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Please verify your account')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is invalid or has expired')

def check_permissions_detail(
    required_permissions: List[str],
    required_permissions_detail: List[str],
    user: models.User,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    
    if user.role.code == UserRoleEnum.admin:
        background_tasks.add_task(user_history, user, db=db, status_code=status.HTTP_200_OK, permission=required_permissions[0], permission_detail=required_permissions_detail[0])
        return user
    else:
        user_role_permissions = {permission.permission.code for permission in user.role.permissions}

        user_permission_details = {
            permission_detail.code
            for role_permission in user.role.permissions
            for permission_detail in role_permission.permission.permissions_detail
        }

        all_required_permissions = set(required_permissions + required_permissions_detail)

        if not all_required_permissions.issubset(user_role_permissions.union(user_permission_details)):
            status_code = status.HTTP_403_FORBIDDEN
        else:
            status_code = status.HTTP_200_OK

        # background_tasks.add_task(user_history, user, db=db, status_code=status.HTTP_200_OK, permission=required_permissions[0], permission_detail=required_permissions_detail[0])

        if status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(status_code=status_code, detail='User does not have required permissions')

    
def user_history(user: models.User, db: Session = Depends(get_db), permission: str = '', permission_detail: str = '',status_code: int = None):
    try:
        new_history = models.UserHisory(email=user.email, user_id=user.id, status_code=status_code, permission=permission, permission_detail=permission_detail)
        db.add(new_history)
        db.commit()
        db.refresh(new_history)
    except Exception as e:
        error_message = f"Error creating history. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot create history')