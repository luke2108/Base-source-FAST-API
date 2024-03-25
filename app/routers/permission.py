import uuid
from app.schemas.enum import PermissionDetailEnum, PermissionEnum, UserRoleEnum

from app.schemas.permission import ListPermissionResponse, PermissionResponse, UpdatePermissionSchema
from .. import models
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, Depends, HTTPException, status, APIRouter, Response
from app.oauth2 import check_permissions_detail, require_user
from uuid import UUID
from ..database import get_db
from sqlalchemy.orm import joinedload
from app.logging_config import setup_logging

router = APIRouter()
logger = setup_logging()

@router.get('', response_model=ListPermissionResponse)
async def get_permissions(background_tasks: BackgroundTasks, limit: int = 100, page: int = 1, db: Session = Depends(get_db), user: str = Depends(require_user)):

    check_permissions_detail([PermissionEnum.permissions], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)
    skip = (page - 1) * limit
    permissions_query = db.query(models.Permission).options(joinedload(models.Permission.roles))

    count_all = permissions_query.count()

    permissions = permissions_query.limit(limit).offset(skip).all()

    permission_list = []
    for permission in permissions:
        role_names = [role.role.name for role in permission.roles]
        permission_data = {
            'id': str(permission.id),
            'name': permission.name,
            'code': permission.code,
            'description': permission.description,
            'created_at': permission.created_at,
            'updated_at': permission.updated_at,
            'role_names': role_names,
        }
        permission_list.append(permission_data)

    return {'status': 'success', 'count_all': count_all, 'results': len(permissions), 'permissions': permission_list}

@router.post('', status_code=status.HTTP_201_CREATED, response_model=PermissionResponse)
async def create_permission(background_tasks: BackgroundTasks, permission: UpdatePermissionSchema, db: Session = Depends(get_db), user: str = Depends(require_user)):
    
        check_permissions_detail([PermissionEnum.permissions], [PermissionDetailEnum.create], user, background_tasks=background_tasks, db=db)
        
        permission.code = permission.code.lower()
        
        existing_permission = db.query(models.Permission).filter(models.Permission.code == permission.code).first()
        if existing_permission:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission code already exists")
        
        try:
            new_permission = models.Permission(**permission.dict())
            db.add(new_permission)
            db.commit()
            db.refresh(new_permission)

            admin_role = db.query(models.Role).filter(models.Role.code == UserRoleEnum.admin).first()
            if admin_role:
                role_permission = models.RolePermission(role=admin_role, permission=new_permission)
                db.add(role_permission)
                db.commit()

            return new_permission
        except Exception as e:
            error_message = f"Error creating permission. Error: {str(e)}"
            logger.error(error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot create permission')
    

@router.put('/{id}', response_model=PermissionResponse)
async def update_permission(background_tasks: BackgroundTasks, id: UUID, permision: UpdatePermissionSchema, db: Session = Depends(get_db), user: str = Depends(require_user)):
    
    check_permissions_detail([PermissionEnum.permissions], [PermissionDetailEnum.write], user, background_tasks=background_tasks, db=db)

    permission_query = db.query(models.Permission).filter(models.Permission.id == id)
    updated_Permission = permission_query.first()

    if not updated_Permission:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Permission not found')
    try:
        permission_query.update(permision.dict(exclude_unset=True), synchronize_session=False)
        db.commit()
        return updated_Permission
    except Exception as e:
        error_message = f"Error update permission. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot update permission. Maybe permission already exists')

@router.get('/{id}', response_model=PermissionResponse)
async def get_permission(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(require_user)):
    
    check_permissions_detail([PermissionEnum.permissions], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)

    permission = db.query(models.Permission).filter(models.Permission.id == id).first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Permission not found")
    return permission

@router.delete('/{id}')
async def delete_permission(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(require_user)):
    check_permissions_detail([PermissionEnum.permissions], [PermissionDetailEnum.delete], user, background_tasks=background_tasks, db=db)

    permission = db.query(models.Permission).filter(models.Permission.id == id).first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Permission not found')

    role_permissions = db.query(models.RolePermission).filter(models.RolePermission.permission_id == id).all()

    if len(role_permissions) > 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail='Cannot delete permission. It is associated with one or more roles.')
    elif len(role_permissions) == 1:
        try:
            db.delete(role_permissions[0])
            db.commit()
        except Exception as e:
            db.rollback()
            error_message = f"Error Delete permission. Error: {str(e)}"
            logger.error(error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='An error occurred while deleting RolePermission')

    db.delete(permission)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
