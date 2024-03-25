from fastapi import APIRouter, BackgroundTasks, Request, Response, status, Depends, HTTPException
from app.schemas.enum import PermissionDetailEnum, PermissionEnum
from app.schemas.status import CreateStatusSchema, ListStatusResponse, UpdateStatusSchema, StatusResponse
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, oauth2
from uuid import UUID
from fastapi import Depends, HTTPException, status, APIRouter, Response
from app.logging_config import setup_logging
logger = setup_logging()
router = APIRouter()

@router.get('', response_model=ListStatusResponse)
async def get_status(background_tasks: BackgroundTasks, db: Session = Depends(get_db), limit: int = 100, page: int = 1, user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.statuses], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)

    query = db.query(models.Status)
    skip = (page - 1) * limit
    status = query.limit(limit).offset(skip).all()
    
    return {'status': 'success', 'results': len(status), 'statuses': status}

@router.post('', status_code=status.HTTP_201_CREATED, response_model=StatusResponse)
async def create_status(background_tasks: BackgroundTasks, payload: CreateStatusSchema, request: Request, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):

    oauth2.check_permissions_detail([PermissionEnum.statuses], [PermissionDetailEnum.create], user, background_tasks=background_tasks, db=db)
    
    try:
        new_status = models.Status(**payload.dict())
        db.add(new_status)
        db.commit()
        db.refresh(new_status)

        return new_status
    except Exception as e:
        error_message = f"Error creating status. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot create status')

@router.get('/{id}', response_model=StatusResponse)
async def get_status(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.statuses], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)
    
    status_query = db.query(models.Status).filter(models.Status.id == id).first()
    if not status_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Status not found")
    return status_query

@router.put('/{id}', response_model=StatusResponse)
async def update_status(background_tasks: BackgroundTasks, id: UUID, payload: UpdateStatusSchema, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.statuses], [PermissionDetailEnum.write], user, background_tasks=background_tasks, db=db)
    
    status_query = db.query(models.Status).filter(models.Status.id == id)
    updated_status = status_query.first()

    if not updated_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Status not found')
    try:
        status_query.update(payload.dict(exclude_unset=True), synchronize_session=False)
        db.commit()
        return updated_status
    except Exception as e:
        error_message = f"Error update status. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot update status')

@router.delete('/{id}')
async def delete_status(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.statuses], [PermissionDetailEnum.delete], user, background_tasks=background_tasks, db=db)

    status_query = db.query(models.Status).filter(models.Status.id == id)
    status_filter = status_query.first()
    if not status_filter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Status not found')

    status_detail = db.query(models.Schedule).filter(models.Schedule.status_id == id).first()
    if status_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Cannot delete status. It is associated with one or more status.')
    try:
        status_query.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        error_message = f"Error delete status. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot delete status')