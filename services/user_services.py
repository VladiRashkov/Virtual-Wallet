from data.connection import query
from data.schemas import UserOut, AmountOut, AccountBalanceOut
from fastapi import HTTPException, status
from re import search
from security.password_hashing import get_password_hash
from data.models import User


def get_account_balance(user_id: int) -> AccountBalanceOut:
    """This function checks account balance of logged user"""
    data = query.table('users').select('amount').eq('id', user_id).execute()

    # convert ORM object to list with dictionary
    balance_list = data.data

    # convert balance_list to dictionary
    balance = balance_list[0]

    # return balance as dictionary
    return AccountBalanceOut(balance=balance['amount'])


def update_account_balance(amount: float, user_id: int) -> AmountOut:
    """This function update account balance of logged user.
    If amount is negative number or equal to 0, it raises exception!"""
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid amount!')

    # get account balance as obj
    old_balance_obj = get_account_balance(user_id)

    # get account balance as float
    old_balance = old_balance_obj.balance

    # sum old balance + amount
    new_balance = old_balance + amount

    # update account balance
    balance_data = query.table('users').update({"amount": new_balance}).eq('id', user_id).execute()
    balance_list = balance_data.data
    balance_dict = balance_list[0]

    # get updated account balance
    balance = balance_dict['amount']

    return AmountOut(message="Balance updated!", old_balance=old_balance, new_balance=balance)


def _is_valid_password(password: str) -> tuple[bool, str]:
    """This function checks if a given password meets specific security requirements.
    It returns a boolean indicating the validity of the password and a message detailing the result."""

    if len(password) < 8:
        return False, 'Password length must be more than 8 symbols!'
    if not search(r'[A-Z]', password):
        return False, 'Password must have at least one capital letter!'
    if not search(r'\d', password):
        return False, 'Password must have at least one digit!'
    if not search(r'[+\-*^&]', password):
        return False, 'Password must have at least one special character: (+, -, *, &, ^, …)'

    return True, 'Password is created!'


def _is_valid_email(email: str) -> True | False:
    """This function checks if a given email address is valid based on the presence of '@' and '.' characters."""

    if ('@' or '.') not in email:
        return False
    return True


def create(username: str, password: str, email: str, phone_number: str) -> UserOut | HTTPException:
    """This function creates a new user with the specified username, password, email, and phone number.
    It validates the input data and raises HTTP exceptions if any validation fails."""

    if len(username) < 2 or len(username) > 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username must be between 2-20 symbols!')

    is_valid_password, is_valid_password_message = _is_valid_password(password)

    if not is_valid_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=is_valid_password_message)

    # hashing the password if is valid
    hashed_password = get_password_hash(password)

    # check if email contains "@" or "."
    if not _is_valid_email(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email is not valid!')

    try:
        # variable 'data'  will return a ORM object
        data = query.table('users').insert(
            {"username": username, "password": hashed_password, "email": email, "phone_number": phone_number}).execute()

        # convert variable 'data' to list with dictionaries
        data_lst = data.data

        generated_id = int(data_lst[0]['id'])
        created_at = data_lst[0]['created_at']

        return UserOut(id=generated_id, username=username, email=email, phone_number=phone_number,
                       created_at=created_at)

    except Exception as err:
        # create a 'error_message' variable with error details
        error_message = err.details if hasattr(err, 'details') else 'No details available'
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)


def _find_user_by_email(email) -> User | None:
    """This function retrieves a user record from the database by the specified email address.
    It queries the 'users' table for a matching email and returns a User object populated with the user's details if found.
    If no user is found with the given email, the function returns None."""
    # return ORM object
    data = query.table('users').select('id', 'username', 'password', 'email', 'phone_number', 'created_at').eq('email',
                                                                                                               email).execute()

    # convert data ORM object to list with dictionary in it
    data_lst = data.data

    # check if data_lst is empty, if it's empty, that's because user with this email is not found and return none

    if not data_lst:
        return
        # access dictionary from the list
    data_dict = data_lst[0]

    return User(
        id=data_dict['id'],
        username=data_dict['username'],
        password=data_dict['password'],
        email=data_dict['email'],
        phone_number=data_dict['phone_number'],
        created_at=data_dict['created_at']
    )


def try_login(email: str, password: str) -> User | HTTPException:
    """This function attempts to log in a user with the provided email address and password.
    If the email address or password is invalid,
    it raises an HTTP exception with a 401 Unauthorized status code."""

    # if email is wrong, return none
    user = _find_user_by_email(email)

    # check if user exists
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Email address: {email} is not valid! Please enter a valid email address!')

    hashed_password = get_password_hash(password)

    # check if password of current user is invalid, raise exception
    if user.password != hashed_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Please, enter a valid password!')

    return user
