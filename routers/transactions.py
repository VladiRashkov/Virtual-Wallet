from fastapi import APIRouter
from services import transactions_services
#1. Transaction history after a regular user has logged in
#->admin cannot check the transaction history!
#2. Make transaction
#3. Each transaction has to be put through a confirmation step -> accept or decline
#4. Receiver has to accept ot decline transaction
#5. Add money to wallet

#6. Filter by date, sender, recipient, and direction (in/out)
#7. Sort by date or amount
#8. Withdraw

transaction_router = APIRouter(prefix='/transactions')

@transaction_router.get('/{sender_id}') # will require token of the user
def get_transactions(sender_id: int, sort: str | None = None):
    transactions = transactions_services.all_user_transations(sender_id)
    return transactions
        
        
        
@transaction_router.put('/create_transaction')
def create_transaction(sender_id:int, receiver_id:int, amount:float):
    result = transactions_services.transfer_money(sender_id, receiver_id, amount)
    return {'message':result}