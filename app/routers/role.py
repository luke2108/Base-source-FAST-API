from sqlalchemy.orm import selectinload
from app.schemas.enum import PermissionDetailEnum, PermissionEnum, UserRoleEnum
from app.schemas.role import ListRoleResponse, RoleDetailResponse, RoleWithUserCountResponse, CreateRoleSchema
from .. import models
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, Depends, HTTPException, status, APIRouter, Response
from app.oauth2 import check_permissions_detail, require_user
from uuid import UUID
from ..database import get_db
from app.logging_config import setup_logging
from sqlalchemy.orm import selectinload
from sqlalchemy import func
logger = setup_logging()

router = APIRouter()

@router.get('', response_model=ListRoleResponse)
async def get_roles(background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: str = Depends(require_user)):
    check_permissions_detail([PermissionEnum.roles], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)
    roles = (
        db.query(models.Role, func.count(models.User.id).label('user_count'))
        .outerjoin(models.User, models.User.role_id == models.Role.id)
        .group_by(models.Role.id)
        .all()
    )

    roles_with_user_count = [
        RoleWithUserCountResponse(
            id=role.id,
            name=role.name,
            code=role.code,
            icon=role.icon,
            color=role.color,
            created_at=role.created_at,
            updated_at=role.updated_at,
            user_count=user_count,
        )
        for role, user_count in roles
    ]

    return {'status': 'success', 'results': len(roles_with_user_count), 'roles': roles_with_user_count}


@router.post('', status_code=status.HTTP_201_CREATED, response_model=RoleDetailResponse)
async def create_role(background_tasks: BackgroundTasks, role: CreateRoleSchema, db: Session = Depends(get_db), user: str = Depends(require_user)):
    check_permissions_detail([PermissionEnum.roles], [PermissionDetailEnum.create], user, background_tasks=background_tasks, db=db)
    role.code = role.code.lower()
    
    existing_role = db.query(models.Role).filter(models.Role.code == role.code).first()
    if existing_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")

    try:
        new_role = models.Role(name=role.name, code=role.code, icon=role.icon, color=role.color)
        db.add(new_role)
        db.commit()
        db.refresh(new_role)

        new_role_permissions = []

        try:
            if role.permissions:
                for permission_detail in role.permissions:

                    permission = db.query(models.Permission).get(permission_detail.permission_id)
                    if permission:
                        role_permission = models.RolePermission(role=new_role, permission=permission)
                        db.add(role_permission)

                        # Save permission details
                        permission_details_list = []
                        for detail_id in permission_detail.permission_details:
                            permission_detail_model = models.RolePermissionDetail(role_id=new_role.id, permission_detail_id=detail_id)
                            
                            db.add(permission_detail_model)
                            associated_permission_detail = db.query(models.PermissionDetail).get(detail_id)
                            permission_details_list.append({
                                'id': str(detail_id),
                                'name': associated_permission_detail.name,
                                'code': associated_permission_detail.code,
                            })


                        new_role_permissions.append({
                            'permission_id': str(permission.id),
                            'permission_name': permission.name,
                            'permission_code': permission.code,
                            'permission_details': permission_details_list,
                        })
        except Exception as e:
            error_message = f"Error Role Permission Detail role. Error: {str(e)}"
            logger.error(error_message)

        db.commit()
        db.refresh(new_role)

        response_data = {
            'id': str(new_role.id),
            'name': str(new_role.name),
            'code': str(new_role.code),
            'color': str(new_role.color),
            'icon': str(new_role.icon),
            'created_at': new_role.created_at,
            'updated_at': new_role.updated_at,
            'permissions': new_role_permissions,
        }

        return response_data
    except Exception as e:
        error_message = f"Error creating role. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot create role')


def get_role_response_data(role):
    permissions_list = []
    for role_permission in (role.permissions or []):
        permission = role_permission.permission
        permission_details_list = []
        for role_permission_detail in (permission.permissions_detail or []):
            permission_detail = role_permission_detail.permission_detail
            permission_details_list.append({
                'id': str(permission_detail.id),
                'name': permission_detail.name,
                'code': permission_detail.code,
                'created_at': permission_detail.created_at,
                'updated_at': permission_detail.updated_at,
            })
        permissions_list.append({
            'permission_id': str(permission.id),
            'permission_name': permission.name,
            'permission_code': permission.code,
            'permission_details': permission_details_list,
        })

    response_data = {
        'id': str(role.id),
        'name': str(role.name),
        'code': str(role.code),
        'created_at': role.created_at,
        'updated_at': role.updated_at,
        'permissions': permissions_list,
    }
    return response_data


@router.put('/{id}', response_model=RoleDetailResponse)
async def update_role(background_tasks: BackgroundTasks, id: UUID, role: CreateRoleSchema, db: Session = Depends(get_db), user: str = Depends(require_user)):
    check_permissions_detail([PermissionEnum.roles], [PermissionDetailEnum.write], user, background_tasks=background_tasks, db=db)
    
    role.code = role.code.lower()

    try:
        # Fetch the existing role with permissions
        updated_role = db.query(models.Role).options(selectinload(models.Role.permissions)).filter(models.Role.id == id).first()

        if not updated_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')

        if role.code != updated_role.code:
            existing_role = db.query(models.Role).filter(models.Role.code == role.code).first()
            if existing_role:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role with the updated code '{role.name}' already exists")
        new_role_permissions = []

        db.query(models.RolePermissionDetail).filter(models.RolePermissionDetail.role_id == id).delete()
        db.query(models.RolePermission).filter(models.RolePermission.role_id == id).delete()
        
        if role.permissions:
            # Clear existing RolePermissionDetails
            
            for permission_detail in role.permissions:
                permission_id = permission_detail.permission_id

                if permission_id:
                    permission = db.query(models.Permission).get(permission_id)
                    
                    # Create a new RolePermission instance for each permission
                    new_permission = models.RolePermission(role_id=id, permission_id=permission_id)
                    db.add(new_permission)

                    permission_details = permission_detail.permission_details
                    permission_details_list = []
                    for detail_id in permission_details:
                        new_permission_detail = models.RolePermissionDetail(role=updated_role, permission_detail_id=detail_id)
                        db.add(new_permission_detail)
                        associated_permission_detail = db.query(models.PermissionDetail).get(detail_id)
                        permission_details_list.append({
                            'id': str(detail_id),
                            'name': associated_permission_detail.name,
                            'code': associated_permission_detail.code,
                        })

                    new_role_permissions.append({
                        'permission_id': str(permission.id),
                        'permission_name': permission.name,
                        'permission_code': permission.code,
                        'permission_details': permission_details_list,
                    })

        if updated_role.code not in [UserRoleEnum.admin, UserRoleEnum.commentators, UserRoleEnum.operators]:
            updated_role.code = role.code

        updated_role.name = role.name
        updated_role.icon = role.icon
        updated_role.color = role.color

        db.commit()
        db.refresh(updated_role)

        response_data = {
            'id': str(updated_role.id),
            'name': str(updated_role.name),
            'code': str(updated_role.code),
            'icon': str(updated_role.icon),
            'color': str(updated_role.color),
            'created_at': updated_role.created_at,
            'updated_at': updated_role.updated_at,
            'permissions': new_role_permissions,
        }

        return response_data
    except Exception as e:
        error_message = f"Error updating role. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot update role')

@router.get('/{id}', response_model=RoleDetailResponse)
async def get_role(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(require_user)):
    check_permissions_detail([PermissionEnum.roles], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)
    
    role = db.query(models.Role).filter(models.Role.id == id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    role_permissions = []
    for rp in role.permissions:
        permission_id = rp.permission.id

        permission_details = db.query(models.RolePermissionDetail.permission_detail_id).filter(
            models.RolePermissionDetail.role_id == role.id,
            models.RolePermissionDetail.permission_detail.has(permission_id=permission_id),
            models.RolePermissionDetail.permission_detail_id.isnot(None)
        ).all()


        permission_details = [str(detail[0]) for detail in permission_details]

        permission_details_list = []
        for detail_id in permission_details:
            associated_permission_detail = db.query(models.PermissionDetail).get(detail_id)
            permission_details_list.append({
                'id': str(detail_id),
                'name': associated_permission_detail.name,
                'code': associated_permission_detail.code,
            })

        role_permissions.append({
            'permission_id': str(permission_id),
            'permission_name': str(rp.permission.name),
            'permission_code': str(rp.permission.code),
            'permission_details': permission_details_list,
        })

    response_data = {
        'id': str(role.id),
        'name': str(role.name),
        'icon': str(role.icon),
        'code': str(role.code),
        'color': str(role.color),
        'permissions': role_permissions,
    }

    return response_data

@router.delete('/{id}')
async def delete_role(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(require_user)):
    check_permissions_detail([PermissionEnum.roles], [PermissionDetailEnum.delete], user, background_tasks=background_tasks, db=db)
    
    role_query = db.query(models.Role).filter(models.Role.id == id)
    role = role_query.first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Role not found')
    
    # Delete User using Role
    user_using_role =  db.query(models.User).filter(models.User.role_id == id).first()
    if user_using_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Role is being used')
        
    # Delete Permission using Role
    permissions_using_role =  db.query(models.RolePermission).filter(models.RolePermission.role_id == id)
    for permission_using_role in permissions_using_role:
        db.delete(permission_using_role)
    db.commit()

    permissions_detail_using_roles =  db.query(models.RolePermissionDetail).filter(models.RolePermissionDetail.role_id == id)
    for permissions_detail_using_role in permissions_detail_using_roles:
        db.delete(permissions_detail_using_role)
    db.commit()

    try:
        role_query.delete(synchronize_session=False)
        db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        error_message = f"Error delete role. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot delete role')
