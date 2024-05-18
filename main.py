from fastapi import FastAPI
from routers.transactions import transaction_router

app = FastAPI()


app.include_router(transaction_router)