#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @文件       :commonality.py
# @时间       :2023/12/5 下午2:37
# @作者       :lihb
# @说明       : 公共函数
import hashlib
import socket

from loguru import logger


def calculate_md5(data):
    """ 计算data的MD5值

    :param data: 内容
    :return: MD5值
    """
    md5_hash = hashlib.md5()
    md5_hash.update(data.encode('utf-8'))
    md5 = md5_hash.hexdigest()
    logger.debug(f'生成MD5: {md5}')
    return md5


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        if not s:
            s.close()
    return ip
