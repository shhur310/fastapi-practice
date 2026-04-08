from fastapi import APIRouter, Path, Query, status, HTTPException
from database.connection import SessionFactory
from user.models import User
from user.request import UserCreateRequest, UserUpdateRequest
from user.response import UserResponse


# 핸들러 함수들을 관리하는 객체
router = APIRouter(tags=["User"])

# 임시 데이터베이스
users = [
        {"id": 1, "name": "alex", "job": "student"},
        {"id": 2, "name": "bob", "job": "sw engineer"},
        {"id": 3, "name": "chris", "job": "barista"},
    ]

# 전체 사용자 목록 조회 API
# GET /user
@router.get("/user", status_code=status.HTTP_200_OK)
def get_users_handler():
    return users

# 사용자 정보 검색 API
# GET /users/search?name=alex
# GET /users/search?job=student
@router.get("/user/search")
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
@router.get("/user/{user_id}")
def get_users_handler(
    user_id: int = Path(..., ge=1),
):
    for user in users:
        if user["id"] == user_id:
            return user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found",
        )

# 회원 추가 API
# POST /users
@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user_handler(
    body: UserCreateRequest
):
    # context manager를 벗어나는 순간 자동으로 close() 호출
    with SessionFactory() as session:
        new_user = User(name=body.name, job=body.job)
        session.add(new_user)
        session.commit() # 변경사항 저장
        session.refresh(new_user) # id, created_at 읽어봄
        return new_user

# 회원 정보 수정 API

# PUT: 전체 교체(replace)
# PATCH: 일부 수정
# PATCH /users/{user_id}
@router.patch("/users/{user_id}", response_model=UserResponse,)
def update_user_handler(
    # 1) 입력값 정의
    user_id: int,
    body:UserUpdateRequest,
):
    # 2) 처리
    for user in users:
         # user_id로 사용자를 조회
        if user["id"] == user_id:
            # 데이터 수정
            user["job"] = body.job

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User Not Found"
    )

    # 3) 반환
    return

# 회원 삭제 API
# DELETE /users/{user_id}
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT,)
def delete_user_handler(user_id: int):
    for user in users:
        if user["id"] == user_id:
            users.remove(user)
            return
        
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User Not Found"
    )