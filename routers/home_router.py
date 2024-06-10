from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.requests import Request
from common.authorization import get_current_user
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

home_router = APIRouter(prefix='')

templates = Jinja2Templates(directory="templates")


@home_router.get("/")
def read_root():
    return JSONResponse(content={"message": "Welcome to the FastAPI application!"})


@home_router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user_id = request.state.user_id
    user = None
    if user_id:
        user = get_current_user(user_id)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})
