from pydantic import BaseModel, EmailStr
from datetime import datetime


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
