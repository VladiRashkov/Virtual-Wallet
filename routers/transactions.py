from fastapi import APIRouter, Depends, Query
from services import transactions_services
from common.authorization import get_current_user
from typing import Optional, List
from data.schemas import DepositAmount, WithdrawMoney, CreateTransaction, ConfirmOrDecline, AcceptTransaction

from datetime import date
from data.models import Transaction


transaction_router = APIRouter(prefix='/transactions', tags=['Transactions'])


@transaction_router.get('/user')
def get_logged_user_transactions(sort_by: Optional[str] = Query('created_at', pattern='^(created_at|amount)$'),
                                 order: Optional[str] = Query('desc', pattern='^(asc|desc)$'),
                                 transaction_type: str = Query(None, pattern='^(sent|received)$'),
                                 transaction_status: str = Query('all', pattern='^(confirmed|pending|declined|all)$'),
                                 sender_id: int = Depends(get_current_user)):
    ''''This endpoint retrieves transactions associated with the logged-in user.
    It allows filtering transactions based on parameters such as sorting criteria (sort_by),
    sorting order (order), transaction type (transaction_type),
    and transaction status (transaction_status).
    The default sorting criterion is created_at in descending order (desc).
    The transaction type can be specified as either sent or received, and the transaction status
    can be confirmed, pending, declined, or all.
    The endpoint ensures authentication by depending on the get_current_user
    dependency to retrieve the sender's ID.'''
    transactions = transactions_services.get_logged_user_transactions(sender_id, transaction_type, sort_by, order,
                                                                      transaction_status)
    return transactions


@transaction_router.post('/transaction')
def create_transaction(transaction_credentials: CreateTransaction, sender_id: int = Depends(get_current_user)):
    '''Creates a new transaction initiated by the logged-in user.'''
    result = transactions_services.transfer_money(sender_id, transaction_credentials.receiver_id,
                                                  transaction_credentials.amount,
                                                  transaction_credentials.category)
    return {'message': result[0]}


@transaction_router.put('/{transaction_id}/category')
def edit_category(transaction_id: int, category_name: str, logged_user_id: int = Depends(get_current_user)):
    '''Edits the category of a transaction by the logged-in user.'''
    
    result = transactions_services.edit_category(transaction_id, category_name, logged_user_id)
    return result


@transaction_router.get('/{category_name}')
def get_category_report(order: str, category_name: str, logged_user_id: int = Depends(get_current_user),
                        start_date: Optional[date] = None, end_date: Optional[date] = None):
    '''Retrieves a category report for the logged-in user.'''
    result = transactions_services.get_category_report(order, category_name, logged_user_id, start_date, end_date)
    return result


@transaction_router.put('/deposit')
def deposit_money(deposit_credentials: DepositAmount, user: int = Depends(get_current_user)):
    '''    Deposits money into the account of the logged-in user.'''
    result = transactions_services.deposit_money(deposit_credentials.deposit_amount, user)
    return result


@transaction_router.put('/withdraw')
def extract_money(withdraw_sum: WithdrawMoney, user: int = Depends(get_current_user)):
    result = transactions_services.withdraw_money(withdraw_sum.withdraw_sum, user)
    return result


@transaction_router.put('/confirm/{transaction_id}')
def confirm_transaction(confirm_or_decline: ConfirmOrDecline, transaction_id: int,
                        user: int = Depends(get_current_user)):
    '''Extracts money from the account of the logged-in user.'''
    result = transactions_services.confirm_transaction(confirm_or_decline.confirm_or_decline, transaction_id, user)
    return result


@transaction_router.put('/accept/{transaction_id}')
def accept_transaction(transaction_id: int, acceptation: AcceptTransaction, user: int = Depends(get_current_user)):
    ''' Accepts a transaction by the logged-in user.'''
    result = transactions_services.accept_transaction(transaction_id, acceptation.acceptation, user)
    return result



# @transaction_router.get('/filter', response_model=List[Transaction])
# def filter_transactions_endpoint(
#         start_date: Optional[date] = Query(None, description="Start date in the format YYYY-MM-DD"),
#         end_date: Optional[date] = Query(None, description="End date in the format YYYY-MM-DD"),
#         sender_id: Optional[int] = Query(None),
#         receiver_id: Optional[int] = Query(None),
#         transaction_type: str = Query('all', pattern='^(sent|received|all)$'),
#         user_id: int = Depends(get_current_user)
#
# ):
#     '''
#     Retrieves transactions based on specified filters for the logged-in user.
#
#     Parameters:
#     - start_date (Optional[date]): Start date for filtering transactions (YYYY-MM-DD format).
#     - end_date (Optional[date]): End date for filtering transactions (YYYY-MM-DD format).
#     - sender_id (Optional[int]): ID of the sender for filtering transactions.
#     - receiver_id (Optional[int]): ID of the receiver for filtering transactions.
#     - transaction_type (str): Type of transactions to retrieve ('sent', 'received', or 'all').
#     - user_id (int): ID of the logged-in user.
#
#     Returns:
#     - List[Transaction]: List of transactions that match the specified filters.
#     '''
#     transactions = transactions_services.filter_transactions(
#         user_id=user_id,
#         start_date=start_date,
#         end_date=end_date,
#         sender_id=sender_id,
#         receiver_id=receiver_id,
#         transaction_type=transaction_type
#     )
#     return transactions


@transaction_router.get('/all/{user_id}')
def get_all_transactions(user_id: int, logged_user_id: int = Depends(get_current_user), page: int = 1,
                         sent_or_received: str = None,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None, direction: str = None,
                         sort: str = Query(None, description="amount | created_at"), order: str = 'desc'):
    '''Retrieves all transactions for a specified user.'''
    result = transactions_services.get_all_transactions(user_id, logged_user_id, page, sent_or_received, start_date,
                                                        end_date, direction, sort, order)
    return result


@transaction_router.put('/deny/{transaction_id}')
def deny_transaction(transaction_id: int, logged_user_id: int = Depends(get_current_user)):
    '''Denies a transaction by the logged-in user.'''
    result = transactions_services.deny_transaction(transaction_id, logged_user_id)
    return result
