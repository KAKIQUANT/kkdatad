"""
MySQL 数据库模型
User, Group, Auth, APIKey
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime, Float, JSON, Text
from kkdatad.utils.database import Base
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
    api_usage = relationship("APIUsage", back_populates="user", uselist=False)
    queries = relationship("QueryAnalytics", back_populates="user", cascade="all, delete-orphan")
    factors = relationship("Factor", back_populates="creator")
    factor_evaluations = relationship("FactorEvaluation", back_populates="user")

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

class APIUsage(Base):
    __tablename__ = 'api_usage'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    total_quota = Column(Integer, default=1000)  # Set default quota
    used_quota = Column(Integer, default=0)

    user = relationship("User", back_populates="api_usage")

class QueryAnalytics(Base):
    __tablename__ = 'query_analytics'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    query = Column(String(4096), nullable=False)
    execution_time = Column(Float, nullable=False)
    rows_returned = Column(Integer, nullable=False)
    error = Column(String(1024))
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="queries")

class Factor(Base):
    __tablename__ = 'factors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(60), unique=True, nullable=False)
    description = Column(String(255))
    category = Column(String(60), nullable=False)  # technical, fundamental, alternative
    version = Column(String(20), default="1.0.0")
    factor_metadata = Column(JSON)
    code = Column(Text, nullable=False)  # The actual factor computation code
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = Column(Boolean, default=False)
    
    # Relationships
    creator = relationship("User", back_populates="factors")
    evaluations = relationship("FactorEvaluation", back_populates="factor")

class FactorEvaluation(Base):
    __tablename__ = 'factor_evaluations'

    id = Column(Integer, primary_key=True, index=True)
    factor_id = Column(Integer, ForeignKey('factors.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    ic_mean = Column(Float)  # Information Coefficient mean
    ic_std = Column(Float)   # Information Coefficient std
    sharpe = Column(Float)   # Factor Sharpe ratio
    turnover = Column(Float) # Factor turnover
    evaluation_date = Column(DateTime, default=datetime.utcnow)
    evaluation_metadata = Column(JSON)  # Changed from metadata to evaluation_metadata
    
    factor = relationship("Factor", back_populates="evaluations")
    user = relationship("User", back_populates="factor_evaluations")