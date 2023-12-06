# FastAPI + Loguru + Nacos 示例项目

本项目演示了如何使用 FastAPI 和 Loguru 结合 Nacos 从远程加载配置，并根据指定环境运行应用程序。

## 环境要求

- Python 3.11

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置 Nacos
确保已经正确配置 Nacos，并在 .env.dev 文件中提供连接信息，例如：

```ini
NACOS_SERVER_ADD=http://192.168.90.108:8848
NACOS_FILE_EXTENSION=yml
NACOS_NAMESPACE=5d540982-f0c0-4717-874a-8fee7d44440a
NACOS_GROUP=DEV_GROUP
NACOS_USERNAME=nacos
NACOS_PASSWORD=zwjy@2021
NACOS_APP_PORT=8000
NACOS_APP_NAME=zw-ai-chat
```

## 运行应用程序
使用以下命令运行应用程序：
```shell
python main.py --env dev
```
可用的环境包括 `[dev|test|pre|prod]`。通过修改 core/nacos.py 中的 EnvEnum 枚举来添加或更改环境。

## 查看帮助信息
```shell
python main.py --help

```
