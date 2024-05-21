from data.connection import query
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any
from services.user_services import get_account_balance
from data.schemas import AmountOut
from datetime import date, datetime, time
from data.models import Transaction


# TODO make a confirmation step when creating a transaction! (maybe new endpoint)

def all_user_transactions(user_id: int, transaction_type: str = None, sort_by: Optional[str] = 'created_at',
                          order: Optional[str] = 'desc', transaction_status: str = 'all') -> List[
                                                                                                 object] | HTTPException:
    """Retrieves all transactions for a user by sender ID, including sent, received, and filtered by transaction status.
    Ensures no duplicate transactions by checking for deposits where sender_id and receiver_id are the same. Raises a 404
    HTTP exception if no transactions are found."""

    transactions = []

    # if all query params are default, this will be the output data
    sender_data = query.table('transactions').select('*').eq('sender_id', user_id).execute()
    receiver_data = query.table('transactions').select('*').eq('receiver_id', user_id).execute()
    transactions.extend(sender_data.data)
    transactions.extend(receiver_data.data)

    # get transactions if the logged user is sender of the transaction
    if transaction_type == 'sent':
        transactions.clear()
        sent_data = query.table('transactions').select('*').eq('sender_id', user_id).execute()
        transactions.extend(sent_data.data)

    # get transactions if the logged user is receiver of the transaction
    elif transaction_type == 'received':
        transactions.clear()
        received_data = query.table('transactions').select('*').eq('receiver_id', user_id).execute()
        transactions.extend(received_data.data)

    # get transaction status of the transactions which logged user SENT
    if transaction_status in ['confirmed', 'pending', 'declined']:
        transactions.clear()
        transactions_data = query.table('transactions').select('*').eq('status', transaction_status).eq(
            'sender_id',
            user_id).execute()
        transactions.extend(transactions_data.data)

    if not transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with id {user_id} has no {transaction_status} transactions!')

    # Here we check if transactions list has duplicate transactions.
    # If this check does not exist when retrieving transactions from the ATM,
    # duplicates will occur. Our logic is to retrieve transactions using sender_
    # id and receiver_id, but when there is a deposit from the ATM, both sender_id
    # and receiver_id will be the same.
    unique_transactions = []

    # set does not allow to have multiple values in it
    transaction_ids = set()
    for transaction in transactions:
        # here we check if transaction id exists in the set
        if transaction['id'] not in transaction_ids:
            # if this transaction id is not in the set, we can append the transaction to unique_transactions
            unique_transactions.append(transaction)
            # and add the id in the set
            transaction_ids.add(transaction['id'])

    transactions = unique_transactions

    if sort_by:
        reverse = (order == "desc")
        transactions.sort(key=lambda x: x[sort_by], reverse=reverse)

    return transactions


def transfer_money(sender_id: int, receiver_id: int, amount: float, category: str):
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

    # confirm = input(f"Are you sure you want to transfer {amount} to user with ID {receiver_id}? (yes/no): ")
    # if confirm.lower() != "yes":
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail='Transfer canceled by user')

    new_sender_balance = sender_balance - amount
    # new_receiver_balance = receiver_balance + amount

    query.table('users').update({'amount': new_sender_balance}).eq(
        'id', sender_id).execute()
    # query.table('users').update({'amount': new_receiver_balance}).eq(
    #     'id', receiver_id).execute()

    transaction_data = {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'amount': amount,
        'status': "pending",
        'category': category
    }

    insert_transaction = query.table('transactions').insert(transaction_data).execute()

    return 'Successful', insert_transaction


def deposit_money(deposit_amount: float, logged_user_id: int) -> AmountOut:
    """The deposit_money function is designed to update the account balance of a logged-in user
    by adding a specified deposit amount to their current balance."""

    user_balance_data = get_account_balance(logged_user_id)

    user_balance = user_balance_data.balance

    if deposit_amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='The deposit sum has to be a positive number!')

    new_balance = user_balance + deposit_amount

    # update the balance of the user
    update_balance_data = query.table('users').update({"amount": new_balance}).eq('id', logged_user_id).execute()

    # get the user amount, because we need it for make a record in transactions table
    update_balance_list = update_balance_data.data
    update_balance = update_balance_list[0]["amount"]

    # transaction category
    category = 'atm'

    # make a transaction record
    query.table('transactions').insert(
        {'amount': deposit_amount, "sender_id": logged_user_id, "receiver_id": logged_user_id, "status": "confirmed",
         "category": category, "is_accepted": True}).execute()

    return AmountOut(message="Balance updated!", old_balance=user_balance, new_balance=new_balance)


def withdraw_money(withdraw_sum: float, logged_user_id: int):
    # user = query.table('users').select('amount').eq('id', logged_user_id).execute()

    # if not user.data:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail='The user was not found')
    # user_data = user.data[0]
    # user_amount = user_data['amount']
    
    user_balance_data = get_account_balance(logged_user_id)

    user_balance = user_balance_data.balance

    if withdraw_sum <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The sum has to be a positive number')

    if user_balance < withdraw_sum:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Insufficient balance')

    new_balance = user_balance - withdraw_sum

    update_result_data = query.table('users').update({'amount': new_balance}).eq('id', logged_user_id).execute()
    update_result = update_result_data.data[0]['amount']
    category = 'atm'
    query.table('transactions').insert(
    {'amount': withdraw_sum, "sender_id": logged_user_id, "receiver_id": logged_user_id, "status": "confirmed",
        "category": category, "is_accepted": True}).execute()

    return AmountOut(message="Balance updated!", old_balance=user_balance, new_balance=new_balance)





def confirm_transaction(confirm_or_decline: str, transaction_id: int, logged_user_id: int):
    transaction_data = query.table('transactions').select('*').eq('id', transaction_id).eq('sender_id',
                                                                                           logged_user_id).eq('status',
                                                                                                              'pending').execute()

    if not transaction_data.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Transaction with id: {transaction_id} is not found! You can confirm only pending '
                                   f'transactions!')

    transaction = transaction_data.data[0]
    transaction_amount = transaction['amount']
    sender_id = transaction['sender_id']

    sender_account_balance = get_account_balance(sender_id).balance

    confirm_or_deny_list = ['confirm', 'deny']

    if confirm_or_decline not in confirm_or_deny_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='You can only "confirm" or "deny" the transaction!')

    if confirm_or_decline == 'decline':
        new_sender_account_balance = sender_account_balance + transaction_amount
        query.table('users').update({'amount': new_sender_account_balance}).eq('id', sender_id).execute()
        query.table('transactions').update({'status': 'declined'}).eq('id', transaction_id).execute()
        return f'Transaction with id: {transaction_id} was DECLINED!'
    elif confirm_or_decline == 'confirm':
        query.table('transactions').update({'status': 'confirmed'}).eq('id', transaction_id).execute()
        return f'Transaction with id: {transaction_id} was CONFIRMED!'

    
#NOT COMPLETED ADDITIONAL CORRECTION REQUIRE IMPLEMENTATION
def filter_transactions(
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    sender_id: Optional[int] = None,
    receiver_id: Optional[int] = None,
    transaction_type: str = "all"
) -> List[Transaction]:
    """Filters transactions based on the given criteria."""
    
    
    
    start_datetime = datetime.combine(start_date, time.min) if start_date else None
    end_datetime = datetime.combine(end_date, time.max) if end_date else None

    query_builder = query.table('transactions').select('*')
    
    if sender_id == None and receiver_id == None:
        if start_date:
            query_builder = query_builder.gte('created_at', start_datetime)
        if end_date:
            query_builder = query_builder.lte('created_at', end_datetime)
        if sender_id:
            query_builder = query_builder.eq('sender_id', user_id)
        if receiver_id:
            query_builder = query_builder.eq('receiver_id', user_id)
        if transaction_type == "sent":
            query_builder = query_builder.eq('sender_id', user_id)
        elif transaction_type == "received":
            query_builder = query_builder.eq('receiver_id', user_id)

        transactions_data = query_builder.execute().data
        
        if not transactions_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No transactions found matching the criteria')
        
        return transactions_data
    
    if user_id not in [sender_id, receiver_id]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized!')

    if start_date:
        query_builder = query_builder.gte('created_at', start_datetime)
    if end_date:
        query_builder = query_builder.lte('created_at', end_datetime)
    if sender_id:
        query_builder = query_builder.eq('sender_id', sender_id)
    if receiver_id:
        query_builder = query_builder.eq('receiver_id', receiver_id)
    if transaction_type == "sent":
        query_builder = query_builder.eq('sender_id', user_id)
    elif transaction_type == "received":
        query_builder = query_builder.eq('receiver_id', user_id)
    
    transactions_data = query_builder.execute().data
    
    if not transactions_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No transactions found matching the criteria')
    
    return transactions_data