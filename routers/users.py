from fastapi import APIRouter, status, Form
from common.authorization import create_token, get_current_user, logout_user
from fastapi.requests import Request
from fastapi import HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from services import user_services
from data.schemas import UserCreate, UserLogin, UpdateProfile, ConfirmUserRegistration, BlockOrUnblock
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from data.helpers import is_admin
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

templates = Jinja2Templates(directory="templates")

users_router = APIRouter(prefix='/users', tags=['Users'])


@users_router.get('/balance')
def get_account_balance(logged_user_id: int = Depends(get_current_user)):
    balance = user_services.get_user_balance(logged_user_id)
    return balance


# @users_router.post('/register', status_code=status.HTTP_201_CREATED)
# def register(user_create: UserCreate):
#     new_user = user_services.create(user_create.username, user_create.password, user_create.email,
#                                     user_create.phone_number)
#     return new_user

@users_router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@users_router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...),
                   phone_number: str = Form(...)):
    try:
        new_user = user_services.create(username, password, email, phone_number)
        return templates.TemplateResponse("register.html",
                                          {"request": request, "success": "Registration successful! Please log in."})
    except HTTPException as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": e.detail})


@users_router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@users_router.post('/login', status_code=status.HTTP_200_OK)
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        user = user_services.try_login(email, password)
        access_token = create_token(data={"user_id": user.id})
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    except HTTPException as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": e.detail})


@users_router.get('/profile/update', response_class=HTMLResponse)
async def update_profile_form(request: Request):
    user_id = request.state.user_id
    if user_id is None:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Not authenticated"})
    user = user_services.get_logged_user(user_id)
    return templates.TemplateResponse("update_profile.html", {"request": request, "user": user})


@users_router.post('/profile/update', status_code=status.HTTP_200_OK)
async def update_profile(request: Request, email: str = Form(...), password: str = Form(...),
                         phone_number: str = Form(...)):
    user_id = request.state.user_id
    if user_id is None:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Not authenticated"})
    try:
        result = user_services.update_profile(password, email, phone_number, user_id)
        return templates.TemplateResponse("update_profile.html",
                                          {"request": request, "success": "Profile updated successfully!",
                                           "user": {"email": email, "phone_number": phone_number}})
    except HTTPException as e:
        user = user_services.get_logged_user(user_id)
        return templates.TemplateResponse("update_profile.html", {"request": request, "error": e.detail, "user": user})


@users_router.get('/profile')
def get_logged_user(request: Request):
    user_id = request.state.user_id
    if user_id is None:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Not authenticated"})
    result = user_services.get_logged_user(user_id)
    return templates.TemplateResponse("profile.html", {"request": request, "user": result})


# @users_router.get('/profile')
# def get_logged_user(logged_user_id: int = Depends(get_current_user)):
#     result = user_services.get_logged_user(logged_user_id)
#     return result

# @users_router.post('/login', status_code=status.HTTP_200_OK)
# def login(user_login: UserLogin):
#     user = user_services.try_login(user_login.email, user_login.password)
#
#     access_token = create_token(data={"user_id": user.id})
#
#     return {"access_token": access_token, "token_type": "bearer"}


# @users_router.get('/profile/update', response_class=HTMLResponse)
# async def update_profile_form(request: Request, logged_user_id: int = Depends(get_current_user)):
#     user = user_services.get_logged_user(logged_user_id)
#     return templates.TemplateResponse("update_profile.html", {"request": request, "user": user})


# @users_router.post('/profile/update', status_code=status.HTTP_200_OK)
# async def update_profile(request: Request, email: str = Form(...), password: str = Form(...),
#                          phone_number: str = Form(...), logged_user: int = Depends(get_current_user)):
#     try:
#         result = user_services.update_profile(password, email, phone_number, logged_user)
#         return templates.TemplateResponse("update_profile.html",
#                                           {"request": request, "success": "Profile updated successfully!",
#                                            "user": {"email": email, "phone_number": phone_number}})
#     except HTTPException as e:
#         user = user_services.get_logged_user(logged_user)
#         return templates.TemplateResponse("update_profile.html", {"request": request, "error": e.detail, "user": user})


# @users_router.put('/profile/update')
# def update_profile(update_profile_params: UpdateProfile, logged_user: int = Depends(get_current_user)):
#     result = user_services.update_profile(update_profile_params.password, update_profile_params.email,
#                                           update_profile_params.phone_number, logged_user)
#     return result


# @users_router.get('/', response_class=HTMLResponse)
# async def get_all_users(request: Request, username: str = None, email: str = None, phone_number: str = None,
#                         registered: str = None, page: int = 1):
#     logged_user_id = request.state.user_id
#     if not logged_user_id or not is_admin(logged_user_id):
#         return templates.TemplateResponse("error.html",
#                                           {"request": request, "error": "You must be an admin to see all users!"})
#     try:
#         registered_bool = None
#         if registered:
#             registered_bool = registered.lower() == 'true'
#         users = user_services.get_all_users(logged_user_id, username=username, email=email, phone_number=phone_number,
#                                             registered=registered_bool, page=page)
#         return templates.TemplateResponse("all_users.html", {"request": request, "users": users, "page": page})
#     except HTTPException as e:
#         return templates.TemplateResponse("error.html", {"request": request, "error": e.detail})

@users_router.get('/', response_class=HTMLResponse)
async def get_all_users(request: Request, page: int = 1, username: str = None, email: str = None,
                        phone_number: str = None, registered: str = None):
    logged_user_id = request.state.user_id

    if not logged_user_id or not is_admin(logged_user_id):
        return templates.TemplateResponse('error.html',
                                          {"request": request, "error": "Only admins can get all users information!"})

    registered_bool = None
    if registered == "true":
        registered_bool = True
    elif registered == "false":
        registered_bool = False

    result = user_services.get_all_users(logged_user_id, username, email, phone_number, registered_bool, page)
    return templates.TemplateResponse("all_users.html",
                                      {"request": request, "users": result, "page": page, "username": username,
                                       "email": email, "phone_number": phone_number, "registered": registered})


# @users_router.get('/')
# def get_all_users(page: int = 1, username: str = None, email: str = None, phone_number: str = None,
#                   registered: bool = None,
#                   logged_user_id: int = (Depends(get_current_user))):
#     result = user_services.get_all_users(logged_user_id, username, email, phone_number, registered, page)
#     return result


@users_router.get('/confirm', response_class=HTMLResponse)
async def confirm_user_registration_form(request: Request):
    user_id = request.state.user_id
    if user_id is None or not is_admin(user_id):
        return templates.TemplateResponse("error.html", {"request": request,
                                                         "error": "You must be an admin to confirm registrations"})
    return templates.TemplateResponse("confirm_user_registration.html", {"request": request})


@users_router.post('/confirm', status_code=status.HTTP_200_OK)
async def confirm_user_registration(request: Request, email: str = Form(...)):
    user_id = request.state.user_id
    if user_id is None or not is_admin(user_id):
        return templates.TemplateResponse("error.html", {"request": request,
                                                         "error": "You must be an admin to confirm registrations"})
    try:
        confirmation = ConfirmUserRegistration(confirm=True)
        result = user_services.confirm_user_registration(confirmation.confirm, email, user_id)
        return templates.TemplateResponse("confirm_user_registration.html",
                                          {"request": request, "success": "User registration confirmed successfully!"})
    except HTTPException as e:
        return templates.TemplateResponse("confirm_user_registration.html", {"request": request, "error": e.detail})


# @users_router.put('/confirm/{user_email}')
# def confirm_user_registration(confirmation: ConfirmUserRegistration, user_email: str,
#                               logged_user_id: int = (Depends(get_current_user))):
#     result = user_services.confirm_user_registration(confirmation.confirm, user_email, logged_user_id)
#     return result


@users_router.get('/block')
def block_user_form(request: Request):
    logged_user_id = request.state.user_id
    if not logged_user_id or not is_admin(logged_user_id):
        return templates.TemplateResponse('error.html',
                                          {'request': request, 'error': 'Only admins can block or unblock users!'})
    return templates.TemplateResponse('block_user.html', {'request': request})


@users_router.post('/block')
async def block_user(request: Request, user_id: int = Form(...), block_status: str = Form(...)):
    logged_user_id = request.state.user_id
    if not logged_user_id or not is_admin(logged_user_id):
        return templates.TemplateResponse('error.html',
                                          {'request': request, 'error': 'Only admins can block or unblock users!'})
    block_status_bool = block_status.lower() == 'true'
    try:
        result = user_services.block_user(block_status_bool, user_id, logged_user_id)
        return templates.TemplateResponse("block_user.html", {"request": request, "success": result})
    except Exception as e:
        return templates.TemplateResponse("block_user.html", {"request": request, "error": str(e)})


# @users_router.put('/block/{user_id}')
# def block_user(block_status: BlockOrUnblock, user_id: int, logged_user_id: int = Depends(get_current_user)):
#     result = user_services.block_user(block_status.is_blocked, user_id, logged_user_id)
#     return result


@users_router.get('/logout', response_class=HTMLResponse)
def show_logout_form(request: Request):
    return templates.TemplateResponse('logout.html', {'request': request, 'user_id': request.state.user_id})


@users_router.get('/logout', response_class=HTMLResponse)
def show_logout_form(request: Request):
    return templates.TemplateResponse('logout.html', {'request': request, 'user_id': request.state.user_id})


@users_router.post('/logout', status_code=status.HTTP_200_OK)
def logout_current_user(request: Request):
    logged_user_id = request.state.user_id
    if not logged_user_id:
        return templates.TemplateResponse('error.html',
                                          {'request': request, 'error': 'Only logged in users can logout!'})
    logout = logout_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=request.cookies.get('access_token')))
    response = templates.TemplateResponse('logout.html', {'request': request})
    response.delete_cookie('access_token')
    return response

# @users_router.post('/logout', status_code=status.HTTP_200_OK)
# def logout(logged_user: int = Depends(logout_user)):
#     return {"msg": "Successfully logged out"}
