# routers/recurring_transactions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from services.recurring_transactions_services import create_recurring_transaction, process_recurring_transaction, update_recurring_transaction, delete_recurring_transaction, get_all_recurring_transactions
from data.schemas import CreateRecurringTransaction, UpdateRecurringTransaction
from common.authorization import get_current_user
from data.connection import query
from typing import Optional


recurring_transaction_router = APIRouter(prefix='/recurring_transactions')

@recurring_transaction_router.get('/')
def get_logged_user_transactions(sender_id: int = Depends(get_current_user)):
    result = get_all_recurring_transactions(sender_id)
    return result.data
        # transactions = transactions_services.get_logged_user_transactions(sender_id, transaction_type, sort_by, order,
        #                                                               transaction_status)

@recurring_transaction_router.post('/create_recurring_transaction')
def create_recurring_transaction_endpoint(transaction: CreateRecurringTransaction, sender_id: int = Depends(get_current_user)):
    result = create_recurring_transaction(sender_id, transaction)
    return {'message': result}


@recurring_transaction_router.post('/process_recurring_transaction/{transaction_id}')
def process_recurring_transaction_endpoint(transaction_id: int, user_id: int = Depends(get_current_user)):
   
    transaction_data = query.table('recurring_transactions').select('*').eq('id', transaction_id).execute().data
    if not transaction_data:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction = transaction_data[0]
    if transaction['sender_id'] != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to process this transaction")

   
    process_recurring_transaction(transaction_id)
    return {'message': f"Recurring transaction {transaction_id} processed successfully"}

@recurring_transaction_router.put('/update_recurring_transaction/{recurring_transaction_id}')
def update_recurring_transaction_endpoint(recurring_transaction_id: int, update_transaction: UpdateRecurringTransaction, user_id: int = Depends(get_current_user)):
    result = update_recurring_transaction(recurring_transaction_id, user_id, update_transaction)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found or you are not authorized to update this transaction")
    return {'message': f'Recurring transation {recurring_transaction_id} updated successfully'}


@recurring_transaction_router.delete('/delete_recurring_transaction/{recurring_transaction_id}')
def delete_recurring_transaction_endpoint(recurring_transaction_id: int, user_id: int = Depends(get_current_user)):
    delete_recurring_transaction(recurring_transaction_id, user_id)
    
    return {'message': f"Recurring transaction {recurring_transaction_id} deleted successfully"}

# def d