from typing import Annotated

import typer
from fastapi import FastAPI

# from typing_extensions import Literal
from api import router
from core.config import settings
from core.exceptions import exception_handler
from core.lifespan_handler import lifespan
from core.log import setup_logging
from core.middleware import add_middleware
from core.nacos import EnvEnum, environment, get_nacos_settings

setup_logging()
app = FastAPI(lifespan=lifespan)
add_middleware(app)
exception_handler(app)
app.include_router(router=router)


def run(
        env: Annotated[EnvEnum, typer.Option(help='需要加载的环境')] = EnvEnum.dev.value,
        debug: Annotated[bool, typer.Option(help='是否需要开启debug模式，开启后会自动重载')] = True

):
    environment.write_enum_value(env.value)
    import uvicorn

    uvicorn.run(
            "main:app",
            reload=debug,
            reload_excludes=['DirectoryV3.xml'],
            app_dir=settings.base_dir_str,
            host=str(get_nacos_settings(environment).app_ip),
            port=get_nacos_settings(environment).app_port
    )
    environment.close()


if __name__ == '__main__':
    typer.run(run)
