from fastapi import APIRouter, BackgroundTasks, Request, Response, status, Depends, HTTPException
from app.schemas.enum import PermissionDetailEnum, PermissionEnum
from app.schemas.subject_menu import CreateSubjectMenuSchema, ListSubjectMenuResponse, UpdateSubjectMenuSchema, SubjectMenuResponse
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, oauth2
from uuid import UUID
from fastapi import Depends, HTTPException, status, APIRouter, Response
from app.logging_config import setup_logging
logger = setup_logging()
router = APIRouter()

@router.get('', response_model=ListSubjectMenuResponse)
async def get_subject_menu(background_tasks: BackgroundTasks, db: Session = Depends(get_db), limit: int = 100, page: int = 1, user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.subject_menu], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)

    query = db.query(models.SubjectMenu)
    skip = (page - 1) * limit
    subject_menus = query.limit(limit).offset(skip).all()
    
    return {'status': 'success', 'results': len(subject_menus), 'subject_menus': subject_menus}

@router.post('', status_code=status.HTTP_201_CREATED, response_model=SubjectMenuResponse)
async def create_subject_menu(background_tasks: BackgroundTasks, payload: CreateSubjectMenuSchema, request: Request, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):

    oauth2.check_permissions_detail([PermissionEnum.subject_menu], [PermissionDetailEnum.create], user, background_tasks=background_tasks, db=db)
    check_exits_subject_menu = db.query(models.SubjectMenu).filter(models.SubjectMenu.code == payload.code).first()
    if check_exits_subject_menu:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'SubjectMenu exits code')
        
    try:
        new_subject_menu = models.SubjectMenu(**payload.dict())
        db.add(new_subject_menu)
        db.commit()
        db.refresh(new_subject_menu)

        return new_subject_menu
    except Exception as e:
        error_message = f"Error creating status. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot create status')

@router.get('/{id}', response_model=SubjectMenuResponse)
async def get_subject_menu(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.subject_menu], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)
    
    subject_menu_query = db.query(models.SubjectMenu).filter(models.SubjectMenu.id == id).first()
    if not subject_menu_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"SubjectMenu not found")
    return subject_menu_query

@router.put('/{id}', response_model=SubjectMenuResponse)
async def update_subject_menu(background_tasks: BackgroundTasks, id: UUID, payload: UpdateSubjectMenuSchema, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.subject_menu], [PermissionDetailEnum.write], user, background_tasks=background_tasks, db=db)
    
    subject_menu_query = db.query(models.SubjectMenu).filter(models.SubjectMenu.id == id)
    updated_subject_menu = subject_menu_query.first()

    if not updated_subject_menu:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'SubjectMenu not found')
    
    check_exits_subject_menu = db.query(models.SubjectMenu).filter(models.SubjectMenu.code == payload.code).first()
    if check_exits_subject_menu:
        if check_exits_subject_menu.id != updated_subject_menu.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'SubjectMenu exits code')

    try:
        subject_menu_query.update(payload.dict(exclude_unset=True), synchronize_session=False)
        db.commit()
        return updated_subject_menu
    
    except Exception as e:
        error_message = f"Error update SubjectMenu. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot update SubjectMenu')

@router.delete('/{id}')
async def delete_subject_menu(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.subject_menu], [PermissionDetailEnum.delete], user, background_tasks=background_tasks, db=db)

    subject_menu_query = db.query(models.SubjectMenu).filter(models.SubjectMenu.id == id)
    subject_menu_filter = subject_menu_query.first()
    if not subject_menu_filter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'SubjectMenu not found')

    subject_menu_using = db.query(models.Menu).filter(models.Menu.subject_id == id).first()
    if subject_menu_using:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Cannot delete subject menu. It is associated with one or more menu.')
    
    try:
        subject_menu_query.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        error_message = f"Error delete subject menu. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot delete subject menu')