#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @文件       :scheduler.py.py
# @时间       :2023/12/5 下午4:57
# @作者       :lihb
# @说明       :
import asyncio

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler

loop = asyncio.get_event_loop()

ascheduler = AsyncIOScheduler(event_loop=loop, timezone='Asia/Shanghai')
scheduler = BackgroundScheduler(executors={'threadpool': ThreadPoolExecutor()})
