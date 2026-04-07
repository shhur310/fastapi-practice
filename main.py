from fastapi import FastAPI, Path, Query
from pydantic import BaseModel
from request import UserCreateRequest
from response import UserResponse

# 127.0.0.1:8000 서버 실행
app = FastAPI()

# @ -> python 데코레이터: 파이썬 함수에 추가적인 기능을 부여하는 문법
# GET / 요청이 들어오면, root_handler라는 함수를 실행하라
@app.get("/")
def root_handler():
    return {"ping": "pong"}

# GET /hello 요청이 들어오면, hello_handler() 실행 
@app.get("/hello")
def hello_handler():
    return {"message": "Hello from. FastAPI!"}

# 임시 데이터베이스
users = [
        {"id": 1, "name": "alex", "job": "student"},
        {"id": 2, "name": "bob", "job": "sw engineer"},
        {"id": 3, "name": "chris", "job": "barista"},
    ]

# 전체 사용자 목록 조회 API
# GET /user
@app.get("/user")
def get_users_handler():
    return users

# 사용자 정보 검색 API
# GET /users/search?name=alex
# GET /users/search?job=student
@app.get("/user/search")
def search_user_handler(
    name: str | None = Query(None), 
    job: str | None = Query(None),
): 
    if name is None and job is None:
        return {"msg": "조회에 사용할 QueryParam이 필요합니다."}
    return {"name": name, "job": job}

    for user in users:
        if name and job:
            if user["name"] == name and user["job"] == job:
                return user
            else:
                return None
        else:
            if user["name"] == name:
                return user
            if user["job"] == job:
                return user

# 단일 사용자 데이터 조회 API
# GET /users/{user_id} -> {user_id}번 사용자 데이터 조회
@app.get("/user/{user_id}")
def get_users_handler(
    user_id: int = Path(..., ge=1),
):
    for user in users:
        if user["id"] == user_id:
            return user

# 회원 추가 API
# POST /users
@app.post("/users", response_model=UserResponse)
def create_user_handler(
    body: UserCreateRequest
):
    # 1) 사용자 데이터를 넘겨 받는다 + 데이터 유효성 검사
    # 2) 사용자 데이터를 저장한다
    new_user = {
        "id": len(users) + 1,
        "name": body.name,
        "job":  body.job,
    }
    users.append(new_user)

    # 3) 응답을 반환하다
    return new_user

