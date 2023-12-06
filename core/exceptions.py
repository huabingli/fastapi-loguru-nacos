#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @文件       :exceptions.py
# @时间       :2023/9/21 上午11:04
# @作者       :lihb
# @说明       :

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.requests import Request
from starlette.responses import JSONResponse

from schemas.base import R


# logger = logging.getLogger(__name__)

class AiChatException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def exception_handler(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """处理请求验证错误"""
        # 记录日志并带上请求信息和验证错误详情
        logger.warning(f'Request validation error occurred for request {request.url}:{exc}')
        fail = R.fail(msg='校验错误', err=jsonable_encoder({"detail": exc.errors(), "body": exc.body}), code=422)
        return JSONResponse(content=fail.model_dump(), status_code=fail.code)

    @app.exception_handler(HTTPException)
    async def http_exception(request: Request, exc: HTTPException):
        """处理 HTTP 错误"""
        # 记录日志
        logger.warning(f'HTTP error occurred for request {request.url}:{exc.detail}')
        fail = R.fail('请求错误', code=exc.status_code or 400, err=jsonable_encoder({"detail": exc.detail}))
        return JSONResponse(content=fail.model_dump(), status_code=fail.code)

    @app.exception_handler(AiChatException)
    async def ai_chat_exception(request: Request, exc: AiChatException):
        logger.warning(f'自定义错误 {request.url}:{exc.message}')
        fail = R.fail(msg='自定义错误', code=400, err=jsonable_encoder({'detail': exc.message}))
        return JSONResponse(content=fail.model_dump(), status_code=fail.code)
