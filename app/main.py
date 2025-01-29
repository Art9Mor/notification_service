from fastapi import FastAPI

from app.api import notify

app = FastAPI()

app.include_router(notify.router)
