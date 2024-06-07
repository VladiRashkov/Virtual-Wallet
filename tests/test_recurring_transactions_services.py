import pytest
from unittest.mock import MagicMock
from services.recurring_transactions_services import create_recurring_transaction, update_recurring_transaction, delete_recurring_transaction
from datetime import datetime, timedelta
from data.schemas import CreateRecurringTransaction, UpdateRecurringTransaction


def test_create_recurring_transaction(monkeypatch):
    mock_query = MagicMock()
    mock_scheduler = MagicMock()
    
    monkeypatch.setattr('services.recurring_transactions_services.query', mock_query)
    monkeypatch.setattr('services.recurring_transactions_services.scheduler', mock_scheduler)
    
    mock_query.table.return_value.insert.return_value.execute.return_value.data = [{'id': 1}]
    
    sender_id = 1
    transaction = CreateRecurringTransaction(
        receiver_id=2,
        amount=100,
        recurring_time='daily'
    )
    
    result = create_recurring_transaction(sender_id, transaction)
    
    assert result == 'Recurring transaction created successfully'
    mock_query.table.assert_called_with('recurring_transactions')
    mock_scheduler.add_job.assert_called()
    
@pytest.fixture
def setup_mocks(monkeypatch):
    mock_query = MagicMock()
    monkeypatch.setattr('services.recurring_transactions_services.query', mock_query)
    
    mock_scheduler = MagicMock()
    monkeypatch.setattr('services.recurring_transactions_services.scheduler', mock_scheduler)
    
    return mock_query, mock_scheduler

def test_update_recurring_transaction_success(setup_mocks):
    mock_query, mock_scheduler = setup_mocks
    mock_query.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {'id': 1, 'sender_id': 1, 'receiver_id': 2, 'amount': 100, 'recurring_time': 'daily'}
    ]
    
    transaction_id = 1
    user_id = 1
    update_transaction = UpdateRecurringTransaction(
        receiver_id=3,
        amount=200,
        recurring_time='weekly',
        status='approved'
    )
    
    result = update_recurring_transaction(transaction_id, user_id, update_transaction)
    
    assert result == True
    mock_query.table.return_value.update.assert_called()
    mock_scheduler.add_job.assert_called()

def test_update_recurring_transaction_no_permission(setup_mocks):
    mock_query, _ = setup_mocks
    mock_query.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {'id': 1, 'sender_id': 2, 'receiver_id': 2, 'amount': 100, 'recurring_time': 'daily'}
    ]
    
    transaction_id = 1
    user_id = 1
    update_transaction = UpdateRecurringTransaction(
        receiver_id=3,
        amount=200,
        recurring_time='weekly',
        status='approved'
    )
    
    result = update_recurring_transaction(transaction_id, user_id, update_transaction)
    
    assert result == False
    


def test_delete_recurring_transaction_success(monkeypatch):
    mock_query = MagicMock()
    monkeypatch.setattr('services.recurring_transactions_services.query', mock_query)
    
    mock_query.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {'id': 1, 'sender_id': 1, 'receiver_id': 2, 'amount': 100, 'recurring_time': 'daily'}
    ]
    
    recurring_transaction_id = 1
    user_id = 1
    
    result = delete_recurring_transaction(recurring_transaction_id, user_id)
    
    assert result == True
    mock_query.table.return_value.delete.assert_called()

def test_delete_recurring_transaction_no_permission(monkeypatch):
    mock_query = MagicMock()
    monkeypatch.setattr('services.recurring_transactions_services.query', mock_query)
    
    mock_query.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {'id': 1, 'sender_id': 2, 'receiver_id': 2, 'amount': 100, 'recurring_time': 'daily'}
    ]
    
    recurring_transaction_id = 1
    user_id = 1
    
    result = delete_recurring_transaction(recurring_transaction_id, user_id)
    
    assert result == False
    mock_query.table.return_value.delete.assert_not_called()