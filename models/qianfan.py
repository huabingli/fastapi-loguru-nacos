#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @文件       :qianfan.py
# @时间       :2023/12/4 下午3:30
# @作者       :lihb
# @说明       :
from typing import Optional

from pydantic import BaseModel, Field


class QianFanRequest(BaseModel):
    user_id: Optional[int] = Field(None, description='用户ID')
    content: str = Field(..., description='提问问题')
    system: str = Field('你是一名光荣的人民教师', description='模型人设，主要用于人设设定，例如，你是一名光荣的人民教师')
