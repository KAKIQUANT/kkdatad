import clickhouse_connect
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateSchema
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlglot import Schema

from kkdatad.config import SQLALCHEMY_DATABASE_URL

async def get_cc_client():
    from kkdatad.config import CC_DATABASE_HOST, CC_DATABASE_PASSWORD, CC_DATABASE_PORT
    # Assuming you're using an async connection, adjust as per actual usage
    client = await clickhouse_connect.get_async_client(host=CC_DATABASE_HOST, username='default', password=CC_DATABASE_PASSWORD, port=CC_DATABASE_PORT)
    return client


# SQLAlchemy setup
engine = create_engine(
    SQLALCHEMY_DATABASE_URL.format(db='')
)
with engine.connect() as conn:
    conn.execute(CreateSchema('kkdatad',if_not_exists=True))

engine = create_engine(
    SQLALCHEMY_DATABASE_URL.format(db='kkdatad')
)
#我们创建了一个SessionLocal类的实例，这个实例将是实际的数据库会话。sessionmaker是sqlalchemy2.0的使用方式，1.4要使用Session(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#我们将用这个类继承，来创建每个数据库模型或类（ORM 模型）
Base = declarative_base()