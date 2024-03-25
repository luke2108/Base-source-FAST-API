from fastapi import APIRouter, BackgroundTasks, Request, Response, status, Depends, HTTPException
from app.logging_config import setup_logging
from app.schemas.enum import PermissionDetailEnum, PermissionEnum, UserRoleEnum
from app.schemas.sub_menu import CreateSubMenuSchema, ListSubMenuResponse, UpdateSubMenuSchema, SubMenuResponse
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, oauth2
from uuid import UUID
from fastapi import Depends, HTTPException, status, APIRouter, Response
router = APIRouter()
logger = setup_logging()

@router.get('', response_model=ListSubMenuResponse)
async def get_sub_menu(background_tasks: BackgroundTasks, db: Session = Depends(get_db),
        limit: int = 100, 
        page: int = 1,  
        name: str='',
        menu_id: UUID = None,
        user: str = Depends(oauth2.require_user)
        ):
    
    oauth2.check_permissions_detail([PermissionEnum.sub_menu], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)
    
    skip = (page - 1) * limit
    query = db.query(models.SubMenu)
    if name:
        query = query.filter(models.SubMenu.name.contains(name))
    if menu_id:
        query = query.filter(models.SubMenu.menu_id == menu_id, models.SubMenu.name.contains(name))
    
    sub_menu = query.limit(limit).offset(skip).all()
    
    return {'status': 'success', 'results': len(sub_menu), 'sub_menu': sub_menu}

@router.post('', status_code=status.HTTP_201_CREATED, response_model=SubMenuResponse)
async def create_sub_menu(background_tasks: BackgroundTasks, payload: CreateSubMenuSchema, request: Request, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    
    oauth2.check_permissions_detail([PermissionEnum.sub_menu], [PermissionDetailEnum.create], user, background_tasks=background_tasks, db=db)

    try:
        new_sub_menu = models.SubMenu(**payload.dict())
        db.add(new_sub_menu)
        db.commit()
        db.refresh(new_sub_menu)
        return new_sub_menu

    except Exception as e:
        error_message = f"Error creating sub_menu. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot create sub_menu')

@router.get('/{id}', response_model=SubMenuResponse)
async def get_sub_menu(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.sub_menu], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)
    
    sub_menu = db.query(models.SubMenu).filter(models.SubMenu.id == id).first()
    if not sub_menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"SubMenu not found")
    return sub_menu

@router.put('/{id}', response_model=SubMenuResponse)
async def update_sub_menu(background_tasks: BackgroundTasks, id: UUID, payload: UpdateSubMenuSchema, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
        oauth2.check_permissions_detail([PermissionEnum.sub_menu], [PermissionDetailEnum.write], user, background_tasks=background_tasks, db=db)

        sub_menu_query = db.query(models.SubMenu).filter(models.SubMenu.id == id)
        updated_sub_menu = sub_menu_query.first()

        if not updated_sub_menu:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'SubMenu not found')
        try:
            sub_menu_query.update(payload.dict(exclude_unset=True), synchronize_session=False)
            db.commit()
            return updated_sub_menu
        except Exception as e:
            error_message = f"Error Update sub_menu. Error: {str(e)}"
            logger.error(error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot update sub_menu')

@router.delete('/{id}')
async def delete_sub_menu(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):

        oauth2.check_permissions_detail([PermissionEnum.sub_menu], [PermissionDetailEnum.delete], user, background_tasks=background_tasks, db=db)

        sub_menu_query = db.query(models.SubMenu).filter(models.SubMenu.id == id)
        sub_menu = sub_menu_query.first()
        if not sub_menu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'SubMenu not found')
        try:
            sub_menu_query.delete(synchronize_session=False)
            db.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            error_message = f"Error Detele sub_menu. Error: {str(e)}"
            logger.error(error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot delete sub_menu')