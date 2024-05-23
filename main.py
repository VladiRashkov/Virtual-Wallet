
from fastapi import FastAPI
from routers import cards
from routers.transactions import transaction_router
from routers.recurring_transactoins import recurring_transaction_router
from routers.users import users_router
import uvicorn
from data import scheduler

app = FastAPI()
app.include_router(cards.router)
app.include_router(users_router)
app.include_router(transaction_router)
app.include_router(recurring_transaction_router)

if __name__ == "__main__":
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)


