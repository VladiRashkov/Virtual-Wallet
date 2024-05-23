from fastapi import APIRouter, status
from common.authorization import create_token, get_current_user, logout_user
from services import user_services
from data.schemas import UserCreate, UserLogin, UpdateProfile, ConfirmUserRegistration, BlockOrUnblock
from fastapi import Depends

users_router = APIRouter(prefix='/users')


@users_router.get('/balance')
def get_account_balance(logged_user_id: int = Depends(get_current_user)):
    balance = user_services.get_user_balance(logged_user_id)
    return balance


@users_router.post('/register', status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate):
    new_user = user_services.create(user_create.username, user_create.password, user_create.email,
                                    user_create.phone_number)
    return new_user


@users_router.post('/login', status_code=status.HTTP_200_OK)
def login(user_login: UserLogin):
    user = user_services.try_login(user_login.email, user_login.password)

    access_token = create_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


@users_router.put('/profile/update')
def update_profile(update_profile_params: UpdateProfile, logged_user: int = Depends(get_current_user)):
    result = user_services.update_profile(update_profile_params.password, update_profile_params.email,
                                          update_profile_params.phone_number, logged_user)
    return result


@users_router.get('/profile')
def get_logged_user(logged_user_id: int = Depends(get_current_user)):
    result = user_services.get_logged_user(logged_user_id)
    return result


@users_router.get('/')
def get_all_users(page: int = 1, username: str = None, email: str = None, phone_number: str = None,
                  registered: bool = None,
                  logged_user_id: int = (Depends(get_current_user))):
    result = user_services.get_all_users(logged_user_id, username, email, phone_number, registered, page)
    return result


@users_router.put('/confirm/{user_email}')
def confirm_user_registration(confirmation: ConfirmUserRegistration, user_email: str,
                              logged_user_id: int = (Depends(get_current_user))):
    result = user_services.confirm_user_registration(confirmation.confirm, user_email, logged_user_id)
    return result


@users_router.put('/block/{user_id}')
def block_user(block_status: BlockOrUnblock, user_id: int, logged_user_id: int = Depends(get_current_user)):
    result = user_services.block_user(block_status.is_blocked, user_id, logged_user_id)
    return result


@users_router.post('/logout', status_code=status.HTTP_200_OK)
def logout(logged_user: int = Depends(logout_user)):
    return {"msg": "Successfully logged out"}
