#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @文件       :lifespan_handler.py
# @时间       :2023/12/5 下午4:53
# @作者       :lihb
# @说明       :
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.nacos import NacosHelper
from utils.scheduler import scheduler


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler.start()
    nacos_helper = NacosHelper()
    # 第一次加载配置文件
    nacos_helper.load_conf()
    # 监听配置是否有变化
    nacos_helper.run_listener_config_thread()
    # 注册实例
    nacos_helper.add_instance()
    # 发送心跳到nacos
    scheduler.add_job(nacos_helper.put_instance, 'interval', seconds=5)
    yield
    scheduler.shutdown()
    nacos_helper.close()