from data.connection import query
import security.password_hashing
from data.schemas import UserOut
from fastapi import HTTPException, status
from re import search
from security.password_hashing import get_password_hash
from data.models import User


def _is_valid_password(password: str):
    if len(password) < 8:
        return False, 'Password length must be more than 8 symbols!'
    if not search(r'[A-Z]', password):
        return False, 'Password must have at least one capital letter!'
    if not search(r'\d', password):
        return False, 'Password must have at least one digit!'
    if not search(r'[+\-*^&]', password):
        return False, 'Password must have at least one special character: (+, -, *, &, ^, …)'

    return True, 'Password is created!'


def _is_valid_email(email: str):
    if ('@' or '.') not in email:
        return False
    return True


def create(username: str, password: str, email: str, phone_number: str):
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


def _find_user_by_email(email):
    # return ORM object
    data = query.table('users').select('id', 'username', 'password', 'email', 'phone_number', 'created_at').eq('email',
                                                                                                               email).execute()
    # convert data ORM object to list with dictionary in it
    data_lst = data.data

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


def try_login(email: str, password: str):
    user = _find_user_by_email(email)

    hashed_password = get_password_hash(password)

    return user if user and user.password == hashed_password else None
