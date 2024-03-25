from fastapi import APIRouter, BackgroundTasks, Request, Response, status, Depends, HTTPException
from psycopg2 import IntegrityError
from app.logging_config import setup_logging
from app.schemas.enum import PermissionDetailEnum, PermissionEnum, UserRoleEnum
from app.schemas.menu import CreateMenuSchema, ListMenuAndSubjectMenuResponse, ListMenuResponse, ListMenuUserLoginResponse, UpdateMenuSchema, MenuResponse
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, oauth2
from uuid import UUID
from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import joinedload

router = APIRouter()
logger = setup_logging()

@router.get('', response_model=ListMenuAndSubjectMenuResponse)
async def get_menu(background_tasks: BackgroundTasks, db: Session = Depends(get_db),
                   limit: int = 100,
                   page: int = 1,
                   name: str = '',
                   user: str = Depends(oauth2.require_user)
                   ):

    oauth2.check_permissions_detail([PermissionEnum.menu], [
                                    PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)

    skip = (page - 1) * limit

    query = db.query(models.Menu)

    if user.role.code not in [UserRoleEnum.admin, UserRoleEnum.operators]:
        query = query.join(models.RoleMenu).filter(models.RoleMenu.role_id == user.role.id)

    if name:
        query = query.filter(models.Menu.name.contains(name))

    menu = query.options(joinedload(models.Menu.menu).joinedload(models.RoleMenu.role), joinedload(models.Menu.sub_menu)).limit(limit).offset(skip).all()
    result = []
    for menu_item in menu:
        roles = [{
            'id': str(role_menu.role.id),
            'name': role_menu.role.name,
            'code': role_menu.role.code,
            'icon': role_menu.role.icon,
        } for role_menu in menu_item.menu]

        subbject_menu = None
        if menu_item.menu_subject:
            subbject_menu = {
                "id" :  menu_item.menu_subject.id,
                "name" :  menu_item.menu_subject.name,
                "code" :  menu_item.menu_subject.code,
                "position" :  menu_item.menu_subject.position,
            }

        submenus = [{
            'id': str(sub_menu.id),
            'name': sub_menu.name,
            'code': sub_menu.code,
            'icon': sub_menu.icon,
            'created_at': sub_menu.created_at,
            'updated_at': sub_menu.updated_at,
        } for sub_menu in menu_item.sub_menu]

        result.append({
            'name': menu_item.name,
            'code': menu_item.code,
            'icon': menu_item.icon,
            'position': menu_item.position,
            'subject_menu': subbject_menu,
            'roles': roles,
            'submenus': submenus,
            'id': str(menu_item.id),
            'created_at': menu_item.created_at,
            'updated_at': menu_item.updated_at,
        })

    return {'status': 'success', 'results': len(result), 'menu': result}

@router.post('', status_code=status.HTTP_201_CREATED, response_model=MenuResponse)
async def create_menu(background_tasks: BackgroundTasks, payload: CreateMenuSchema, request: Request, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):

    oauth2.check_permissions_detail([PermissionEnum.menu], [
                                    PermissionDetailEnum.create], user, background_tasks=background_tasks, db=db)
    payload.code = payload.code.lower()
    
    existing_role = db.query(models.Role).filter(models.Menu.code == payload.code).first()
    if existing_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Menu already exists")
    try:
        new_menu = models.Menu(
            name=payload.name, code=payload.code, icon=payload.icon, position=payload.position, subject_id=payload.subject_id)
        
        db.add(new_menu)
        db.commit()
        db.refresh(new_menu)
        new_role_menu_list = []
        if payload.role_ids:
            for role_id in payload.role_ids:
                try:
                    new_role_menu = models.RoleMenu(
                        role_id=role_id, menu_id=new_menu.id)
                    db.add(new_role_menu)
                    db.commit()
                    db.refresh(new_role_menu)

                    new_role_menu_list.append({
                        'id': str(role_id),
                        'name': new_role_menu.role.name,
                        'code': new_role_menu.role.code,
                        'icon': new_role_menu.role.icon,
                    })
                except IntegrityError as e:
                    db.rollback()
                    error_message = f"Error creating RoleMenu. IntegrityError: {str(e)}"
                    logger.error(error_message)
        submenu = None
        if new_menu.menu_subject:
            submenu = {
                "id" :  new_menu.menu_subject.id,
                "name" :  new_menu.menu_subject.name,
                "code" :  new_menu.menu_subject.code,
                "position" :  new_menu.menu_subject.position,
            }
        response_data = {
            'id': str(new_menu.id),
            'name': str(new_menu.name),
            'code': str(new_menu.code),
            'icon': str(new_menu.icon),
            'position': str(new_menu.position),
            'subject_menu': submenu,
            'roles': new_role_menu_list,
            'created_at': new_menu.created_at,
            'updated_at': new_menu.updated_at,
        }

        return response_data

    except Exception as e:
        error_message = f"Error creating menu. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot create menu')

@router.get('/{id}', response_model=MenuResponse)
async def get_menu(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.menu], [
                                    PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)

    menu = (
        db.query(models.Menu)
        .filter(models.Menu.id == id)
        .options(joinedload(models.Menu.menu).joinedload(models.RoleMenu.role), joinedload(models.Menu.sub_menu))
        .first()
    )
    
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Menu not found")

    roles = [{
        'id': str(role_menu.role.id),
        'name': role_menu.role.name,
        'code': role_menu.role.code,
        'icon': role_menu.role.icon,
    } for role_menu in menu.menu]

    submenus = [{
        'id': str(sub_menu.id),
        'name': sub_menu.name,
        'code': sub_menu.code,
        'icon': sub_menu.icon
    } for sub_menu in menu.sub_menu]

    subbject_menu = None
    if menu.menu_subject:
        subbject_menu = {
            "id" :  menu.menu_subject.id,
            "name" :  menu.menu_subject.name,
            "code" :  menu.menu_subject.code,
            "position" :  menu.menu_subject.position,
        }

    response_data = {
        'id': str(menu.id),
        'name': str(menu.name),
        'code': str(menu.code),
        'icon': str(menu.icon),
        'position': str(menu.position),
        'subject_menu': subbject_menu,
        'roles': roles,
        'submenus': submenus,
        'created_at': menu.created_at,
        'updated_at': menu.updated_at,
    }

    return response_data

@router.put('/{id}', response_model=MenuResponse)
async def update_menu(background_tasks: BackgroundTasks, id: UUID, payload: UpdateMenuSchema, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.menu], [
                                    PermissionDetailEnum.write], user, background_tasks=background_tasks, db=db)

    menu_query = db.query(models.Menu).filter(models.Menu.id == id)
    updated_menu = menu_query.first()

    if not updated_menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Menu not found')

    try:
        update_data = {
            "name": payload.name,
            "code": payload.code,
            "icon": payload.icon,
            "position": payload.position,
            "subject_id": payload.subject_id,
        }
        menu_query.update(update_data)

        # Load submenus along with the menu
        updated_menu = (
            db.query(models.Menu)
            .filter(models.Menu.id == id)
            .options(joinedload(models.Menu.sub_menu))
            .first()
        )

        new_role_menu_list = []
        db.query(models.RoleMenu).filter(models.RoleMenu.menu_id == id).delete()
        if payload.role_ids:
            for role_id in payload.role_ids:
                try:
                    new_role_menu = models.RoleMenu(
                        role_id=role_id, menu_id=id)
                    db.add(new_role_menu)
                    db.commit()
                    db.refresh(new_role_menu)

                    new_role_menu_list.append({
                        'id': str(role_id),
                        'name': new_role_menu.role.name,
                        'code': new_role_menu.role.code,
                        'icon': new_role_menu.role.icon,
                    })
                except IntegrityError as e:
                    db.rollback()
                    error_message = f"Error creating RoleMenu. IntegrityError: {str(e)}"
                    logger.error(error_message)

        subbject_menu = None
        if updated_menu.menu_subject:
            subbject_menu = {
                "id" :  updated_menu.menu_subject.id,
                "name" :  updated_menu.menu_subject.name,
                "code" :  updated_menu.menu_subject.code,
                "position" :  updated_menu.menu_subject.position,
                
            }

        response_data = {
            'id': str(id),
            'name': str(updated_menu.name),
            'code': str(updated_menu.code),
            'icon': str(updated_menu.icon),
            'position': str(updated_menu.position),
            'subject_menu': subbject_menu,
            'roles': new_role_menu_list,
            'submenus': [
                {
                    'id': str(sub_menu.id),
                    'name': sub_menu.name,
                    'code': sub_menu.code,
                    'icon': sub_menu.icon
                } for sub_menu in updated_menu.sub_menu
            ],
            'created_at': updated_menu.created_at,
            'updated_at': updated_menu.updated_at,
        }

        return response_data
    except Exception as e:
        error_message = f"Error updating menu. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot update menu')

@router.delete('/{id}')
async def delete_menu(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):

    oauth2.check_permissions_detail([PermissionEnum.menu], [
                                    PermissionDetailEnum.delete], user, background_tasks=background_tasks, db=db)

    menu_query = db.query(models.Menu).filter(models.Menu.id == id)
    menu = menu_query.first()
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Menu not found')
    try:

        # Delete Rolemenu
        role_menu_using_menu =  db.query(models.RoleMenu).filter(models.RoleMenu.menu_id == id)
        for role_menu_using_menu_item in role_menu_using_menu:
            db.delete(role_menu_using_menu_item)
        db.commit()

        # Delete SubMenu
        submenu_using_menu =  db.query(models.SubMenu).filter(models.SubMenu.menu_id == id)
        for submenu_using_menu_item in submenu_using_menu:
            db.delete(submenu_using_menu_item)
        db.commit()

        menu_query.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        error_message = f"Error Detele menu. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot delete menu')