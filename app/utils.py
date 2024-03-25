from passlib.context import CryptContext
import uuid
from typing import Dict
from starlette.websockets import WebSocket, WebSocketState
from sqlalchemy.orm import Session
from .models import User, Role
from typing import Dict, List
from sqlalchemy.orm import Session
from app.database import SessionLocal
import random
import string
from app import models
import redis
from app.logging_config import setup_logging
logger = setup_logging()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=1)

# User connnect websocket Store
active_websockets: Dict[str, List[WebSocket]] = {}

async def hash_password(password: str):
    return pwd_context.hash(password)

async def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)

def get_user_ids_by_roles(db: Session, roles: list):
    role_ids = db.query(Role.id).filter(Role.name.in_(roles)).all()

    user_ids = (
        db.query(User.id)
        .filter(User.role_id.in_([role_id for (role_id,) in role_ids]))
        .filter(User.is_activate == True)
        .all()
    )

    return [user_id for (user_id,) in user_ids]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RedisManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RedisManager, cls).__new__(cls)
            cls._instance._redis = redis.Redis(host="localhost", port=6379, db=0)
        return cls._instance

    def get_redis(self):
        return self._redis