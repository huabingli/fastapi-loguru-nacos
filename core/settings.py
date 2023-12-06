#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @文件       :settings.py
# @时间       :2023/9/21 上午11:04
# @作者       :lihb
# @说明       :
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSetting(BaseModel):
    pass
    # db_url: MariaDBDsn | MySQLDsn = 'mariadb+pymysql://root:zwjy.com@192.168.80.236:32312/devops_test3??charset=utf8mb4'
    # redis_url: RedisDsn = 'redis://'


class QianFan(BaseModel):
    """https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application"""
    qianfan_ak: str = Field('tdduECDHthXumTdZ5me0PyXj', description='百度智能云千帆应用API Key（即AK）')
    qianfan_sk: str = Field('zGejmnmTu4bRDiTsmSlpsuNP19vr3wzQ', description='百度智能云千帆的应用Secret Key（即SK）')
    appid: int = Field(44279065, description='百度智能云千帆的应用ID')


class Base(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter='__', env_file=None)

    base_dir: Path = Path(__file__).resolve().parent.parent
    log_level: str = 'INFO'

    @property
    def base_dir_str(self) -> str:
        return str(self.base_dir)

    def update_data(self, data: dict):
        try:
            updated_model = self.model_validate(data)
        except ValidationError as e:
            raise ValueError(f"Invalid data: {e.errors()}")

        for field_name, field_value in updated_model:
            if hasattr(self, field_name):
                setattr(self, field_name, field_value)


class Settings(Base):
    db: DBSetting = DBSetting()
    qianfan: QianFan = QianFan()


if __name__ == '__main__':
    pass
    # print(get_nacos_settings('dev'))
