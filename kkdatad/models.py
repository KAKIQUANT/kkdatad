"""
MySQL 数据库模型
User, Group, Auth, APIKey
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime
from kkdatad.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Group(Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    # : name of group
    # : 权限组名称
    name = Column(String(60), comment="权限组名称")
    # a description of a group
    # 权限组描述
    info = Column(String(255), comment="权限组描述")


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(60), unique=True, index=True, nullable=False)
    password = Column(String(60), nullable=False)
    nickname = Column(String(60))
    email = Column(String(60))
    isadmin = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    invite_codes = relationship("InviteCode", back_populates="creator", cascade="all, delete-orphan")

class Auth(Base):
    __tablename__ = 'auth'

    id = Column(Integer, primary_key=True)
    # : 权限字段
    auth = Column(String(60), comment="权限字段")
    # : 权限的模块
    endpoint = Column(String(60), comment="路由名称")

class APIKey(Base):
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(60), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="api_keys")

class InviteCode(Base):
    __tablename__ = 'invite_codes'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(60), unique=True, index=True, nullable=False)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationships
    creator = relationship("User", back_populates="invite_codes")

