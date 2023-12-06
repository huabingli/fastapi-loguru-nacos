#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @文件       :nacos.py
# @时间       :2023/12/5 上午10:14
# @作者       :lihb
# @说明       : 进行读写配置和注册服务
import json
import threading
import time
from enum import Enum
from functools import cached_property, lru_cache

import httpx
import yaml
from loguru import logger
from pydantic import Field, HttpUrl, IPvAnyAddress
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.config import settings
from core.exceptions import AiChatException
from core.log import setup_logging
from utils.commonality import SharedEnumMmap, calculate_md5, get_host_ip


class EnvEnum(str, Enum):
    dev = 'dev'
    test = 'test'
    pre = 'pre'
    prod = 'prod'


environment = SharedEnumMmap()


class Nacos(BaseSettings):
    app_name: str = Field('zw-ai-chat', description='app名称')
    app_ip: IPvAnyAddress = Field(default_factory=get_host_ip, description='本机IP地址')
    app_port: int = Field(8000, description='启动端口号')
    server_add: HttpUrl = Field('http://192.168.90.108:8848', description='nacos的地址')
    file_extension: str = Field('yml', description='文件类型')
    namespace: str = Field('5d540982-f0c0-4717-874a-8fee7d44440a', description='nacos命名空间')
    group: str = Field('DEV_GROUP', description='nacos组')
    username: str = Field('nacos', description='nacos用户')
    password: str = Field('zwjy@2021', description='nacos组')
    model_config = SettingsConfigDict(env_prefix='nacos_')


@lru_cache()
def get_nacos_settings(env: SharedEnumMmap):
    from core.config import settings
    return Nacos(_env_file=f'{settings.base_dir_str}/.env.{env.read_enum_value()}')


class NacosHelper:
    def __init__(self):
        self._cached_token = None
        self._content_md5 = None
        self.settings = get_nacos_settings(environment)
        self.headers = {
            # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self.client = httpx.Client(base_url=str(self.settings.server_add), headers=self.headers, timeout=30)

    @staticmethod
    def err_status(res: httpx.Response):
        """判断是否查询失败"""
        match res.status_code:
            case 200:
                return True
            case 400:
                raise AiChatException(f'客户端请求中的语法错误 text: {res.text}')
            case 403:
                raise AiChatException(f'没有权限 text: {res.text}')
            case 404:
                raise AiChatException(f'无法找到资源 text: {res.text}')
            case 500:
                raise AiChatException(f'服务器内部错误, text: {res.text}')
            case _:
                raise AiChatException(f'未知错误 status: {res.status_code}, text: {res.text}')

    @property
    def get_nacos_token(self):
        """获取nacos token"""
        if hasattr(self, '_cached_token') and self._cached_token and self._cached_token.get('expiration_time', 0) > int(
                time.time() * 1000):
            return self._cached_token.get('accessToken')  # 返回缓存的 token 数据
        nacos_uri = f'/nacos/v1/auth/login'

        data = {
            'username': self.settings.username,
            'password': self.settings.password
        }
        response = self.client.post(nacos_uri, data=data)
        response.raise_for_status()
        token_data = response.json()

        token_info = {
            'accessToken': token_data['accessToken'],
            'tokenTtl': token_data['tokenTtl'],
            'expiration_time': int(time.time() * 1000) + token_data['tokenTtl'] * 1000
        }
        logger.info(f'获取nacos的token: {token_info}')
        # 缓存 token 数据
        self._cached_token = token_info

        return token_info['accessToken']

    def load_conf(self):
        """ 获取nacos配置

        :return:
        """
        url = f'/nacos/v1/cs/configs'
        params = {
            'tenant': self.settings.namespace,
            'accessToken': self.get_nacos_token,
            'dataId': f'{self.settings.app_name}.{self.settings.file_extension}',
            'group': self.settings.group
        }
        res = self.client.get(url, params=params)
        self.err_status(res)
        text = res.text
        logger.info(f'获取nacos配置\n{text}')
        self._content_md5 = calculate_md5(text)
        settings.update_data(yaml.safe_load(text))
        # settings = settings.model_validate(yaml.safe_load(text))
        logger.info(f'重新加载setting配置 {settings.model_dump_json(indent=2)}')
        return text

    def listener_conf(self):
        """ 监听nacos配置是否改变

        :return: 如果配置无变化：会返回空串
        """
        # 轮训等待时间也就是说，等待多长时间会检查一次 秒
        timeout = 30
        headers = {'Long-Pulling-Timeout': str(timeout * 1000)}
        headers.update(**self.headers)
        url = f'/nacos/v1/cs/configs/listener'
        data = f"Listening-Configs={self.settings.app_name}.{self.settings.file_extension}%02{self.settings.group}%02{self._content_md5 if self._content_md5 else ''}%02{self.settings.namespace}%01"
        try:
            res = self.client.post(url, data=data, headers=headers, timeout=timeout + 10)
            self.err_status(res)
            logger.debug(f'监听nacos配置是否改变, status: {res.status_code}, 内容{"有变化" if res.text else "未变化"}')
            return res.text
        except (httpx.HTTPError, AiChatException) as exc:
            logger.exception(exc)
            time.sleep(18)
            return False
        # print(res.text, res.status_code)

    def run_listener_config_thread(self):
        """后台运行监听nacos配置实例"""
        # 使用 threading.Thread 创建一个新线程，目标为 listener_conf 方法
        listener_thread = threading.Thread(target=self.listener_thread_worker)
        # 将新线程设置为守护线程，确保主程序退出时线程也会退出
        listener_thread.daemon = True
        # 启动新线程
        listener_thread.start()
        # 注册实例
        self.add_instance()
        # 使用 threading.Thread 创建一个新线程，目标为 put_instance 方法
        instance_thread = threading.Thread(target=self.instance_beat_thread_worker)
        # 将新线程设置为守护线程，确保主程序退出时线程也会退出
        instance_thread.daemon = True
        # 启动新线程
        instance_thread.start()

    def listener_thread_worker(self):
        """线程工作函数，用于运行 listener_conf 方法"""
        while True:
            config_text = self.listener_conf()
            if config_text:
                # 处理配置文本的逻辑，更新应用程序配置等
                self.load_conf()
                setup_logging()
            # 可以选择在一段时间后再次运行 listener_conf 方法，或者根据需求进行其他逻辑

    def instance_beat_thread_worker(self):
        """线程工作函数，用于运行 put_instance 方法"""
        while True:
            time.sleep(4)
            self.put_instance()

    def add_instance(self):
        """注册一个实例到nacos。

        :return: 返回是否注册成功
        """
        url = '/nacos/v1/ns/instance'
        params = {
            'accessToken': self.get_nacos_token,
            'port': self.settings.app_port,
            'ip': str(self.settings.app_ip),
            'weight': 1.0,
            'serviceName': self.settings.app_name,
            'groupName': self.settings.group,
            'encoding': 'UTF-8',
            'enabled': 'true',
            'healthy': 'true',
            'namespaceId': self.settings.namespace,
            "metadata": json.dumps({"preserved.register.source": "SPRING_CLOUD"})
            # 'metadata': {"preserved.register.source": "SPRING_CLOUD"}
        }
        res = self.client.post(url, params=params)
        self.err_status(res)
        logger.info(f'注册实例到nacos {res.text}')
        return True if res.text == 'ok' else False

    def del_instance(self):
        """ 注销实例

        :return:
        """
        url = f'/nacos/v1/ns/instance'
        params = {
            'accessToken': self.get_nacos_token,
            'serviceName': self.settings.app_name,
            'ip': str(self.settings.app_ip),
            'port': self.settings.app_port,
            'groupName': self.settings.group,
            'enabled': 'false',
            'namespaceId': self.settings.namespace,
        }
        res = self.client.delete(url, params=params)
        self.err_status(res)
        logger.info(f'从nacos注销实例 {res.text}')
        return True if res.text == 'ok' else False

    @cached_property
    def get_instance(self):
        """ 查询实例详情

        :return: 查询到的详情
        """
        url = '/nacos/v1/ns/instance'
        params = {
            'accessToken': self.get_nacos_token,
            'serviceName': self.settings.app_name,
            'ip': str(self.settings.app_ip),
            'port': self.settings.app_port,
            'groupName': self.settings.group,
            'namespaceId': self.settings.namespace,
        }
        res = self.client.get(url, params=params)
        self.err_status(res)
        logger.debug(f'查询实例详情 {res.text}')
        return res.text

    @cached_property
    def _put_instance_params(self):
        params = {
            # 'accessToken': self.get_nacos_token,
            'encoding': 'UTF-8',
            'serviceName': f"{self.settings.group}@@{self.settings.app_name}",
            'namespaceId': self.settings.namespace,
            'app': 'unknown',
            'beat': json.dumps({"cluster": "DEFAULT", "ip": str(self.settings.app_ip),
                                "metadata": {"preserved.register.source": "SPRING_CLOUD"}, "period": 5000,
                                "port": self.settings.app_port, "scheduled": False,
                                "serviceName": f"{self.settings.group}@@{self.settings.app_name}", "stopped": False,
                                "weight": 1.0})
        }
        return params

    def put_instance(self):
        """发送实例的心跳

        :return:
        """
        url = f'/nacos/v1/ns/instance/beat'

        try:
            res = self.client.put(url, params=self._put_instance_params)
            self.err_status(res)
        except (httpx.HTTPError, AiChatException) as exc:
            logger.exception(exc)
            return False
        res_json = res.json()

        logger.debug(f'发送实例心跳 {res_json}')
        return res_json['lightBeatEnabled']

    def close(self):
        self.del_instance()
        self.client.close()


if __name__ == '__main__':
    n = NacosHelper()
    n.load_conf()
    n.add_instance()
    time.sleep(1)
    try:
        while True:
            test = n.listener_conf()
            if test:
                n.load_conf()
            # time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        n.del_instance()
        n.close()
    # print(settings.qianfan.qianfan_sk)
#     # print(get_host_ip())
