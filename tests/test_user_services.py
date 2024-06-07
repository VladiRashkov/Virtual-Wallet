import unittest
from unittest.mock import patch, Mock, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

import common.authorization
import routers.users
import services.user_services
from main import app
from data.schemas import UserOut, GetUser, AccountBalanceOut

ID = 1
USERNAME = 'test'
PASSWORD = 'test123'
EMAIL = 'test@test.test'
PHONE_NUM = '1234567890'
IS_ADMIN = False
CREATED_AT = '2024-06-01T00:00:00+00:00'
AMOUNT = 10.0
IS_REGISTERED = True
IS_BLOCKED = False

ID = 1
USERNAME = 'test'
PASSWORD = 'test123'
EMAIL = 'test@test.test'
PHONE_NUM = '1234567890'
IS_ADMIN = False
CREATED_AT = '2024-06-01T00:00:00+00:00'
AMOUNT = 10.0
IS_REGISTERED = True
IS_BLOCKED = False


class TestUserServices(unittest.TestCase):
    @patch('routers.users.get_current_user')
    @patch('services.user_services.find_user_by_id')
    @patch('services.user_services.get_password_hash')
    @patch('services.user_services.is_valid_password')
    @patch('services.user_services.is_valid_email')
    @patch('services.user_services.query.table')
    def test_update(self, mock_query_table, mock_is_valid_email, mock_is_valid_pass, mock_get_pass_hash,
                    mock_find_user_by_id, mock_get_current_user):
        mock_get_current_user.return_value = ID
        mock_find_user_by_id.return_value = GetUser(id=ID, username=USERNAME, password=PASSWORD,
                                                    email=EMAIL, phone_number=PHONE_NUM, is_admin=IS_ADMIN,
                                                    created_at=CREATED_AT, amount=AMOUNT, is_registered=IS_REGISTERED,
                                                    is_blocked=IS_BLOCKED)
        mock_is_valid_email.return_value = True
        mock_is_valid_pass.return_value = (True, '')
        mock_get_pass_hash.return_value = 'new_hash_pass'

        mock_update = MagicMock()
        mock_query_table.return_value.update.return_value.eq.return_value.execute = mock_update

        result = services.user_services.update_profile('newpassword123', 'new@example.com', '0987654321', ID)

        self.assertEqual(result, 'Credentials updated!')

        mock_find_user_by_id.assert_called_once_with(ID)

        mock_get_pass_hash.assert_called_once_with('newpassword123')
        mock_is_valid_pass.assert_called_once_with('newpassword123')
        mock_is_valid_email.assert_called_once_with('new@example.com')
        mock_update.assert_called_once()

    @patch('services.user_services.get_account_balance')
    def test_get_user_balance(self, mock_get_account_balance):
        mock_get_account_balance.return_value = AccountBalanceOut(balance=100.10)

        user = services.user_services.get_user_balance(ID)

        self.assertEqual(user.balance, 100.1)
        self.assertIsInstance(user, AccountBalanceOut)

    @patch('services.user_services.find_user_by_email', return_value=None)
    @patch('services.user_services.find_user_by_phone_number', return_value=None)
    @patch('services.user_services.is_valid_password', return_value=(True, ""))
    @patch('services.user_services.get_password_hash', return_value="hashedpass")
    @patch('services.user_services.is_valid_email', return_value=True)
    @patch('services.user_services.query.table')
    def test_create_user(self, mock_query_table, mock_is_valid_email, mock_hashed_pass,
                         mock_is_valid_password, mock_find_user_by_phone_number,
                         mock_find_user_by_email):
        mock_insert = MagicMock()
        mock_query_table.return_value.insert.return_value.execute = mock_insert
        mock_insert.return_value.data = [{
            "id": ID,
            "created_at": CREATED_AT
        }]

        expected = UserOut(
            id=ID, username=USERNAME, email=EMAIL,
            phone_number=PHONE_NUM, created_at=CREATED_AT
        )

        res = services.user_services.create(USERNAME, PASSWORD, EMAIL, PHONE_NUM)

        self.assertEqual(res, expected)

    @patch('services.user_services.find_user_by_email')
    @patch('services.user_services.get_password_hash')
    def test_try_login(self, mock_pass_hash, mock_find_user_by_email):
        mock_find_user_by_email.return_value = GetUser(id=ID, username=USERNAME, password=PASSWORD,
                                                       email=EMAIL, phone_number=PHONE_NUM, is_admin=IS_ADMIN,
                                                       created_at=CREATED_AT, amount=AMOUNT,
                                                       is_registered=IS_REGISTERED,
                                                       is_blocked=IS_BLOCKED)
        mock_pass_hash.return_value = PASSWORD

        expected = UserOut(id=ID, username=USERNAME, email=EMAIL, phone_number=PHONE_NUM,
                           created_at=CREATED_AT)

        res = services.user_services.try_login(EMAIL, PASSWORD)

        self.assertEqual(res, expected)
        self.assertIsInstance(res, UserOut)

    @patch('services.user_services.find_user_by_id')
    @patch('services.user_services.is_valid_password')
    @patch('services.user_services.is_valid_email')
    @patch('services.user_services.query.table')
    def test_update_profile(self, mock_query_table, mock_is_valid_email, mock_is_valid_pass,
                            mock_find_user_by_id):
        mock_find_user_by_id.return_value = GetUser(id=ID, username=USERNAME, password=PASSWORD,
                                                    email=EMAIL, phone_number=PHONE_NUM, is_admin=IS_ADMIN,
                                                    created_at=CREATED_AT, amount=AMOUNT, is_registered=IS_REGISTERED,
                                                    is_blocked=IS_BLOCKED)
        mock_is_valid_pass.return_value = (True, "")
        mock_is_valid_email.return_value = True

        mock_update = MagicMock()
        mock_query_table.return_value.update.return_value.eq.return_value.execute = mock_update

        res = services.user_services.update_profile('new_pass', 'new_email', '1234567891', ID)

        expected = 'Credentials updated!'

        self.assertEqual(res, expected)
        mock_update.assert_called_once()

    @patch('services.user_services.find_user_by_id')
    def test_get_logged_user(self, mock_find_user_by_id):
        mock_find_user_by_id.return_value = GetUser(id=ID, username=USERNAME, password=PASSWORD,
                                                    email=EMAIL, phone_number=PHONE_NUM, is_admin=IS_ADMIN,
                                                    created_at=CREATED_AT, amount=AMOUNT, is_registered=IS_REGISTERED,
                                                    is_blocked=IS_BLOCKED)

        expected = UserOut(id=ID, username=USERNAME, email=EMAIL,
                           phone_number=PHONE_NUM, created_at=CREATED_AT)

        res = services.user_services.get_logged_user(ID)

        self.assertEqual(res, expected)
        self.assertIsInstance(res, UserOut)

    @patch('services.user_services.is_admin')
    @patch('services.user_services.query.table')
    @patch('services.user_services.find_user_by_phone_number')
    @patch('services.user_services.find_user_by_username')
    @patch('services.user_services.find_user_by_email')
    def test_get_all_users(self, mock_find_user_by_email, mock_find_user_by_username, mock_find_user_by_phone_number,
                           mock_query_table, mock_is_admin):
        mock_is_admin.return_value = True

        mock_users_data = MagicMock()
        mock_users_data.data = [
            {
                "id": 1,
                "username": USERNAME,
                "password": PASSWORD,
                "email": EMAIL,
                "phone_number": PHONE_NUM,
                "is_admin": IS_ADMIN,
                "created_at": CREATED_AT,
                "amount": AMOUNT,
                "is_registered": IS_REGISTERED,
                "is_blocked": IS_BLOCKED
            },
            {
                "id": 2,
                "username": "user2",
                "password": "hashed_password",
                "email": "user2@example.com",
                "phone_number": "0987654321",
                "is_admin": False,
                "created_at": CREATED_AT,
                "amount": 50.0,
                "is_registered": False,
                "is_blocked": False
            }
        ]

        mock_query_table.return_value.select.return_value.range.return_value.execute.return_value = mock_users_data

        # Test all users
        users = services.user_services.get_all_users(logged_user_id=ID, page=1)
        self.assertEqual(len(users), 2)

        # Test with phone number
        mock_find_user_by_phone_number.return_value = mock_users_data.data[0]
        user = services.user_services.get_all_users(logged_user_id=ID, phone_number=PHONE_NUM)
        self.assertEqual(user, mock_users_data.data[0])
        mock_find_user_by_phone_number.assert_called_once_with(PHONE_NUM)

        # Test with username
        mock_find_user_by_username.return_value = mock_users_data.data[0]
        user = services.user_services.get_all_users(logged_user_id=ID, username=USERNAME)
        self.assertEqual(user, mock_users_data.data[0])
        mock_find_user_by_username.assert_called_once_with(USERNAME)

        # Test with email
        mock_find_user_by_email.return_value = mock_users_data.data[0]
        user = services.user_services.get_all_users(logged_user_id=ID, email=EMAIL)
        self.assertEqual(user, mock_users_data.data[0])
        mock_find_user_by_email.assert_called_once_with(EMAIL)

        # Test with registered=True
        users = services.user_services.get_all_users(logged_user_id=ID, registered=True)
        self.assertEqual(len(users), 1)
        self.assertTrue(users[0]['is_registered'])

        # Test with registered=False
        users = services.user_services.get_all_users(logged_user_id=ID, registered=False)
        self.assertEqual(len(users), 1)
        self.assertFalse(users[0]['is_registered'])

        # Test when user is NOT admin
        mock_is_admin.return_value = False
        with self.assertRaises(HTTPException):
            services.user_services.get_all_users(logged_user_id=ID, page=1)

    @patch('services.user_services.is_admin')
    @patch('services.user_services.find_user_by_email')
    @patch('services.user_services.query.table')
    def test_confirm_user_registration(self, mock_query_table, mock_find_user_by_email, mock_is_admin):
        mock_is_admin.return_value = True

        mock_find_user_by_email.return_value = GetUser(
            id=ID, username=USERNAME, password=PASSWORD,
            email=EMAIL, phone_number=PHONE_NUM, is_admin=IS_ADMIN,
            created_at=CREATED_AT, amount=AMOUNT, is_registered=False,
            is_blocked=IS_BLOCKED)

        mock_update = MagicMock()
        mock_query_table.return_value.update.return_value.eq.return_value.execute = mock_update

        # register
        result = services.user_services.confirm_user_registration(True, EMAIL, ID)
        self.assertEqual(result, 'Confirmation for this user is successful!')

        # check if method is called successfully
        mock_update.assert_called_once_with()

        #  Raise error when user is already registered
        mock_find_user_by_email.return_value = GetUser(
            id=ID, username=USERNAME, password=PASSWORD,
            email=EMAIL, phone_number=PHONE_NUM, is_admin=IS_ADMIN,
            created_at=CREATED_AT, amount=AMOUNT, is_registered=True,  # Вече регистриран
            is_blocked=IS_BLOCKED)
        with self.assertRaises(HTTPException):
            services.user_services.confirm_user_registration(True, EMAIL, ID)

        # Raise error when confirmation is not valid
        with self.assertRaises(HTTPException):
            services.user_services.confirm_user_registration(None, EMAIL, ID)

    @patch('services.user_services.is_admin')
    @patch('services.user_services.find_user_by_id')
    @patch('services.user_services.query.table')
    def test_block_user(self, mock_query_table, mock_find_user_by_id, mock_is_admin):
        mock_is_admin.return_value = True

        mock_find_user_by_id.return_value = GetUser(
            id=ID, username=USERNAME, password=PASSWORD,
            email=EMAIL, phone_number=PHONE_NUM, is_admin=IS_ADMIN,
            created_at=CREATED_AT, amount=AMOUNT, is_registered=IS_REGISTERED,
            is_blocked=IS_BLOCKED)

        mock_update = MagicMock()
        mock_query_table.return_value.update.return_value.eq.return_value.execute = mock_update

        # block user
        result = services.user_services.block_user(True, ID, ID)
        self.assertEqual(result, 'Block status: True set successfully!')

        # check if method is called successfully
        mock_update.assert_called_once_with()

        # unblock user
        result = services.user_services.block_user(False, ID, ID)
        self.assertEqual(result, 'Block status: False set successfully!')

        # check if method is called twice, one time for blocking, one time for unblocking
        self.assertEqual(mock_update.call_count, 2)

        # Raise error when id is not valid
        mock_find_user_by_id.return_value = None
        with self.assertRaises(HTTPException):
            services.user_services.block_user(True, 999, ID)

        # Raise error when user is not admin
        mock_is_admin.return_value = False
        with self.assertRaises(HTTPException):
            services.user_services.block_user(True, ID, ID)


if __name__ == '__main__':
    unittest.main()
