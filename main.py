from fastapi import FastAPI
from routers.cards import cards_router
from routers.transactions import transaction_router
from routers.recurring_transactoins import recurring_transaction_router
from routers.users import users_router
from routers.contacts import router_contacts
import uvicorn


app = FastAPI(swagger_ui_parameters={"operationsSorter": "alpha"})
app.include_router(cards_router)
app.include_router(router_contacts)
app.include_router(users_router)
app.include_router(transaction_router)
app.include_router(recurring_transaction_router)

if __name__ == "__main__":
    uvicorn.run('main:app', host='127.0.0.1', port=8000)
