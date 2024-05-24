from data.connection import query
from data.schemas import GetUser, AccountBalanceOut, TransactionOut
from fastapi import HTTPException, status

PHONE_NUMBER_ERROR = HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                   detail='User with this phone number not found!')
EMAIL_ERROR = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User with this email not found!')
ID_ERROR = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User with this id not found!')
USERNAME_ERROR = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User with this username not found!')
ADMIN_ERROR = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin cannot do this!')
TRANSACTION_ERROR = HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                  detail='Transaction with this id is not found!')


def find_user_by_phone_number(phone_number: str) -> GetUser | None:
    """This function retrieves a user record from the database by the specified phone number.
        It queries the 'users' table for a matching phone number and
        returns a User object populated with the user's details if found.
        If no user is found with the given phone number, the function returns None."""

    user_data = query.table('users').select('*').eq('phone_number', phone_number).execute()

    if len(phone_number) != 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Phone number must be EXACTLY 10 symbols!')

    if not user_data.data:
        return

    user = user_data.data[0]

    return GetUser(
        id=user['id'],
        username=user['username'],
        password=user['password'],
        email=user['email'],
        phone_number=user['phone_number'],
        is_admin=user['is_admin'],
        created_at=user['created_at'],
        amount=user['amount'],
        is_registered=user['is_registered'],
        is_blocked=user['is_blocked']
    )


def find_user_by_username(username: str):
    user_data = query.table('users').select('*').eq('username', username).execute()

    if not user_data.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with username: {username} is not found!')

    user = user_data.data[0]

    return GetUser(
        id=user['id'],
        username=user['username'],
        password=user['password'],
        email=user['email'],
        phone_number=user['phone_number'],
        is_admin=user['is_admin'],
        created_at=user['created_at'],
        amount=user['amount'],
        is_registered=user['is_registered'],
        is_blocked=user['is_blocked']
    )


def find_user_by_email(email) -> GetUser | None:
    """This function retrieves a user record from the database by the specified email address.
    It queries the 'users' table for a matching email and returns a User object populated with
    the user's details if found.
    If no user is found with the given email, the function returns None."""

    # return ORM object
    email_data = query.table('users').select('*').eq('email', email).execute()

    # convert data ORM object to list with dictionary in it
    email_data_lst = email_data.data

    if not email_data_lst:
        return

        # check if data_lst is empty, if it's empty, that's because user with this email is not found and return none

        # access dictionary from the list
    email_dict = email_data_lst[0]

    return GetUser(
        id=email_dict['id'],
        username=email_dict['username'],
        password=email_dict['password'],
        email=email_dict['email'],
        phone_number=email_dict['phone_number'],
        is_admin=email_dict['is_admin'],
        created_at=email_dict['created_at'],
        amount=email_dict['amount'],
        is_registered=email_dict['is_registered'],
        is_blocked=email_dict['is_blocked']
    )


def find_user_by_id(user_id: int) -> GetUser | None:
    user_data = query.table('users').select('*').eq('id', user_id).execute()

    if not user_data.data:
        return
    user = user_data.data[0]

    return GetUser(
        id=user['id'],
        username=user['username'],
        password=user['password'],
        email=user['email'],
        phone_number=user['phone_number'],
        is_admin=user['is_admin'],
        created_at=user['created_at'],
        amount=user['amount'],
        is_registered=user['is_registered'],
        is_blocked=user['is_blocked']
    )


def get_account_balance(user_id: int) -> AccountBalanceOut | None:
    """This function checks account balance of logged user"""
    user = find_user_by_id(user_id)
    if not user:
        return
    amount = user.amount
    return AccountBalanceOut(balance=amount)


def is_admin(user_id: int):
    user = find_user_by_id(user_id)
    if user and user.is_admin:
        return True
    return False


def pagination_offset(page: int, page_size: int):
    offset = (page - 1) * page_size
    return offset


def get_transaction(transaction_id: int) -> TransactionOut | None:
    transaction_data = query.table('transactions').select('*').eq('id', transaction_id).execute().data

    if not transaction_data:
        return

    transaction = transaction_data[0]

    created_at = transaction['created_at']
    amount = transaction['amount']
    sender_id = transaction['sender_id']
    receiver_id = transaction['receiver_id']
    transaction_status = transaction['status']
    category = transaction['category']
    acceptation = transaction['acceptation']

    return TransactionOut(id=transaction_id, created_at=created_at, amount=amount, sender_id=sender_id,
                          receiver_id=receiver_id, status=transaction_status, category=category,
                          acceptation=acceptation)


def update_transaction(transaction_id: int, update_dict_data: dict):
    transaction_data = query.table('transactions').update(update_dict_data).eq('id', transaction_id).execute().data
    if not transaction_data:
        return

    transaction = transaction_data[0]

    created_at = transaction['created_at']
    amount = transaction['amount']
    sender_id = transaction['sender_id']
    receiver_id = transaction['receiver_id']
    transaction_status = transaction['status']
    category = transaction['category']
    acceptation = transaction['acceptation']

    return TransactionOut(id=transaction_id, created_at=created_at, amount=amount, sender_id=sender_id,
                          receiver_id=receiver_id, status=transaction_status, category=category,
                          acceptation=acceptation)
