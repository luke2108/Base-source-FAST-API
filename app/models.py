import uuid
from .database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, Boolean, text, INTEGER
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name = Column(String(length=50), nullable=False)
    code = Column(String(length=50), nullable=True)
    description = Column(String(length=500), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    roles = relationship('RolePermission', back_populates='permission', cascade='all, delete-orphan', single_parent=True)
    permissions_detail = relationship('PermissionDetail', back_populates='permissions', cascade='all, delete-orphan', single_parent=True)

    __table_args__ = (
        UniqueConstraint('name', 'code'),
    )

class PermissionDetail(Base):
    __tablename__ = 'permissions_detail'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    permission_id = Column(UUID(as_uuid=True), ForeignKey('permissions.id'))
    name = Column(String(length=50), nullable=False)
    code = Column(String(length=50), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    permissions = relationship('Permission', back_populates='permissions_detail')
    role_permission_details = relationship('RolePermissionDetail', back_populates='permission_detail')

    __table_args__ = (
        UniqueConstraint('permission_id', 'code'),
    )

class RolePermission(Base):
    __tablename__ = 'role_permissions'
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True)

    permission = relationship('Permission', back_populates='roles')
    role = relationship('Role', back_populates='permissions', passive_deletes=True)

class RolePermissionDetail(Base):
    __tablename__ = 'role_permission_details'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'))
    permission_detail_id = Column(UUID(as_uuid=True), ForeignKey('permissions_detail.id'))
    
    role = relationship('Role', back_populates='permission_details')
    permission_detail = relationship('PermissionDetail', back_populates='role_permission_details')

class UserMeta(Base):
    __tablename__ = 'user_meta'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    meta_code = Column(String(length=100) , nullable=False)
    meta_name = Column(String(length=100), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    details = relationship('UserMetaDetail', back_populates='meta', cascade='all, delete-orphan', single_parent=True)
    role_meta = relationship('Role', back_populates='role_user_meta')

class UserMetaDetail(Base):
    __tablename__ = 'user_meta_detail'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    meta_id = Column(UUID(as_uuid=True), ForeignKey('user_meta.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    meta_value = Column(String(length=250), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    meta = relationship('UserMeta', back_populates='details')
    user = relationship('User', back_populates='user_meta_details')

class Category(Base):
    __tablename__ = 'categories'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name = Column(String(length=250), nullable=True)
    code = Column(String(length=250), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    # schedules = relationship('Schedule', back_populates='category', cascade='all, delete-orphan', single_parent=True)

class Status(Base):
    __tablename__ = 'statuses'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    title = Column(String(length=250), nullable=True)
    type = Column(String(length=250), nullable=True)
    color = Column(String(length=100), nullable=True)
    code = Column(String(length=50), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    # schedules = relationship('Schedule', back_populates='status', cascade='all, delete-orphan', single_parent=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name = Column(String(length=250), nullable=False)
    email = Column(String(length=250), unique=True, nullable=False)
    avatar = Column(String(length=550), nullable=True)
    password = Column(String, nullable=False)
    is_activate = Column(Boolean, default=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
    role = relationship('Role', back_populates='users')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    user_meta_details = relationship('UserMetaDetail', back_populates='user')
    # rooms = relationship('Room', back_populates='user')
    user = relationship('UserHisory', back_populates='user')

class UserHisory(Base):
    __tablename__ = 'user_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    permission = Column(String(length=50), nullable=True)
    permission_detail = Column(String(length=50), nullable=True)
    email = Column(String, nullable=True)
    status_code = Column(INTEGER, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    user = relationship('User', back_populates='user')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

class Role(Base):
    __tablename__ = 'roles'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name = Column(String(length=250), nullable=False)
    code = Column(String(length=50), unique=True, nullable=True)
    icon = Column(String(length=50), nullable=True)
    color = Column(String(length=50), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    permissions = relationship('RolePermission', back_populates='role', cascade='all, delete-orphan', single_parent=True)
    permission_details = relationship('RolePermissionDetail', back_populates='role', cascade='all, delete-orphan', single_parent=True)
    users = relationship('User', back_populates='role', cascade='all, delete-orphan', single_parent=True)
    
    role_menus = relationship('RoleMenu', back_populates='role', cascade='all, delete-orphan', single_parent=True)
    role_user_meta = relationship('UserMeta', back_populates='role_meta')

class SubjectMenu(Base):
    __tablename__ = 'subject_menu'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name = Column(String(length=250), nullable=False)
    code = Column(String(length=250), nullable=False)
    position = Column(INTEGER, nullable=False)
    icon = Column(String(length=250), nullable=True)
    decscript = Column(String(length=500), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    menu = relationship('Menu', back_populates='menu_subject', cascade='all, delete-orphan', single_parent=True)

class Menu(Base):
    __tablename__ = 'menus'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    subject_id = Column(UUID(as_uuid=True), ForeignKey('subject_menu.id'), nullable=True)
    name = Column(String(length=250), nullable=False)
    code = Column(String(length=250), nullable=False)
    position = Column(INTEGER, nullable=True)
    icon = Column(String(length=250), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    sub_menu = relationship('SubMenu', back_populates='menu', cascade='all, delete-orphan', single_parent=True)
    menu = relationship('RoleMenu', back_populates='menu', cascade='all, delete-orphan', single_parent=True)
    menu_subject = relationship('SubjectMenu', back_populates='menu', cascade='all, delete-orphan', single_parent=True)

class SubMenu(Base):
    __tablename__ = 'submenus'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menus.id'), primary_key=True)
    name = Column(String(length=250), nullable=False)
    code = Column(String(length=250), nullable=False)
    icon = Column(String(length=250), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    menu = relationship('Menu', back_populates='sub_menu', cascade='all, delete-orphan', single_parent=True)

class RoleMenu(Base):
    __tablename__ = 'role_menus'
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menus.id'), primary_key=True)
    role = relationship('Role', back_populates='role_menus')
    menu = relationship('Menu', back_populates='menu')