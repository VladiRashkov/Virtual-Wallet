from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from data.helpers import is_admin

home_router = APIRouter()

templates = Jinja2Templates(directory="templates")


@home_router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@home_router.get('/menu', response_class=HTMLResponse)
async def read_menu(request: Request):
    logged_user_id = request.state.user_id

    if not logged_user_id:
        return templates.TemplateResponse('error.html',
                                          {'request': request, 'error': 'Only registered users can see the menu!'})
    if not is_admin(logged_user_id):
        return templates.TemplateResponse('users_menu.html', {'request': request})

    return templates.TemplateResponse('admins_menu.html', {'request': request})
