#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @文件       :config.py.py
# @时间       :2023/9/21 上午11:03
# @作者       :lihb
# @说明       :
from contextvars import ContextVar

from .settings import Settings

settings = Settings()
request_id_var: ContextVar[str] = ContextVar("request-id", default="")

request_time_it_var: ContextVar[str] = ContextVar('process-time', default="")
