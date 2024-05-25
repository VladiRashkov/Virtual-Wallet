from data.connection import query
from data.schemas import UserOut
from fastapi import HTTPException, status
from security.password_hashing import get_password_hash
from data.helpers import get_account_balance, find_user_by_email, find_user_by_id, find_user_by_username, \
    find_user_by_phone_number, \
    PHONE_NUMBER_ERROR, EMAIL_ERROR, USERNAME_ERROR, ID_ERROR, pagination_offset, is_admin, is_valid_email, \
    is_valid_password


def get_user_balance(logged_user_id):
    user_balance = get_account_balance(logged_user_id)
    return user_balance


def create(username: str, password: str, email: str, phone_number: str) -> UserOut | HTTPException:
    """This function creates a new user with the specified username, password, email, and phone number.
    It validates the input data and raises HTTP exceptions if any validation fails."""

    if find_user_by_email(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User with this email is ALREADY registered!')

    # If phone number is not equal to 10 symbols,
    # it raises error as result of the function (see how function is implemented).
    # Here we check if phone number already exists, it raises error
    if find_user_by_phone_number(phone_number):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User with this phone number is ALREADY registered!')

    if len(username) < 2 or len(username) > 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username must be between 2-20 symbols!')

    is_valid_password_data, is_valid_password_message = is_valid_password(password)

    if not is_valid_password_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=is_valid_password_message)

    # hashing the password if is valid
    hashed_password = get_password_hash(password)

    # check if email contains "@" or "."
    if not is_valid_email(email):
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


def try_login(email: str, password: str) -> UserOut | HTTPException:
    """This function attempts to log in a user with the provided email address and password.
    If the email address or password is invalid,
    it raises an HTTP exception with a 401 Unauthorized status code."""

    user = find_user_by_email(email)
    if not user:
        raise EMAIL_ERROR

    # check if user registered -> if admin confirmed his registration
    if not user.is_registered:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='User registration is not confirmed already by Admin, try again later!')

    hashed_password = get_password_hash(password)

    # check if password of current user is invalid, raise exception
    if user.password != hashed_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Please, enter a valid password!')

    return UserOut(id=user.id, username=user.username, email=user.email, phone_number=user.phone_number,
                   created_at=user.created_at)


def update_profile(password: str, email: str, phone_number: str, logged_user_id: int) -> str | HTTPException:
    """Updates the profile of the logged-in user with the provided password, email, and phone number.
        It performs validation on the inputs and ensures they are different from the current values.
        If validation passes, it updates the user's credentials in the database. Raises HTTP exceptions
        for invalid inputs or if the new credentials are the same as the current ones."""

    current_user = find_user_by_id(logged_user_id)

    if current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You CANNOT change credentials of ADMIN!')

    current_user_password = current_user.password
    current_user_email = current_user.email
    current_user_phone_number = current_user.phone_number

    hashed_pass = get_password_hash(password)

    # validation step
    is_valid_pass = is_valid_password(password)
    is_valid_email_data = is_valid_email(email)

    if is_valid_pass[0] is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=is_valid_pass[1])
    elif is_valid_email_data is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid email!')
    elif len(phone_number) != 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Phone number must be EXACTLY 10 symbols!')

    # here we will put the credentials to update, and we use it in the update method from query
    change_credentials_dict = {}

    # here we check if current password is different from new password
    if current_user_password != hashed_pass:
        # if is different, we add the new password to the dict
        change_credentials_dict.update(password=hashed_pass)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Choose different password! ')

    if current_user_email != email:
        # if is different, we add the new email to the dict
        change_credentials_dict.update(email=email)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Choose different email! ')

    if current_user_phone_number != phone_number:
        # if is different, we add the new phone_number to the dict
        change_credentials_dict.update(phone_number=phone_number)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Choose different phone_number! ')

    # and finally, we pass our change_credentials_dict to query method update
    (query.table('users').update(change_credentials_dict).eq('id', logged_user_id).execute())

    return 'Credentials updated!'


def get_logged_user(logged_user_id: int) -> UserOut | HTTPException:
    """This function retrieves information of current user!"""
    logged_user = find_user_by_id(logged_user_id)

    # it does not show password for security purposes
    return UserOut(id=logged_user.id, username=logged_user.username, email=logged_user.email,
                   phone_number=logged_user.phone_number, created_at=logged_user.created_at)


def get_all_users(logged_user_id: int, username: str = None, email: str = None, phone_number: str = None,
                  registered: bool = None, page: int = 1):
    """This function retrieves a list of all users from the database.
    It ensures that only administrators can access this information and provides an option to
    filter the users based on their registration status."""
    records_per_page = 3
    page_offset = pagination_offset(page, records_per_page)

    if not is_admin(logged_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Only ADMIN users can get information for all users!')

    # get all users with pagination
    users_data = query.table('users').select('*').range(page_offset, page_offset + records_per_page - 1).execute()
    users = users_data.data

    if phone_number:
        user = find_user_by_phone_number(phone_number)
        if not user:
            raise PHONE_NUMBER_ERROR

        return user

    elif username:
        user = find_user_by_username(username)
        if not user:
            raise USERNAME_ERROR

        return user
    elif email:
        user = find_user_by_email(email)
        if not user:
            raise EMAIL_ERROR

        return user

    not_registered_users = []

    registered_users = []

    # check for not registered users
    for user in users:
        if user['is_registered'] is False:
            not_registered_users.append(user)
        else:
            registered_users.append(user)

    if registered is None:
        return users

    elif registered is False:
        # check if not_registered users list is empty - if all users are registered
        if not not_registered_users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='It does not have non registered users for now!')
        return not_registered_users

    elif registered is True:
        # check if registered_users list is empty - if all users are not registered
        if not registered_users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='It does not have registered users for now!')
        return registered_users


def confirm_user_registration(confirmation: bool, user_email: str, logged_user_id: int):
    """This function is designed to handle the confirmation of a user's registration status.
    This function ensures that only administrators can confirm user registrations,
    checks if the user exists, and updates their registration status accordingly."""

    if not is_admin(logged_user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Only ADMIN users can confirm user registration!')

    user = find_user_by_email(user_email)
    if not user:
        raise EMAIL_ERROR

    # check if user is already registered
    if user.is_registered is True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'User with email: {user_email} is already registered!')

    if confirmation not in [True, False]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Confirm: true/false')

    if confirmation is True:
        query.table('users').update({'is_registered': confirmation}).eq('id', user.id).execute()
        return 'Confirmation for this user is successful!'

    return 'Confirmation for this user is NOT successful!'


def block_user(block_status: bool, user_id: int, logged_user_id: int):
    if not is_admin(logged_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only ADMIN users can block user!')

    user = find_user_by_id(user_id)

    if not user:
        raise ID_ERROR
    if block_status in [True, False]:
        if block_status is True:
            query.table('users').update({'is_blocked': block_status}).eq('id', user_id).execute()
        else:
            query.table('users').update({'is_blocked': block_status}).eq('id', user_id).execute()

    return f'Block status: {block_status} set successfully!'
