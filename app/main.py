from datetime import datetime
import json
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import httpx
from app import models
from app.config import Settings
from app.database import SessionLocal, get_db
from app.logging_config import setup_logging
from app.routers import user, auth, role, permission, category, status, permission_detail, menu, sub_menu, subject_menu
import pytz
from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket, Depends, WebSocketDisconnect, Query
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import HTMLResponse
from app.utils import RedisManager, active_websockets
from sqlalchemy.orm import Session
from app.config import settings
from fastapi import Depends
import asyncio
from sqlalchemy import update

logger = setup_logging()
app = FastAPI(
    title="Stream API DOCS",
    version="1.0.0",
)


# app.mount("/statics", StaticFiles(directory=Path(__file__).parent / "statics"), name="static")

# origins = [
#     settings.CLIENT_ORIGIN,
# ]

origins = [
    "*"
]
app.state.timezone = pytz.timezone('Asia/Manila')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')
app.include_router(user.router, tags=['Users'], prefix='/api/users')
app.include_router(subject_menu.router, tags=['Subject Menu'], prefix='/api/subject-menu')
app.include_router(menu.router, tags=['Menu'], prefix='/api/menu')
app.include_router(sub_menu.router, tags=['Sub Menu'], prefix='/api/sub-menu')
app.include_router(role.router, tags=['Roles'], prefix='/api/roles')
app.include_router(permission.router, tags=['Permissions'], prefix='/api/permissions')
app.include_router(permission_detail.router, tags=['Permissions Detail'], prefix='/api/permissions-detail')
app.include_router(category.router, tags=['Categories'], prefix='/api/categories')
app.include_router(status.router, tags=['Status'], prefix='/api/status')