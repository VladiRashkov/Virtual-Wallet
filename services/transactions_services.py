from data.connection import query
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any
from services.user_services import get_account_balance
from data.schemas import AmountOut, WithdrawMoney


# TODO make a confirmation step when creating a transaction! (maybe new endpoint)

def all_user_transactions(user_id: int, transaction_type: str = "all", sort_by: Optional[str] = None,
                          order: Optional[str] = None) -> List[Dict[str, Any]]:
    """This function retrieves all transactions made by a user with the specified sender ID. If no transactions are found,
    it raises an HTTP exception with a 404 Not Found status code."""

    transactions = []

    if transaction_type in ['sent', 'all']:
        sent_data = query.table('transactions').select('*').eq('sender_id', user_id).execute()
        transactions.extend(sent_data.data)

    if transaction_type in ["received", "all"]:
        received_data = query.table('transactions').select('*').eq('receiver_id', user_id).execute()
        transactions.extend(received_data.data)

    if not transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with id {user_id} has no transactions!')

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

    
