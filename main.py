import anyio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from user.router import router

# 쓰레드 풀 크기 조정
@asynccontextmanager
async def lifespan(_):
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 200
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)

def aws_sync():
    # AWS 서버랑 통신(예: 2초)
    return

from starlette.concurrency import run_in_threadpool

# 비동기 라이브러리를 지원하지 않는 경우
@app.get("/async")
async def async_handler(): 
    # 동기 함수를 비동기 방식으로 실행할 수 있게 해주는 유틸리티 함수
    await run_in_threadpool(aws_sync)
    return {"msg": "ok"}