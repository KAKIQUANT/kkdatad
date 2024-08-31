"""
MySQL 数据库模型
User, Group, Auth, APIKey
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime
from kkdatad.database import Base

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
    __tablename__ = "user" # 数据库表名
    id = Column(Integer,primary_key=True)
    username = Column(String(24), nullable=False, unique=True, comment="用户名")
    password = Column(String(500), nullable=False, comment="密码")
    nickname = Column(String(100),nullable=True, comment="昵称")
    email = Column(String(100), nullable=True,  comment="电子邮箱")
    isadmin = Column(Boolean,default=False,comment="管理员")

class Auth(Base):
    __tablename__ = 'auth'

    id = Column(Integer, primary_key=True)
    # : 权限字段
    auth = Column(String(60), comment="权限字段")
    # : 权限的模块
    endpoint = Column(String(60), comment="路由名称")

class APIKey(Base):
    __tablename__ = 'api-key'

    id = Column(Integer, primary_key=True)
    # : API
    api_key = Column(String(60), comment="API")
