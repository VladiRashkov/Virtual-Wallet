import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from data.schemas import UserOut, GetUser

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


class TestUsersEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.user_create_payload = {
            "username": "testuser",
            "password": "TestPassword123!",
            "email": "test@example.com",
            "phone_number": "1234567890"
        }
        self.update_profile_payload = {
            "password": "NewPassword123!",
            "email": "newemail@example.com",
            "phone_number": "0987654321"
        }

    @patch('services.user_services.find_user_by_email', return_value=None)
    @patch('services.user_services.find_user_by_phone_number', return_value=None)
    @patch('services.user_services.is_valid_password', return_value=(True, ""))
    @patch('services.user_services.get_password_hash', return_value="hashedpassword")
    @patch('services.user_services.is_valid_email', return_value=True)
    @patch('services.user_services.query.table')
    def test_register_user(self, mock_table, mock_is_valid_email, mock_get_password_hash, mock_is_valid_password,
                           mock_find_user_by_phone_number, mock_find_user_by_email):
        mock_insert = mock_table.return_value.insert.return_value.execute
        mock_insert.return_value.data = [{
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "phone_number": "1234567890",
            "created_at": "2024-06-01T00:00:00+00:00"
        }]

        response = self.client.post('/users/register', json=self.user_create_payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "phone_number": "1234567890",
            "created_at": "2024-06-01T00:00:00+00:00"
        })

    @patch('services.user_services.get_user_balance')
    @patch('common.authorization.verify_access_token')
    def test_get_account_balance(self, mock_verify_access_token, mock_get_user_balance):
        mock_verify_access_token.return_value = 1
        mock_get_user_balance.return_value = {'balance': 100}

        headers = {"Authorization": "Bearer testtoken"}

        response = self.client.get('/users/balance', headers=headers)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json(), {"balance": 100.0})

    @patch('services.user_services.try_login')
    @patch('routers.users.create_token')
    def test_try_login(self, mock_create_token, mock_try_login):
        mock_create_token.return_value = 'testtoken'
        mock_try_login.return_value = UserOut(
            id=1, username='testuser', email='test@test.test',
            phone_number='1234567890', created_at='2024-06-01T00:00:00+00:00'
        )

        user_login_payload = {
            "email": "test@test.test",
            "password": "TestPassword123!"
        }

        response = self.client.post('/users/login', json=user_login_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"access_token": 'testtoken', "token_type": "bearer"})

    @patch('common.authorization.verify_access_token')
    @patch('services.user_services.find_user_by_id')
    @patch('services.user_services.is_valid_password')
    @patch('services.user_services.get_password_hash')
    @patch('services.user_services.is_valid_email')
    @patch('services.user_services.query.table')
    def test_update_user(self, mock_query_table, mock_is_valid_email, mock_get_password_hash,
                         mock_is_valid_password,
                         mock_find_user_by_id, mock_verify_access_token):
        mock_find_user_by_id.return_value = GetUser(
            id=ID, username=USERNAME, password=PASSWORD,
            email=EMAIL, phone_number=PHONE_NUM, is_admin=IS_ADMIN,
            created_at=CREATED_AT, amount=AMOUNT, is_registered=IS_REGISTERED,
            is_blocked=IS_BLOCKED
        )
        mock_is_valid_email.return_value = True
        mock_is_valid_password.return_value = (True, "")
        mock_get_password_hash.return_value = "new_hashed_password"
        mock_verify_access_token.return_value = 1

        mock_update = MagicMock()
        mock_query_table.return_value.update.return_value.eq.return_value.execute = mock_update

        headers = {"Authorization": "Bearer testtoken"}

        response = self.client.put('/users/profile/update', json=self.update_profile_payload, headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Credentials updated!')

        mock_find_user_by_id.assert_called_once_with(ID)
        mock_get_password_hash.assert_called_once_with('NewPassword123!')
        mock_is_valid_password.assert_called_once_with('NewPassword123!')
        mock_is_valid_email.assert_called_once_with('newemail@example.com')
        mock_update.assert_called_once()

    @patch('common.authorization.verify_access_token')
    @patch('services.user_services.find_user_by_id')
    @patch('services.user_services.get_logged_user')
    def test_get_logged_user(self, mock_get_logged_user, mock_find_user_by_id, mock_verify_access_token):
        mock_verify_access_token.return_value = 1
        mock_find_user_by_id.return_value = GetUser(
            id=ID,
            username=USERNAME,
            password=PASSWORD,
            email=EMAIL,
            phone_number=PHONE_NUM,
            is_admin=IS_ADMIN,
            created_at=CREATED_AT,
            amount=AMOUNT,
            is_registered=IS_REGISTERED,
            is_blocked=IS_BLOCKED
        )

        mock_get_logged_user.return_value = UserOut(id=ID, username=USERNAME, email=EMAIL,
                                                    phone_number=PHONE_NUM, created_at=CREATED_AT)

        headers = {"Authorization": "Bearer testtoken"}

        response = self.client.get('/users/profile', headers=headers)

        self.assertIsInstance(mock_get_logged_user.return_value, UserOut)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'id': ID,
                                           'username': USERNAME,
                                           'email': EMAIL,
                                           'phone_number': PHONE_NUM,
                                           'created_at': CREATED_AT})

    @patch('common.authorization.verify_access_token')
    @patch('services.user_services.is_admin')
    @patch('services.user_services.find_user_by_email')
    @patch('services.user_services.confirm_user_registration')
    @patch('services.user_services.query.table')
    def test_confirm_user_registration(self, mock_query_table, mock_confirm_user_registration, mock_find_user_by_email,
                                       mock_is_admin, mock_verify_access_token):
        mock_verify_access_token.return_value = 1

        mock_is_admin.return_value = True

        mock_find_user_by_email.return_value = GetUser(
            id=ID, username=USERNAME, password=PASSWORD,
            email=EMAIL, phone_number=PHONE_NUM, is_admin=IS_ADMIN,
            created_at=CREATED_AT, amount=AMOUNT, is_registered=IS_REGISTERED,
            is_blocked=IS_BLOCKED)

        mock_confirm_user_registration.return_value = 'Successful'

        mock_update = MagicMock()
        mock_query_table.return_value.update.return_value.eq.return_value.execute = mock_update

        headers = {"Authorization": "Bearer testtoken"}

        payload = {'confirm': True}

        response = self.client.put(f'/users/confirm/{EMAIL}', headers=headers, json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Successful')

    @patch('services.user_services.query.table')
    @patch('common.authorization.verify_access_token')
    @patch('services.user_services.is_admin')
    @patch('services.user_services.find_user_by_id')
    def test_block_user(self, mock_find_user_by_id, mock_is_admin, mock_verify_access_token, mock_query_table):
        mock_verify_access_token.return_value = 1
        mock_is_admin.return_value = True
        mock_find_user_by_id.return_value = GetUser(
            id=ID, username=USERNAME, password=PASSWORD,
            email=EMAIL, phone_number=PHONE_NUM, is_admin=IS_ADMIN,
            created_at=CREATED_AT, amount=AMOUNT, is_registered=IS_REGISTERED,
            is_blocked=IS_BLOCKED)

        mock_update = MagicMock()
        mock_query_table.return_value.update.return_value.eq.return_value.execute = mock_update

        headers = {"Authorization": "Bearer testtoken"}

        payload = {'is_blocked': True}

        response = self.client.put(f'/users/block/{ID}', json=payload, headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), f'Block status: True set successfully!')
        mock_update.assert_called_once()


if __name__ == '__main__':
    unittest.main()
