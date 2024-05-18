from fastapi import APIRouter, HTTPException, status
import services.user_services
from common.authorization import create_token
from security.password_hashing import get_password_hash, verify_password
from services import user_services
from data.schemas import UserCreate, UserLogin

users_router = APIRouter(prefix='/users')


@users_router.post('/register', status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate):
    result = user_services.create(user_create.username, user_create.password, user_create.email,
                                  user_create.phone_number)
    return result


@users_router.post('/login', status_code=status.HTTP_200_OK)
def login(user_login: UserLogin):
    user = user_services.try_login(user_login.email, user_login.password)

    access_token = create_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
