from sqlalchemy import or_
from sqlalchemy.orm import aliased
import base64
from datetime import datetime
import os
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, Request, Response, status, Depends, HTTPException
from pydantic import EmailStr
from app import utils
from app.schemas.enum import PermissionDetailEnum, PermissionEnum, UserRoleEnum
from app.schemas.menu import ListMenuUserLoginResponse
from app.schemas.role import RoleDetailResponse, RoleLitleResponse
from app.schemas.user import AvatarReposnseBase, CreateUserSchema, ListUserCommentatorResponse, ListUserMemberChatResponse, PermissiionDetailUserResponse, ProfileInfoResponse, ProfileResponse, ProfileUpdate, ResetPasswordUserSchema, UploadAvatarBase, UserMemberResponse, UserMetaResponse
from app.schemas.user import UpdateUserSchema, UserResponse, ListUserResponse, ListUserAllResponse
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, oauth2
from uuid import UUID
from fastapi import Depends, HTTPException, status, APIRouter
from app.logging_config import setup_logging
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, func

logger = setup_logging()
router = APIRouter()


@router.post('', status_code=status.HTTP_201_CREATED)
async def create_user(background_tasks: BackgroundTasks, payload: CreateUserSchema, request: Request, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):

    oauth2.check_permissions_detail([PermissionEnum.users], [
                                    PermissionDetailEnum.create], user, background_tasks=background_tasks, db=db)

    user_query = db.query(models.User).filter(
        models.User.email == EmailStr(payload.email.lower()))
    user = user_query.first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Account already exist')

    if payload.password != payload.passwordConfirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')

    try:
        payload.password = await utils.hash_password(payload.password)
        del payload.passwordConfirm
        payload.email = EmailStr(payload.email.lower())
        new_user = models.User(**payload.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {'status': 'success', 'message': 'Create successfully'}
    except Exception as e:
        error_message = f"Error creating user. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot create user')

@router.post('/reset-password')
async def reset_password(background_tasks: BackgroundTasks, payload: ResetPasswordUserSchema, request: Request, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):

    oauth2.check_permissions_detail([PermissionEnum.users], [
                                    PermissionDetailEnum.write], user, background_tasks=background_tasks, db=db)
    user = db.query(models.User).filter(
        models.User.id == payload.user_id).first()

    if payload.password != payload.passwordConfirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')

    payload.password = await utils.hash_password(payload.password)
    del payload.passwordConfirm
    try:
        user.password = payload.password
        db.commit()
        db.refresh(user)

    except Exception as e:
        error_message = f"Error reset password: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot reset password')

    return {'status': 'success', 'message': f'Reset password for user {user.email} successfully'}

@router.get('', response_model=ListUserAllResponse)
async def get_users(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    limit: int = 100,
    page: int = 1,
    name: str = '',
    email: str = '',
    status: bool = None,
    user: str = Depends(oauth2.require_user)
):
    skip = (page - 1) * limit

    # Build the query with filters
    query = db.query(models.User).filter(
        models.User.name.contains(name),
        models.User.email.contains(email)
    ).order_by(models.User.created_at.desc())

    if status is not None:
        query = query.filter(models.User.is_activate == status)

    all_user = db.query(models.User)

    users_activate = all_user.filter(models.User.is_activate == True).count()
    users_inactivate = all_user.filter(models.User.is_activate == False).count()
    count_all = query.count()

    users = query.limit(limit).offset(skip).all()

    return {'status': 'success', 'count_all': count_all, 'users_activate': users_activate, 'users_inactivate': users_inactivate,'results': len(users), 'users': users}

@router.get('/commentators', response_model=ListUserCommentatorResponse)
async def get_users_commentators(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    limit: int = 100,
    page: int = 1,
    name: str = '',
    email: str = '',
    user: str = Depends(oauth2.require_user)
):
    skip = (page - 1) * limit

    # Build the query with filters
    query = db.query(models.User).join(models.Role).filter(
        models.Role.code == UserRoleEnum.commentators,
        models.User.is_activate == True,
        models.User.name.contains(name),
        models.User.email.contains(email)
    )

    count_all = query.count()

    users = query.limit(limit).offset(skip).all()

    return {'status': 'success', 'count_all': count_all, 'results': len(users), 'users': users}

@router.get('/customer-service', response_model=ListUserCommentatorResponse)
async def get_users_customer_service(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    limit: int = 100,
    page: int = 1,
    name: str = '',
    email: str = '',
    user: str = Depends(oauth2.require_user)
):
    skip = (page - 1) * limit

    # Build the query with filters
    query = db.query(models.User).join(models.Role).filter(
        models.Role.code == UserRoleEnum.customer_service,
        models.User.is_activate == True,
        models.User.name.contains(name),
        models.User.email.contains(email)
    )

    count_all = query.count()

    users = query.limit(limit).offset(skip).all()

    return {'status': 'success', 'count_all': count_all, 'results': len(users), 'users': users}

@router.get('/permission', response_model=PermissiionDetailUserResponse)
async def get_user_permissions(background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    try:
        role = db.query(models.Role).filter(
            models.Role.id == user.role_id).first()
        role_permissions = []
        for rp in role.permissions:
            permission_details = []
            permission_id = rp.permission.id
            if role.code != UserRoleEnum.admin:

                permission_details = db.query(models.RolePermissionDetail.permission_detail_id).filter(
                    models.RolePermissionDetail.role_id == role.id,
                    models.RolePermissionDetail.permission_detail.has(
                        permission_id=permission_id),
                    models.RolePermissionDetail.permission_detail_id.isnot(
                        None)
                ).all()
            else:
                permission_details = db.query(models.PermissionDetail.id).join(
                    models.Permission
                ).filter(
                    models.Permission.id == permission_id
                ).all()

            permission_details = [str(detail[0])
                                  for detail in permission_details]

            permission_details_list = []
            for detail_id in permission_details:
                associated_permission_detail = db.query(
                    models.PermissionDetail).get(detail_id)
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
            'permissions': role_permissions,
        }

        background_tasks.add_task(oauth2.user_history, user, db=db, status_code=status.HTTP_200_OK,
                                  permission="permission", permission_detail="permission")

        return response_data

    except Exception as e:
        error_message = f"Error get Permisiion  for User . Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot Get Permission')

@router.get('/profile', response_model=ProfileResponse)
async def get_profile(db: Session = Depends(get_db), user=Depends(oauth2.require_user)):
    users_meta = db.query(models.UserMeta).filter(
        models.UserMeta.role_id == user.role_id).all()

    user_meta_response = []
    for user_meta in users_meta:
        meta_detail = next(
            (detail for detail in user_meta.details if detail.user_id == user.id), None)

        meta_response = UserMetaResponse(
            meta_id=user_meta.id,
            meta_code=user_meta.meta_code,
            meta_name=user_meta.meta_name,
            meta_detail_id=meta_detail.id if meta_detail else None,
            meta_value=meta_detail.meta_value if meta_detail else None,
        )
        user_meta_response.append(meta_response)

    profile_info = ProfileInfoResponse(
        name=user.name, email=user.email, status=user.is_activate, role_name=user.role.name, avatar=user.avatar)

    profile_response = ProfileResponse(
        info=profile_info, user_meta=user_meta_response)

    return profile_response


@router.put('/profile', response_model=ProfileResponse)
async def update_profile(profile_update: ProfileUpdate, db: Session = Depends(get_db), user=Depends(oauth2.require_user)):
    try:
        # Update user info
        user_to_update = db.query(models.User).filter(
            models.User.id == user.id).first()
        if user_to_update:
            user_to_update.name = profile_update.info.name

        # Update or create user meta details
        for meta_update in profile_update.user_meta:
            meta_detail_to_update = db.query(models.UserMetaDetail).filter(
                models.UserMetaDetail.id == meta_update.meta_detail_id).first()

            if meta_detail_to_update:
                # Update existing meta detail
                meta_detail_to_update.meta_value = meta_update.meta_value

            elif meta_detail_to_update is None and meta_update.meta_value is not None:
                # Create new meta detail
                meta = db.query(models.UserMeta).filter(
                    models.UserMeta.id == meta_update.meta_id).first()
                if meta:
                    new_meta_detail = models.UserMetaDetail(
                        meta_id=meta.id,
                        user_id=user.id,
                        meta_value=meta_update.meta_value
                    )

                    db.add(new_meta_detail)

        db.commit()
        db.refresh(user_to_update)

        users_meta = db.query(models.UserMeta).filter(
            models.UserMeta.role_id == user.role_id).all()

        user_meta_response = []
        for user_meta in users_meta:
            meta_detail = next(
                (detail for detail in user_meta.details if detail.user_id == user.id), None)

            meta_response = UserMetaResponse(
                meta_id=user_meta.id,
                meta_code=user_meta.meta_code,
                meta_name=user_meta.meta_name,
                meta_detail_id=meta_detail.id if meta_detail else None,
                meta_value=meta_detail.meta_value if meta_detail else None,
            )
            user_meta_response.append(meta_response)

        profile_info = ProfileInfoResponse(
            name=user.name, email=user.email, status=user.is_activate, role_name=user.role.name, avatar=user.avatar)

        profile_response = ProfileResponse(
            info=profile_info, user_meta=user_meta_response)

        return profile_response

    except Exception as e:
        db.rollback()  # Rollback the changes in case of an error
        logger.error(f"Error updating profile. Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Can not update profile")

@router.post('/upload-avatar')
async def upload_avatar(avarta: UploadAvatarBase, db: Session = Depends(get_db), user=Depends(oauth2.require_user)):
    try:
        # Update user info
        static_folder_files = os.path.join(
            os.getcwd(), "app/statics/avatar/images")

        check_exist_user = db.query(models.User).filter(
            models.User.id==user.id).first()

        if not check_exist_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="User is not exist please contact admin.")

        file_name = avarta.avatar_name
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
        new_file_name = f"{current_datetime}_{file_name}"
        content_binary = base64.b64decode(avarta.avatar_content)
        file_path = os.path.join(static_folder_files, new_file_name)
        file_url = "/statics/avatar/images/" + new_file_name

        with open(file_path, "wb") as file:
            file.write(content_binary)
        
        check_exist_user.avatar = file_url
        db.add(check_exist_user)
        db.commit()
        db.refresh(check_exist_user)

        return {'status': 'success', 'message': 'Upload avatart successfully', 'avatar_url': file_url}
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating profile. Error: {str(e)}")

@router.get('/menu', response_model=ListMenuUserLoginResponse)
async def get_menu_and_permission(background_tasks: BackgroundTasks, db: Session = Depends(get_db),
                                  limit: int = 1000,
                                  page: int = 1,
                                  name: str = '',
                                  user: str = Depends(oauth2.require_user)
                                  ):

    skip = (page - 1) * limit

    query = db.query(models.Menu)

    query = query.join(models.RoleMenu).filter(
        models.RoleMenu.role_id == user.role.id)

    if name:
        query = query.filter(models.Menu.name.contains(name))

    menu = query.options(joinedload(models.Menu.menu).joinedload(models.RoleMenu.role), joinedload(
        models.Menu.sub_menu)).order_by(models.Menu.position.asc()).limit(limit).offset(skip).all()

    role = db.query(models.Role).filter(models.Role.id == user.role_id).first()
    role_permissions = []
    for rp in role.permissions:
        permission_details = []
        permission_id = rp.permission.id
        if role.code != UserRoleEnum.admin:

            permission_details = db.query(models.RolePermissionDetail.permission_detail_id).filter(
                models.RolePermissionDetail.role_id == role.id,
                models.RolePermissionDetail.permission_detail.has(
                    permission_id=permission_id),
                models.RolePermissionDetail.permission_detail_id.isnot(None)
            ).all()
        else:
            permission_details = db.query(models.PermissionDetail.id).join(
                models.Permission
            ).filter(
                models.Permission.id == permission_id
            ).all()

        permission_details = [str(detail[0]) for detail in permission_details]

        permission_details_list = []
        for detail_id in permission_details:
            associated_permission_detail = db.query(
                models.PermissionDetail).get(detail_id)
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

    role_permission_res = {
        'id': str(role.id),
        'name': str(role.name),
        'code': str(role.code),
        'icon': str(role.icon),
        'color': str(role.color),
        'permissions': role_permissions,
    }

    result = []
    for menu_item in menu:
        submenus = [{
            'id': str(sub_menu.id),
            'name': sub_menu.name,
            'code': sub_menu.code,
            'icon': sub_menu.icon
        } for sub_menu in menu_item.sub_menu]

        result.append({
            'id': str(menu_item.id),
            'name': menu_item.name,
            'code': menu_item.code,
            'position': menu_item.position,
            'icon': menu_item.icon,
            'submenus': submenus,
            'created_at': menu_item.created_at,
            'updated_at': menu_item.updated_at,
        })
    background_tasks.add_task(oauth2.user_history, user, db=db,
                              status_code=status.HTTP_200_OK, permission="menu", permission_detail="menu")

    return {'status': 'success', 'menu': result, 'role_permissions_detail': role_permission_res}


@router.get('/me', response_model=UserResponse)
async def get_me(background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):

    user = db.query(models.User).filter(models.User.id == user.id).first()
    background_tasks.add_task(oauth2.user_history, user, db=db,
                              status_code=status.HTTP_200_OK, permission="", permission_detail="get me")
    return user


@router.get('/{user_id}', response_model=UserResponse)
async def get_user(background_tasks: BackgroundTasks, user_id: UUID, db: Session = Depends(get_db), user: models.User = Depends(oauth2.require_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    background_tasks.add_task(oauth2.user_history, user, db=db,
                              status_code=status.HTTP_200_OK, permission="", permission_detail="get user")
    return user


@router.put('/{id}', response_model=UserResponse)
async def update_user(background_tasks: BackgroundTasks, id: UUID, user: UpdateUserSchema, db: Session = Depends(get_db), user_login: str = Depends(oauth2.require_user)):

    oauth2.check_permissions_detail([PermissionEnum.users], [
                                    PermissionDetailEnum.write], user_login, background_tasks=background_tasks, db=db)

    updated_user = db.query(models.User).filter(models.User.id == id).first()

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    # Update user attributes
    updated_user.name = user.name
    updated_user.role_id = user.role_id
    updated_user.is_activate = user.is_activate

    if user.role_id:
        role = db.query(models.Role).filter(
            models.Role.id == user.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid role_id')

        updated_user.role_id = user.role_id

    try:
        db.commit()
        db.refresh(updated_user)

        return updated_user
    except Exception as e:
        error_message = f"Error update user. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot update user')

# @router.delete('/{id}')
async def delete_user(id: UUID, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    try:
        users = db.query(models.User).filter(models.User.id == id).first()

        db.delete(users)
        db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        db.rollback()
        error_message = f"Error update status notification. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Cannot update status notification')
