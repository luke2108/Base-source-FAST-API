import uuid
from app.schemas.enum import PermissionDetailEnum, PermissionEnum
from app.schemas.permisson_detail import ListPermissionDetailResponse, PermissionDetailResponse, UpdatePermissionDetailSchema
from .. import models
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, Depends, HTTPException, status, APIRouter, Response
from app.oauth2 import require_user, check_permissions_detail
from uuid import UUID
from ..database import get_db
from app.logging_config import setup_logging

router = APIRouter()
logger = setup_logging()

@router.get('', response_model=ListPermissionDetailResponse)
async def get_permissions_detail(background_tasks: BackgroundTasks, db: Session = Depends(get_db), permission_id: UUID = None, user: str = Depends(require_user)):
    check_permissions_detail([PermissionEnum.permission_detail], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)
    
    if permission_id:
        permission_detail_list = db.query(models.PermissionDetail).filter(models.PermissionDetail.permission_id == permission_id).all()
    else:
        permission_detail_list = db.query(models.PermissionDetail).all()
    return {'status': 'success', 'results': len(permission_detail_list), 'permissions_detail': permission_detail_list}

@router.post('', status_code=status.HTTP_201_CREATED, response_model=PermissionDetailResponse)
async def create_permission_detail(background_tasks: BackgroundTasks, permission_detail: UpdatePermissionDetailSchema, db: Session = Depends(get_db), user: str = Depends(require_user)):
        check_permissions_detail([PermissionEnum.permission_detail], [PermissionDetailEnum.create], user, background_tasks=background_tasks, db=db)
        
        permission_detail.code = permission_detail.code.lower()
        existing_permission = db.query(models.PermissionDetail).filter(models.PermissionDetail.code == permission_detail.code, models.PermissionDetail.permission_id == permission_detail.permission_id).first()

        if existing_permission:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission Detail code already exists")
        
        try:
            new_permission_detail = models.PermissionDetail(**permission_detail.dict())
            db.add(new_permission_detail)
            db.commit()
            db.refresh(new_permission_detail)


            return new_permission_detail
        except Exception as e:
            error_message = f"Error creating permission detail. Error: {str(e)}"
            logger.error(error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot create permission detail')
    
@router.put('/{id}', response_model=PermissionDetailResponse)
async def update_permission_detail(background_tasks: BackgroundTasks, id: UUID, permision: UpdatePermissionDetailSchema, db: Session = Depends(get_db), user: str = Depends(require_user)):
    check_permissions_detail([PermissionEnum.permission_detail], [PermissionDetailEnum.write], user, background_tasks=background_tasks, db=db)
    
    permission_detail_query = db.query(models.PermissionDetail).filter(models.PermissionDetail.id == id)
    updated_Permission_detail = permission_detail_query.first()

    if not updated_Permission_detail:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Permission detail not found')
    try:
        permission_detail_query.update(permision.dict(exclude_unset=True), synchronize_session=False)
        db.commit()
        return updated_Permission_detail
    except Exception as e:
        error_message = f"Error update permission detail. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot update permission detail. Maybe permission detail already exists')

@router.get('/{id}', response_model=PermissionDetailResponse)
async def get_permission_detail(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(require_user)):
    check_permissions_detail([PermissionEnum.permission_detail], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)
    
    permission_detail = db.query(models.PermissionDetail).filter(models.PermissionDetail.id == id).first()
    if not permission_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Permission Detail not found")
    return permission_detail

@router.delete('/{id}')
async def delete_permission(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(require_user)):
    check_permissions_detail([PermissionEnum.permission_detail], [PermissionDetailEnum.delete], user, background_tasks=background_tasks, db=db)

    permission_detail = db.query(models.PermissionDetail).filter(models.PermissionDetail.id == id).first()
    if not permission_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Permission Detail not found')

    db.delete(permission_detail)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
