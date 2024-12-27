import clickhouse_connect
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateSchema
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from kkdatad.utils.config import settings

async def get_cc_client():
    client = await clickhouse_connect.get_async_client(
        host=settings.CC_DATABASE_HOST,
        username='default',
        password=settings.CC_DATABASE_PASSWORD,
        port=settings.CC_DATABASE_PORT
    )
    return client

#我们将用这个类继承，来创建每个数据库模型或类（ORM 模型）
Base = declarative_base()

# SQLAlchemy setup
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL.format(db='')
)
with engine.connect() as conn:
    conn.execute(CreateSchema('kkdatad', if_not_exists=True))

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL.format(db='kkdatad')
)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

#我们创建了一个SessionLocal类的实例，这个实例将是实际的数据库会话。sessionmaker是sqlalchemy2.0的使用方式，1.4要使用Session(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Add the get_db dependency function
def get_db():
    """Dependency function to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()