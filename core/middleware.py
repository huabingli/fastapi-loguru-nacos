#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @文件       :middleware.py
# @时间       :2023/9/21 上午11:15
# @作者       :lihb
# @说明       : 中间件
import time
import uuid

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.config import request_id_var, request_time_it_var


# logger = logging.getLogger(__name__)


class ContextMiddleware(BaseHTTPMiddleware):

    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()
        # 为日志添加链路ID
        REQUEST_ID_KEY = "X-Request-Id"
        request_id = request.headers.get(REQUEST_ID_KEY, str(uuid.uuid4()))
        request_id_var.set(request_id)
        response = await call_next(request)
        process_time = time.time() - start_time
        request_time_it_var.set(f'{process_time: .3f}')

        return response


def add_middleware(app: FastAPI):
    app.add_middleware(ContextMiddleware)
    app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],  # 一个允许跨域请求的 HTTP 方法列表
            allow_headers=["*"],  # 一个允许跨域请求的 HTTP 请求头列表
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
