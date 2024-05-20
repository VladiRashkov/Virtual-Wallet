from fastapi import APIRouter, Depends, Query
from services import transactions_services
from common.authorization import get_current_user
from typing import Optional, List, Dict, Any

# 1. Transaction history after a regular user has logged in  -- sending part, reciever part in progress
# ->admin cannot check the transaction history!
# 2. Make transaction -- done
# 3. Each transaction has to be put through a confirmation step -> accept or decline -- consult with team
# 4. Receiver has to accept ot decline transaction
# 5. Add money to wallet

# 6. Filter by date, sender, recipient, and direction (in/out)
# 7. Sort by date or amount -- DONE
# 8. Withdraw -- DONE

transaction_router = APIRouter(prefix='/transactions')


@transaction_router.get('/')  # will require token of the user
def get_transactions(sort_by: Optional[str] = Query(None, pattern='^(created_at|amount)$'),
                     order: Optional[str] = Query(None, pattern='^(asc|desc)$'),
                     transaction_type:str = Query('all', pattern='^(sent|received|all)'),
                     sender_id: int = Depends(get_current_user)):
    transactions = transactions_services.all_user_transactions(sender_id, transaction_type, sort_by, order)
    return transactions

# @transaction_router.get('/filter')
# def get_filter(date:str,
#                receiver_id:int,
#                transaction_type:str = Query('all', pattern='^(sent|received)',
#                sender_id: int = Depends(get_current_user)):
    
    


@transaction_router.post('/create_transaction')
def create_transaction(receiver_id: int, amount: float, category:str, sender_id: int = Depends(get_current_user)):
    result = transactions_services.transfer_money(sender_id, receiver_id, amount, category)
    return {'message': result[0]}

@transaction_router.put('/add')
def add_money(deposit:float, user: int=Depends(get_current_user)):
    result = transactions_services.deposit_money(user,deposit)
    return {'message':result}

@transaction_router.put('/withdraw')
def extract_money(money:float, user: int=Depends(get_current_user)):
    result = transactions_services.withdraw_money(user, money)
    return result
    