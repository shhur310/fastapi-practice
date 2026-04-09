from fastapi import APIRouter, Path, Query, status, HTTPException, Depends
from sqlalchemy import select, delete
from database.connection import SessionFactory, get_session
from user.models import User
from user.request import UserCreateRequest, UserUpdateRequest
from user.response import UserResponse


# 핸들러 함수들을 관리하는 객체
router = APIRouter(tags=["User"])

# 전체 사용자 목록 조회 API
# GET /user
@router.get(
    "/user",
    summary="전체 사용자 목록 조회 API", 
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponse],
)
def get_users_handler(
    # Depends: FastAPI에서 의존성(get_session)을 자동으로 실행/주입/정리
    session = Depends(get_session),
):
    # statement = 구문(명령문)
    stmt = select(User) # SELECT * FROM user;
    result = session.execute(stmt)
    users = result.scalars().all() # [user1, user2, user3, ...]
    return users

# 사용자 정보 검색 API
# GET /users/search?name=alex
# GET /users/search?job=student
@router.get(
    "/user/search",
    summary="사용자 정보 검색 API",
    response_model=list[UserResponse],
)
def search_user_handler(
    name: str | None = Query(None), 
    job: str | None = Query(None),
    session = Depends(get_session),
): 
    if not name and not job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="검색 조건이 없습니다."
        )
    stmt = select(User)
    if name:
        stmt = stmt.where(User.name == name)
    if job:
        stmt = stmt.where(User.job == job)

    result = session.execute(stmt)
    users = result.scalars().all()
    return users

# 단일 사용자 데이터 조회 API
# GET /users/{user_id} -> {user_id}번 사용자 데이터 조회
@router.get(
    "/user/{user_id}",
    summary="단일 사용자 데이터 조회 API",
    response_model=UserResponse,
)
def get_users_handler(
    user_id: int = Path(..., ge=1),
):
    with SessionFactory() as session:
        # 예? SELECT * FROM user WHERE id = 42;
        stmt = select(User).where(User.id == user_id)
        result = session.execute(stmt)
        user = result.scalar() # 존재하면 user 객체, 존재하지 않으면 None
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found",
        )
    return user

# 회원 추가 API
# POST /users
@router.post(
    "/users",
    summary="회원 추가 API",
    status_code=status.HTTP_201_CREATED, 
    response_model=UserResponse,
)
def create_user_handler(body: UserCreateRequest):
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
@router.patch(
    "/users/{user_id}",
    summary="회원 정보 수정 API",
    response_model=UserResponse,
)
def update_user_handler(
    user_id: int,
    body:UserUpdateRequest,
):
    with SessionFactory() as session:
        stmt = select(User).where(User.id == user_id)
        result = session.execute(stmt)
        user = result.scalar()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found",
            )
        
        user.job = body.job
        session.commit() # user tkdxo(job 변경)를 DB 반영
        return user    

# 회원 삭제 API
# DELETE /users/{user_id}
@router.delete(
    "/users/{user_id}",
    summary="회원 삭제 API",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_handler(user_id: int):
    # 1) 조회하고, 삭제
    # with SessionFactory() as session:
    #     stmt = select(User).where(User_id == user_id)
    #     result = session.execute(stmt)
    #     user = result.scalar()

    #     if not user:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="User Not Found",
    #         )
    
    #     session.delete(user) # 객체를 삭제
    #     # session.expunge(user) -> 세션의 추적 대상에서 제거
    #     session.commit()

    # 2) 곧바로 삭제
    with SessionFactory() as session:
        stmt = select(User).where(User.id == user_id)
        session.execute(stmt)
        session.commit()