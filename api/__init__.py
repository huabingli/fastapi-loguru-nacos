#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @文件       :__init__.py.py
# @时间       :2023/9/21 上午10:05
# @作者       :lihb
# @说明       :
from fastapi import APIRouter

from . import openai_gpt_api

router = APIRouter(prefix='/api')
router.include_router(router=openai_gpt_api.router)
# router.include_router(shandong_chemistry.router)
