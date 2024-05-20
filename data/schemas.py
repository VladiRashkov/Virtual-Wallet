from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    phone_number: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    phone_number: str
    created_at: datetime


class UserLogin(BaseModel):
    email: str
    password: str


class UpdateAmount(BaseModel):
    amount: float


class AmountOut(BaseModel):
    message: str
    old_balance: float
    new_balance: float


class AccountBalanceOut(BaseModel):
    balance: float


class DepositAmount(BaseModel):
    deposit_amount: float


class WithdrawMoney(BaseModel):
    withdraw_sum: float


class CreateTransaction(BaseModel):
    receiver_id: int
    amount: float
    category: str
