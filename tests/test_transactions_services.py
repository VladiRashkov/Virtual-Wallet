import pytest
from fastapi import HTTPException, status
from unittest.mock import patch
from services.transactions_services import get_logged_user_transactions, \
transfer_money, deposit_money, withdraw_money, confirm_transaction, deny_transaction, \
edit_category
from data.helpers import ADMIN_ERROR, TRANSACTION_ERROR
from unittest.mock import patch, MagicMock
from data.schemas import AmountOut


class MockUser:
    def __init__(self, is_admin=False, is_blocked=False, amount=0.0):
        self.is_admin = is_admin
        self.is_blocked = is_blocked
        self.amount = amount

def test_get_logged_user_transactions_sent_transactions():
    with patch('services.transactions_services.query') as mock_query:
        mock_query.table().select().eq().execute.return_value.data = [{'id': 1, 'sender_id': 1, 'receiver_id': 2, 'created_at': '2024-06-05T12:00:00'}]
        transactions = get_logged_user_transactions(user_id=1, transaction_type='sent')
        assert isinstance(transactions, list)
        assert len(transactions) == 1

def test_get_logged_user_transactions_received_transactions():
    with patch('services.transactions_services.query') as mock_query:
        mock_query.table().select().eq().execute.return_value.data = [{'id': 1, 'sender_id': 2, 'receiver_id': 1, 'created_at': '2024-06-05T12:00:00'}]
        transactions = get_logged_user_transactions(user_id=1, transaction_type='received')
        assert isinstance(transactions, list)
        assert len(transactions) == 1

def test_get_logged_user_transactions_admin_error():
    with patch('services.transactions_services.is_admin') as mock_is_admin:
        mock_is_admin.return_value = True
        try:
            get_logged_user_transactions(user_id=1)
        except HTTPException as e:
            assert e.status_code == status.HTTP_403_FORBIDDEN

#transfer money tests
@pytest.mark.parametrize("sender_id, receiver_id, amount, category, expected_result", [
    (1, 2, 100.0, "General", ('Successful', 'inserted_transaction_id')),
])
def test_transfer_money_successful(sender_id, receiver_id, amount, category, expected_result):
    with patch('services.transactions_services.find_user_by_id') as mock_find_user_by_id, \
         patch('services.transactions_services.query') as mock_query:
        
        # Create separate mock objects for sender and receiver
        mock_sender = MagicMock()
        mock_sender.is_admin = False
        mock_sender.is_blocked = False
        mock_sender.amount = 150.0
        
        mock_receiver = MagicMock()
        mock_receiver.is_admin = False
        mock_receiver.is_blocked = False
        mock_receiver.amount = 50.0
        
        # Define the side effect function to return the correct mock object
        def find_user_by_id_side_effect(user_id):
            if user_id == sender_id:
                return mock_sender
            elif user_id == receiver_id:
                return mock_receiver
            return None
        
        mock_find_user_by_id.side_effect = find_user_by_id_side_effect
        
        # Mocking the query methods
        mock_query.table().update().execute.return_value = None
        mock_query.table().insert().execute.return_value = 'inserted_transaction_id'
        mock_query.table().select().eq().execute.return_value.data = []

        result = transfer_money(sender_id, receiver_id, amount, category)
        
        assert result == expected_result

# Sender is an admin
def test_transfer_money_sender_admin():
    with patch('services.transactions_services.find_user_by_id') as mock_find_user_by_id:
        mock_sender = mock_find_user_by_id.return_value
        mock_sender.is_admin = True
        
        with pytest.raises(HTTPException) as exc_info:
            transfer_money(1, 2, 100.0, "General")
        
        assert exc_info.value == ADMIN_ERROR

# Sender is blocked
def test_transfer_money_sender_blocked():
    with patch('services.transactions_services.find_user_by_id') as mock_find_user_by_id:
        mock_sender = mock_find_user_by_id.return_value
        mock_sender.is_admin = False
        mock_sender.is_blocked = True
        
        with pytest.raises(HTTPException) as exc_info:
            transfer_money(1, 2, 100.0, "General")
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

# Sender not found
def test_transfer_money_sender_not_found():
    with patch('services.transactions_services.find_user_by_id') as mock_find_user_by_id:
        mock_find_user_by_id.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            transfer_money(1, 2, 100.0, "General")
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

# Receiver not found
def test_transfer_money_receiver_not_found():
    with patch('services.transactions_services.find_user_by_id') as mock_find_user_by_id:
        mock_find_user_by_id.side_effect = [MockUser(), None]
        
        with pytest.raises(HTTPException) as exc_info:
            transfer_money(1, 2, 100.0, "General")
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

# Insufficient balance
def test_transfer_money_insufficient_balance():
    with patch('services.transactions_services.find_user_by_id') as mock_find_user_by_id:
        mock_sender = mock_find_user_by_id.return_value
        mock_sender.is_admin = False
        mock_sender.is_blocked = False
        mock_sender.amount = 50.0
        
        with pytest.raises(HTTPException) as exc_info:
            transfer_money(1, 2, 100.0, "General")
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

# Contact already exists
def test_transfer_money_contact_already_exists():
    with patch('services.transactions_services.find_user_by_id') as mock_find_user_by_id, \
         patch('services.transactions_services.query') as mock_query:
        
        # Create separate mock objects for sender and receiver
        mock_sender = MagicMock()
        mock_sender.is_admin = False
        mock_sender.is_blocked = False
        mock_sender.amount = 150.0
        
        mock_receiver = MagicMock()
        mock_receiver.is_admin = False
        mock_receiver.is_blocked = False
        mock_receiver.amount = 50.0
        
        # Define the side effect function to return the correct mock object
        def find_user_by_id_side_effect(user_id):
            if user_id == 1:
                return mock_sender
            elif user_id == 2:
                return mock_receiver
            return None
        
        mock_find_user_by_id.side_effect = find_user_by_id_side_effect
        
        # Mock the query methods
        mock_query.table().select().eq().execute.return_value.data = [{'current_user': 1, 'contact_name_id': 2}]
        mock_query.table().update().execute.return_value = None
        mock_query.table().insert().execute.return_value = 'inserted_transaction_id'
        
        result = transfer_money(1, 2, 100.0, "General")
        
        assert result == ('Successful', 'inserted_transaction_id')

# New contact
def test_transfer_money_new_contact():
    with patch('services.transactions_services.find_user_by_id') as mock_find_user_by_id, \
         patch('services.transactions_services.query') as mock_query:
        
        # Create separate mock objects for sender and receiver
        mock_sender = MagicMock()
        mock_sender.is_admin = False
        mock_sender.is_blocked = False
        mock_sender.amount = 150.0
        
        mock_receiver = MagicMock()
        mock_receiver.is_admin = False
        mock_receiver.is_blocked = False
        mock_receiver.amount = 50.0
        
        # Define the side effect function to return the correct mock object
        def find_user_by_id_side_effect(user_id):
            if user_id == 1:
                return mock_sender
            elif user_id == 2:
                return mock_receiver
            return None
        
        mock_find_user_by_id.side_effect = find_user_by_id_side_effect
        
        # Mock the query methods
        mock_query.table().select().eq().execute.return_value.data = []
        mock_query.table().update().execute.return_value = None
        mock_query.table().insert().execute.return_value = 'inserted_transaction_id'
        
        result = transfer_money(1, 2, 100.0, "General")
        
        assert result == ('Successful', 'inserted_transaction_id')
        
        
#deposit money
def test_deposit_money_admin_user():
    with patch('services.transactions_services.is_admin') as mock_is_admin:
        mock_is_admin.return_value = True
        
        with pytest.raises(Exception) as exc_info:
            deposit_money(100.0, 1)
        
        assert exc_info.value == ADMIN_ERROR
        
def test_deposit_money_non_positive_amount():
    with patch('services.transactions_services.is_admin') as mock_is_admin, \
         patch('services.transactions_services.get_account_balance') as mock_get_account_balance:
        mock_is_admin.return_value = False
        mock_get_account_balance.return_value = MagicMock(balance=100.0)
        
        with pytest.raises(HTTPException) as exc_info:
            deposit_money(0, 1)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == 'The deposit sum has to be a positive number!'


def test_deposit_money_successful():
    with patch('services.transactions_services.is_admin') as mock_is_admin, \
         patch('services.transactions_services.get_account_balance') as mock_get_account_balance, \
         patch('services.transactions_services.query') as mock_query:
        
        mock_is_admin.return_value = False
        mock_get_account_balance.return_value = MagicMock(balance=100.0)
        
        mock_query.table().update().eq().execute.return_value.data = [{"amount": 200.0}]
        mock_query.table().insert().execute.return_value = None
        
        result = deposit_money(100.0, 1)
        
        assert result == AmountOut(message="Balance updated!", old_balance=100.0, new_balance=200.0)


#withdraw money

def test_withdraw_money_admin_user():
    with patch('services.transactions_services.is_admin') as mock_is_admin:
        mock_is_admin.return_value = True
        
        with pytest.raises(Exception) as exc_info:
            withdraw_money(100.0, 1)
        
        assert exc_info.value == ADMIN_ERROR

def test_withdraw_money_non_positive_amount():
    with patch('services.transactions_services.is_admin') as mock_is_admin, \
         patch('services.transactions_services.get_account_balance') as mock_get_account_balance:
        mock_is_admin.return_value = False
        mock_get_account_balance.return_value = MagicMock(balance=100.0)
        
        with pytest.raises(HTTPException) as exc_info:
            withdraw_money(0, 1)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == 'The sum has to be a positive number'

def test_withdraw_money_insufficient_balance():
    with patch('services.transactions_services.is_admin') as mock_is_admin, \
         patch('services.transactions_services.get_account_balance') as mock_get_account_balance:
        mock_is_admin.return_value = False
        mock_get_account_balance.return_value = MagicMock(balance=50.0)
        
        with pytest.raises(HTTPException) as exc_info:
            withdraw_money(100.0, 1)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == 'Insufficient balance'

def test_withdraw_money_successful():
    with patch('services.transactions_services.is_admin') as mock_is_admin, \
         patch('services.transactions_services.get_account_balance') as mock_get_account_balance, \
         patch('services.transactions_services.query') as mock_query:
        
        mock_is_admin.return_value = False
        mock_get_account_balance.return_value = MagicMock(balance=150.0)
        
        mock_query.table().update().eq().execute.return_value.data = [{"amount": 50.0}]
        mock_query.table().insert().execute.return_value = None
        
        result = withdraw_money(100.0, 1)
        
        assert result == AmountOut(message="Balance updated!", old_balance=150.0, new_balance=50.0)

#confirm transactions

def test_confirm_transaction_admin_user():
    with patch('services.transactions_services.is_admin') as mock_is_admin:
        mock_is_admin.return_value = True
        
        with pytest.raises(Exception) as exc_info:
            confirm_transaction("confirm", 1, 1)
        
        assert exc_info.value == ADMIN_ERROR


def test_confirm_transaction_confirm():
    with patch('services.transactions_services.is_admin') as mock_is_admin, \
         patch('services.transactions_services.query') as mock_query, \
         patch('services.transactions_services.get_account_balance') as mock_get_account_balance:
        
        mock_is_admin.return_value = False
        mock_query.table().select().execute.return_value.data = [{'status': 'pending', 'amount': 100.0, 'sender_id': 1}]
        mock_get_account_balance.return_value = MagicMock(balance=200.0)
        
        mock_query.table().update().eq().execute.return_value = None
        
        result = confirm_transaction("confirm", 1, 1)
        
        assert result == 'Transaction with id: 1 was CONFIRMED!'

#deny
def test_deny_transaction_not_admin():
    with patch('services.transactions_services.is_admin') as mock_is_admin:
        mock_is_admin.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            deny_transaction(1, 1)
        
        assert exc_info.value.status_code == ADMIN_ERROR.status_code
        assert exc_info.value.detail == ADMIN_ERROR.detail
            
        

def test_deny_transaction_not_found():
    with patch('services.transactions_services.is_admin') as mock_is_admin, \
         patch('services.transactions_services.get_transaction') as mock_get_transaction:

        mock_is_admin.return_value = True
        mock_get_transaction.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            deny_transaction(1, 1)
        
        assert exc_info.value.status_code == TRANSACTION_ERROR.status_code
        assert exc_info.value.detail == TRANSACTION_ERROR.detail

def test_deny_transaction_not_confirmed():
    with patch('services.transactions_services.is_admin') as mock_is_admin, \
         patch('services.transactions_services.get_transaction') as mock_get_transaction:
        
        mock_is_admin.return_value = True
        mock_get_transaction.return_value = MagicMock(status='pending')

        with pytest.raises(HTTPException) as exc_info:
            deny_transaction(1, 1)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == 'You can deny only CONFIRMED by sender transactions!'

def test_deny_transaction_success():
    with patch('services.transactions_services.is_admin') as mock_is_admin, \
         patch('services.transactions_services.get_transaction') as mock_get_transaction, \
         patch('services.transactions_services.update_transaction') as mock_update_transaction:
        
        mock_is_admin.return_value = True
        mock_get_transaction.return_value = MagicMock(status='confirmed', acceptation='pending')
        mock_update_transaction.return_value = None

        result = deny_transaction(1, 1)

        assert result == 'Transaction is declined successfully!'
        mock_update_transaction.assert_called_once_with(1, {'acceptation': 'declined'})

def test_deny_transaction_already_declined():
    with patch('services.transactions_services.is_admin') as mock_is_admin, \
         patch('services.transactions_services.get_transaction') as mock_get_transaction, \
         patch('services.transactions_services.update_transaction') as mock_update_transaction:
        
        mock_is_admin.return_value = True
        mock_get_transaction.return_value = MagicMock(status='confirmed', acceptation='declined')

        result = deny_transaction(1, 1)

        assert result == 'Transaction is declined successfully!'
        mock_update_transaction.assert_not_called()
        
#edit

def test_edit_category_transaction_not_found():
    with patch('services.transactions_services.get_transaction') as mock_get_transaction:
        mock_get_transaction.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            edit_category(1, 'new_category', 1)
        
        assert exc_info.value.status_code == TRANSACTION_ERROR.status_code
        assert exc_info.value.detail == TRANSACTION_ERROR.detail

def test_edit_category_not_sender():
    with patch('services.transactions_services.get_transaction') as mock_get_transaction:
        mock_get_transaction.return_value = MagicMock(sender_id=2)

        with pytest.raises(HTTPException) as exc_info:
            edit_category(1, 'new_category', 1)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == 'You can edit only your OWN transaction!'

def test_edit_category_success():
    with patch('services.transactions_services.get_transaction') as mock_get_transaction, \
         patch('services.transactions_services.query') as mock_query:
        mock_get_transaction.return_value = MagicMock(sender_id=1)
        mock_query.table().update().eq().execute.return_value = MagicMock()

        result = edit_category(1, 'new_category', 1)

        assert result == 'Category was edited successfully!'
        mock_query.table().update().eq().execute.assert_called_once()
