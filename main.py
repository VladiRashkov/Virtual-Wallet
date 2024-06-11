from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status

from common.authorization import verify_access_token
from routers.cards import cards_router
from routers.transactions import transaction_router
from routers.recurring_transactoins import recurring_transaction_router
from routers.users import users_router
from routers.contacts import router_contacts
from routers.home_router import home_router

templates = Jinja2Templates(directory="templates")

app = FastAPI(swagger_ui_parameters={"operationsSorter": "alpha"})

app.include_router(cards_router)
app.include_router(router_contacts)
app.include_router(users_router)
app.include_router(transaction_router)
app.include_router(recurring_transaction_router)
app.include_router(home_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_token_to_request(request: Request, call_next):
    token = request.cookies.get("access_token")
    if token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            user_id = verify_access_token(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token),
                                          credentials_exception)
            request.state.user_id = user_id
        except HTTPException:
            request.state.user_id = None
    else:
        request.state.user_id = None

    response = await call_next(request)
    return response

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
