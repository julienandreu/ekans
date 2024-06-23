from fastapi import FastAPI

from .core.monitoring import init
from .modules.items import router

init()

app = FastAPI()

app.include_router(router.router)
app.include_router(router.router)
