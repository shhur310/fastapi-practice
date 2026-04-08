from fastapi import FastAPI
from user.router import router

app = FastAPI()
app.include_router(router)