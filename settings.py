# Scrapy settings for tushare_integration project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
from typing import Annotated, Any, Literal

import yaml
from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict



def env_validator(key, case_sensitive=False):
    env_vars = {k.lower(): v for k, v in os.environ.items()} if not case_sensitive else os.environ
    key = key.lower() if not case_sensitive else key

    def validator(v):
        if key in env_vars:
            return env_vars[key]
        return v

    return validator


def env_variable(env_key, case_sensitive=False):
    return BeforeValidator(env_validator(env_key, case_sensitive))


class DatabaseConfig(BaseSettings):
    # 数据库相关配置
    db_type: Annotated[Literal["clickhouse", "mysql", "doris"], env_variable('DB_TYPE')] = Field(
        ..., description='SQL模板'
    )

    host: Annotated[str, env_variable('DB_HOST')] = Field(..., description='数据库主机')
    port: Annotated[int, env_variable('DB_HOST')] = Field(..., description='数据库端口')
    user: Annotated[str, env_variable('DB_USER')] = Field(..., description='数据库用户名')
    password: Annotated[str, env_variable('DB_PASSWORD')] = Field('', description='数据库密码')

    db_name: Annotated[str, env_variable('DB_NAME')] = Field(..., description='数据库名称')
    template_params: dict[str, Any] = Field(default={}, description='SQL模板参数')

    def get_uri(self):
        if self.db_type == 'clickhouse':
            return f"clickhouse://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        elif self.db_type == 'mysql':
            return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        elif self.db_type == 'doris':
            return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}")

    model_config = SettingsConfigDict(extra='ignore')


# 使用pydantic定义数据模型
class KKDATADSettings(BaseSettings):
    pass