from fastapi import FastAPI
from routers.cards import router as cards_router
from routers.transactions import transaction_router
from routers.users import users_router
import uvicorn

app = FastAPI()
app.include_router(cards_router)
app.include_router(users_router)
app.include_router(transaction_router)

if __name__ == "__main__":
    uvicorn.run('main:app', host='127.0.0.1', port=8000)
