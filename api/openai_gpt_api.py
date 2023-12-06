#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @文件       :openai_gpt_api.py
# @时间       :2023/12/4 下午5:44
# @作者       :lihb
# @说明       :

from fastapi import APIRouter

router = APIRouter(prefix='/openai_gpt', tags=['openai Gpt'])


@router.post('/')
def get_():
    pass
