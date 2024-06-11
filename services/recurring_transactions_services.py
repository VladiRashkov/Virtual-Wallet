# services/recurring_transactions_services.py
from datetime import datetime, timedelta
from data.scheduler import scheduler  # Import the scheduler
from data.connection import query
from data.models import RecurringTransaction
from fastapi import HTTPException, status
from data.schemas import CreateRecurringTransaction, UpdateRecurringTransaction
import logging

def get_all_recurring_transactions(sender_id:int):
    '''Retrieve all recurring transactions initiated by a given sender'''
    all_transactions = query.table('recurring_transactions').select('receiver_id', 'amount', 'created_at', 'recurring_time').eq('sender_id', sender_id).execute()
    return all_transactions

logging.basicConfig(level=logging.DEBUG)
def process_recurring_transaction(transaction_id: int):
    ''' Process a recurring transaction and schedule the next run based on its recurring time.'''
    
    logging.info(f"Processing recurring transaction: {transaction_id}")
    transaction_data = query.table('recurring_transactions').select('*').eq('id', transaction_id).execute().data
    if not transaction_data:
        logging.error(f"No transaction data found for ID: {transaction_id}")
        return

    transaction = RecurringTransaction.from_query_result(**transaction_data[0])
    
    sender_balance_data = query.table('users').select('amount').eq('id', transaction.sender_id).execute().data
    receiver_balance_data = query.table('users').select('amount').eq('id', transaction.receiver_id).execute().data
    
    if not sender_balance_data or not receiver_balance_data:
        logging.error(f"No balance data found for sender or receiver.")
        return
    
    sender_balance = sender_balance_data[0]['amount']
    receiver_balance = receiver_balance_data[0]['amount']
    
    if sender_balance < transaction.amount:
        query.table('recurring_transactions').update({'status': 'failed'}).eq('id', transaction_id).execute()
        logging.info(f"Transaction {transaction_id} failed due to insufficient balance.")
        return
    
    new_sender_balance = sender_balance - transaction.amount
    new_receiver_balance = receiver_balance + transaction.amount
    
    query.table('users').update({'amount': new_sender_balance}).eq('id', transaction.sender_id).execute()
    query.table('users').update({'amount': new_receiver_balance}).eq('id', transaction.receiver_id).execute()
    
    query.table('transactions').insert({
        'sender_id': transaction.sender_id,
        'receiver_id': transaction.receiver_id,
        'amount': transaction.amount,
        'status': 'confirmed',
        'category': 'recurring',
        'created_at': datetime.now().isoformat()  # Convert to string
    }).execute()
    
    if transaction.recurring_time == 'daily':
        next_run_time = datetime.now() + timedelta(days=1)
    elif transaction.recurring_time == 'weekly':
        next_run_time = datetime.now() + timedelta(weeks=1)
    elif transaction.recurring_time == 'monthly':
        next_run_time = datetime.now() + timedelta(weeks=4)
    elif transaction.recurring_time == 'minutely':
        next_run_time = datetime.now() + timedelta(minutes=1)
    else:
        logging.error(f"Invalid recurring time: {transaction.recurring_time}")
        return
    
    if next_run_time:
        query.table('recurring_transactions').update({'created_at': next_run_time.isoformat()}).eq('id', transaction_id).execute()  # Convert to string
        scheduler.add_job(process_recurring_transaction, 'date', run_date=next_run_time, args=[transaction_id])
        logging.info(f"Scheduled next run for transaction {transaction_id} at {next_run_time.isoformat()}")

def create_recurring_transaction(sender_id: int, transaction: CreateRecurringTransaction) -> str:
    '''Create a recurring transaction in the system and schedule it for processing.'''
    
    next_run_time = datetime.now()

    transaction_data = {
        'sender_id': sender_id,
        'receiver_id': transaction.receiver_id,
        'amount': transaction.amount,
        'created_at': next_run_time.isoformat(),  # Convert to string
        'recurring_time': transaction.recurring_time,
        'status': 'approved'
    }
    result = query.table('recurring_transactions').insert(transaction_data).execute()
    transaction_id = result.data[0]['id']
    
    scheduler.add_job(process_recurring_transaction, 'date', run_date=next_run_time, args=[transaction_id])
    logging.info(f"Created and scheduled recurring transaction {transaction_id} to run at {next_run_time.isoformat()}")
    return 'Recurring transaction created successfully'


def update_recurring_transaction(transaction_id:int, user_id:id, update_transaction: UpdateRecurringTransaction):
    '''Update details of a recurring transaction and reschedule its processing if necessary.'''
    
    transaction_data = query.table('recurring_transactions').select('*').eq('id', transaction_id).execute().data
    if not transaction_data:
        return False
    
    transaction = transaction_data[0]
    
    if transaction['sender_id'] != user_id:
        return False
    
    update_data = {
        'receiver_id':update_transaction.receiver_id,
        'amount':update_transaction.amount,
        'recurring_time': update_transaction.recurring_time,
        'status': update_transaction.status,
        'created_at': datetime.now().isoformat()
    }
    
    # Update the transaction details
    query.table('recurring_transactions').update(update_data).eq('id', transaction_id).execute()
    logging.info(f'Updated recurring transaction {transaction_id}')
    
    # Check if the job exists in the scheduler before removing it
    if scheduler.get_job(str(transaction_id)):
        # Job exists, so remove it
        scheduler.remove_job(str(transaction_id))
        logging.info(f'Removed job for transaction {transaction_id}')
    
    # Calculate the next run time based on the updated transaction details
    next_run_time = datetime.now()
    if update_transaction.recurring_time == 'daily':
        next_run_time += timedelta(days=1)
    elif update_transaction.recurring_time == 'weekly':
        next_run_time += timedelta(weeks=1)
    elif update_transaction.recurring_time == 'monthly':
        next_run_time += timedelta(weeks=4)
    elif update_transaction.recurring_time == 'minutely':
        next_run_time += timedelta(minutes=1)
    
    # Add a new job with the updated details and reschedule it
    scheduler.add_job(process_recurring_transaction, 'date', run_date=next_run_time, args=[transaction_id])
    logging.info(f"Rescheduled next run for transaction {transaction_id} at {next_run_time.isoformat()}")
    
    return True


def delete_recurring_transaction(recurring_transaction_id: int, user_id: int) -> bool:
    ''' Delete a recurring transaction from the database if the user has permission.'''
    
    transaction_data = query.table('recurring_transactions').select('*').eq('id', recurring_transaction_id).execute().data
    if not transaction_data:
        return False

    transaction = transaction_data[0]
    if transaction['sender_id'] != user_id:
        return False

    query.table('recurring_transactions').delete().eq('id', recurring_transaction_id).execute()
    logging.info(f"Deleted recurring transaction {recurring_transaction_id}")
    

    return True 