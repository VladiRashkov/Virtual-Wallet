from fastapi import APIRouter, Depends
from services import transactions_services
from common.authorization import get_current_user

# 1. Transaction history after a regular user has logged in
# ->admin cannot check the transaction history!
# 2. Make transaction
# 3. Each transaction has to be put through a confirmation step -> accept or decline
# 4. Receiver has to accept ot decline transaction
# 5. Add money to wallet

# 6. Filter by date, sender, recipient, and direction (in/out)
# 7. Sort by date or amount
# 8. Withdraw

transaction_router = APIRouter(prefix='/transactions')


@transaction_router.get('/')  # will require token of the user
def get_transactions(sort: str | None = None, sender_id: int = Depends(get_current_user)):
    transactions = transactions_services.all_user_transactions(sender_id, sort)
    return transactions


@transaction_router.post('/create_transaction')
def create_transaction(receiver_id: int, amount: float, sender_id: int = Depends(get_current_user)):
    result = transactions_services.transfer_money(sender_id, receiver_id, amount)
    return {'message': result}
