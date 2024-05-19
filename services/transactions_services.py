from data.connection import query
from fastapi import HTTPException, status
from typing import Optional


def all_user_transactions(sender_id: int, sort_by: Optional[str] = None, order:Optional[str] = None):
    """This function retrieves all transactions made by a user with the specified sender ID. If no transactions are found,
    it raises an HTTP exception with a 404 Not Found status code."""

    data = query.table('transactions').select(
        '*').eq('sender_id', sender_id).execute()
    transactions = data.data

    if not transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with id {sender_id} has no transactions!')
        
    if sort_by:
        reverse = (order=="desc")
        transactions.sort(key=lambda x: x[sort_by],reverse=reverse)
    return transactions


def transfer_money(sender_id: int, receiver_id: int, amount: float, category: str):  # TODO add category
    sender = query.table('users').select(
        'amount').eq('id', sender_id).execute()
    receiver = query.table('users').select(
        'amount').eq('id', receiver_id).execute()

    sender_data = sender.data
    receiver_data = receiver.data

    if not sender_data or not receiver_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='The user was not found')
    sender_balance = sender_data[0]['amount']
    receiver_balance = receiver_data[0]['amount']

    
    
    if sender_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Insufficient balance')
        
    confirm = input(f"Are you sure you want to transfer {amount} to user with ID {receiver_id}? (yes/no): ")
    if confirm.lower() != "yes":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Transfer canceled by user')

    new_sender_balance = sender_balance - amount
    new_receiver_balance = receiver_balance + amount

    query.table('users').update({'amount': new_sender_balance}).eq(
        'id', sender_id).execute()
    query.table('users').update({'amount': new_receiver_balance}).eq(
        'id', receiver_id).execute()

    transaction_data = {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'amount': amount,
        'status':"confirmed",
        'category': category
    }

    query.table('transactions').insert(transaction_data).execute()

    return 'Successful'


def deposit_money(id:int, sum:float):
    user = query.table('users').select('amount').eq('id',id).execute()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='The user was not found')
    user_data = user.data[0]
    user_amount = user_data['amount']
    
    if sum<=0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The sum has to be a positive number')
    
    new_balance = user_amount+sum
    
    update_balance = query.table('users').update({'amount': new_balance}).eq('id', id).execute()
    
    return f'The new balance is {update_balance}.'

def withdraw_money(id:int, sum:float):
    user = query.table('users').select('amount').eq('id',id).execute()
    
    if not user.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='The user was not found')
    user_data = user.data[0]
    user_amount = user_data['amount']
    
    if sum<=0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The sum has to be a positive number')
    
    if user_amount<sum:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = 'Insufficient balance')
    
    new_balance = user_amount-sum
    
    update_result = query.table('users').update({'amount': new_balance}).eq('id', id).execute()
    
   
    
    return f'The new balance is {update_result}.'
    
    