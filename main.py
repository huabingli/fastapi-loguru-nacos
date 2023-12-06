from typing import Annotated

import typer
from fastapi import FastAPI

import core.nacos
# from typing_extensions import Literal
from api import router
from core import config
from core.exceptions import exception_handler
from core.lifespan_handler import lifespan
from core.log import setup_logging
from core.middleware import add_middleware
from core.nacos import EnvEnum, get_nacos_settings

setup_logging()
app = FastAPI(lifespan=lifespan)
add_middleware(app)
exception_handler(app)
app.include_router(router=router)


def run(
        env: Annotated[EnvEnum, typer.Option(help='需要加载的环境')] = EnvEnum.dev.value
):
    core.nacos.environment = env
    import uvicorn

    uvicorn.run(
            "main:app",
            reload=True,
            reload_excludes=['DirectoryV3.xml'],
            app_dir=config.settings.base_dir_str,
            host=str(get_nacos_settings(core.nacos.environment).app_ip),
            port=get_nacos_settings(core.nacos.environment).app_port
    )


if __name__ == '__main__':
    typer.run(run)
