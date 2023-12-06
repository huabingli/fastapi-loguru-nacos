#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @文件       :commonality.py
# @时间       :2023/12/5 下午2:37
# @作者       :lihb
# @说明       : 公共函数
import hashlib
import mmap
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


class SharedEnumMmap:
    def __init__(self, mmap_size=1024):
        """
        初始化SharedEnumMmap对象，创建一个共享的mmap对象。

        Parameters:
        - mmap_size (int): mmap的大小，默认为1024字节。
        """
        self.mmap_size = mmap_size
        # 创建共享的mmap对象，用于存储Enum的值
        self.mm = mmap.mmap(-1, mmap_size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)

    def write_enum_value(self, enum_value):
        """
        将Enum的值写入mmap。

        Parameters:
        - enum_value: Enum对象，要写入的Enum值。
        """
        # 将Enum的值转换为字节串，并写入mmap
        enum_str = enum_value.encode('utf-8')
        self.mm.resize(len(enum_str))
        self.mm.seek(0)
        self.mm.write(enum_str)

    def read_enum_value(self):
        """
        从mmap中读取Enum的值。

        Returns:
        - Enum: 读取的Enum值。
        """
        # 从mmap中读取字节串，并转换为Enum对象
        self.mm.seek(0)
        shared_enum_str = self.mm.read(len(self.mm))
        shared_enum_value = shared_enum_str.decode('utf-8')
        return shared_enum_value

    def close(self):
        """
        关闭mmap。
        """
        self.mm.close()
