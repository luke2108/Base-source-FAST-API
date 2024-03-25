from app.schemas.category import CategoryResponse
from fastapi import APIRouter, BackgroundTasks, Request, Response, status, Depends, HTTPException
from app.schemas.category import CreateCategorySchema, ListCategoryResponse, UpdateCategorySchema
from app.schemas.enum import PermissionDetailEnum, PermissionEnum
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, oauth2
from uuid import UUID
from fastapi import Depends, HTTPException, status, APIRouter, Response
from app.logging_config import setup_logging
logger = setup_logging()
router = APIRouter()

@router.get('', response_model=ListCategoryResponse)
async def get_category(background_tasks: BackgroundTasks, db: Session = Depends(get_db), limit: int = 100, page: int = 1,  name: str='', user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.categories], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)
    skip = (page - 1) * limit
    categories = db.query(models.Category).filter(
        models.Category.name.contains(name)).limit(limit).offset(skip).all()
    
    return {'status': 'success', 'results': len(categories), 'categories': categories}

@router.post('', status_code=status.HTTP_201_CREATED, response_model=CategoryResponse)
async def create_category(background_tasks: BackgroundTasks, payload: CreateCategorySchema, request: Request, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.categories], [PermissionDetailEnum.create], user, background_tasks=background_tasks, db=db)
    try:
        new_category = models.Category(**payload.dict())
        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return new_category
    except Exception as e:
        error_message = f"Error creating catgory. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot create catgory')

@router.get('/{id}', response_model=CategoryResponse)
async def get_category(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.categories], [PermissionDetailEnum.read], user, background_tasks=background_tasks, db=db)
    
    permission = db.query(models.Category).filter(models.Category.id == id).first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Category not found")
    return permission


@router.put('/{id}', response_model=CategoryResponse)
async def update_category(background_tasks: BackgroundTasks, id: UUID, payload: UpdateCategorySchema, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.categories], [PermissionDetailEnum.write], user, background_tasks=background_tasks, db=db)
    category_query = db.query(models.Category).filter(models.Category.id == id)
    updated_category = category_query.first()

    if not updated_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Category not found')
    try:
        category_query.update(payload.dict(exclude_unset=True), synchronize_session=False)
        db.commit()

        return updated_category
    except Exception as e:
        error_message = f"Error update catgory. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot update catgory')

@router.delete('/{id}')
async def delete_category(background_tasks: BackgroundTasks, id: UUID, db: Session = Depends(get_db), user: str = Depends(oauth2.require_user)):
    oauth2.check_permissions_detail([PermissionEnum.categories], [PermissionDetailEnum.delete], user, background_tasks=background_tasks, db=db)
    category_query = db.query(models.Category).filter(models.Category.id == id)
    permission = category_query.first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Category not found')

    # category_detail = db.query(models.Schedule).filter(models.Schedule.category_id == id).first()
    # if category_detail:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Cannot delete category. It is associated with one or more category.')

    try:
        category_query.delete(synchronize_session=False)
        db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        error_message = f"Error delete catgory. Error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot delete catgory')
    

