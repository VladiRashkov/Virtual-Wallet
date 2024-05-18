from data.connection import query
from fastapi import HTTPException, status


def all_user_transactions(sender_id: int, sort: str | None):
    """This function retrieves all transactions made by a user with the specified sender ID. If no transactions are found,
    it raises an HTTP exception with a 404 Not Found status code."""

    data = query.table('transactions').select('*').eq('sender_id', sender_id).execute()
    transactions = data.data

    if not transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with id {sender_id} has no transactions!')
    return transactions


def transfer_money(sender_id: int, receiver_id: int, amount: float):  # TODO add category
    sender = query.table('users').select('amount').eq('id', sender_id).execute()
    receiver = query.table('users').select('amount').eq('id', receiver_id).execute()

    sender_data = sender.data
    receiver_data = receiver.data

    if not sender_data or not receiver_data:
        return "Error: Sender or receiver not found"  # TODO raise exception

    sender_balance = sender_data[0]['amount']
    receiver_balance = receiver_data[0]['amount']

    if sender_balance < amount:
        return 'Insufficient balance'  # TODO raise exception

    new_sender_balance = sender_balance - amount
    new_receiver_balance = receiver_balance + amount

    query.table('users').update({'amount': new_sender_balance}).eq('id', sender_id).execute()
    query.table('users').update({'amount': new_receiver_balance}).eq('id', receiver_id).execute()

    transaction_data = {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'amount': amount
    }

    query.table('transactions').insert(transaction_data).execute()

    return 'Successful'
