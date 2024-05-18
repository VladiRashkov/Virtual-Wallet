from pydantic import BaseModel
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
        )
