# routers/recurring_transactions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from services.recurring_transactions_services import create_recurring_transaction, process_recurring_transaction, update_recurring_transaction, delete_recurring_transaction, get_all_recurring_transactions
from data.schemas import CreateRecurringTransaction, UpdateRecurringTransaction
from common.authorization import get_current_user
from data.connection import query


recurring_transaction_router = APIRouter(prefix='/recurring_transactions')

@recurring_transaction_router.get('/',tags=['Recurring Transactions'])
def get_logged_user_transactions(sender_id: int = Depends(get_current_user)):
    '''
    Retrieves all recurring transactions for the logged-in user.

    Parameters:
    - sender_id (int): ID of the logged-in user.

    Returns:
    - dict: A dictionary containing the retrieved recurring transactions.
    '''
    result = get_all_recurring_transactions(sender_id)
    return result.data
      
@recurring_transaction_router.post('/recurring_transaction', tags=['Recurring Transactions'])
def create_recurring_transaction_endpoint(transaction: CreateRecurringTransaction, sender_id: int = Depends(get_current_user)):
    '''
    Creates a new recurring transaction initiated by the logged-in user.

    Parameters:
    - transaction (CreateRecurringTransaction): Details of the recurring transaction to create.
    - sender_id (int): ID of the logged-in user.

    Returns:
    - dict: A dictionary containing a message indicating the result of the creation.
    '''
    result = create_recurring_transaction(sender_id, transaction)
    return {'message': result}


@recurring_transaction_router.post('/process/{transaction_id}', tags=['Recurring Transactions'])
def process_recurring_transaction_endpoint(transaction_id: int, user_id: int = Depends(get_current_user)):
    '''
    Processes a recurring transaction by the logged-in user.

    Parameters:
    - transaction_id (int): ID of the recurring transaction to process.
    - user_id (int): ID of the logged-in user.

    Returns:
    - dict: A dictionary containing a message indicating the result of the processing.
    '''
    transaction_data = query.table('recurring_transactions').select('*').eq('id', transaction_id).execute().data
    if not transaction_data:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction = transaction_data[0]
    if transaction['sender_id'] != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to process this transaction")

   
    process_recurring_transaction(transaction_id)
    return {'message': f"Recurring transaction {transaction_id} processed successfully"}

@recurring_transaction_router.put('/{recurring_transaction_id}', tags=['Recurring Transactions'])
def update_recurring_transaction_endpoint(recurring_transaction_id: int, update_transaction: UpdateRecurringTransaction, user_id: int = Depends(get_current_user)):
    '''
    Updates a recurring transaction by the logged-in user.

    Parameters:
    - recurring_transaction_id (int): ID of the recurring transaction to update.
    - update_transaction (UpdateRecurringTransaction): Details of the update to apply to the transaction.
    - user_id (int): ID of the logged-in user.

    Returns:
    - dict: A dictionary containing a message indicating the result of the update.
    '''
    result = update_recurring_transaction(recurring_transaction_id, user_id, update_transaction)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found or you are not authorized to update this transaction")
    return {'message': f'Recurring transation {recurring_transaction_id} updated successfully'}


@recurring_transaction_router.delete('/{recurring_transaction_id}', tags=['Recurring Transactions'])
def delete_recurring_transaction_endpoint(recurring_transaction_id: int, user_id: int = Depends(get_current_user)):
    '''
    Deletes a recurring transaction by the logged-in user.

    Parameters:
    - recurring_transaction_id (int): ID of the recurring transaction to delete.
    - user_id (int): ID of the logged-in user.

    Returns:
    - dict: A dictionary containing a message indicating the result of the deletion.
    '''
    delete_recurring_transaction(recurring_transaction_id, user_id)
    
    return {'message': f"Recurring transaction {recurring_transaction_id} deleted successfully"}
