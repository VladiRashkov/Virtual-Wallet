from pydantic import BaseModel, EmailStr
from datetime import datetime


class Transaction(BaseModel):
    id: int
    created_at: datetime
    amount: float 
    status: str
    category: str

    @classmethod
    def from_query_result(cls, id, created_at, amount, status, category):
        return cls(
            id=id,
            created_at=created_at,
            amount=amount,
            status=status,
            category=category


class User(BaseModel):
    id: int
    username: str
    password: str
    email: str
    phone_number: str
    created_at: datetime

    @classmethod
    def from_query_result(cls, id: int, username: str, password: str, email: str, phone_number: str,
                          created_at: datetime):
        return cls(
            id=id,
            username=username,
            password=password,
            email=email,
            phone_number=phone_number,
            created_at=created_at

        )
