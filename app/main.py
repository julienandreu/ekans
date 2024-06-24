from fastapi import FastAPI

from .core.lifespan import lifespan
from .core.monitoring import init
from .modules.users.router import router as usersRouter

init()

app = FastAPI(lifespan=lifespan)

app.include_router(usersRouter)
