import pytest
from unittest.mock import MagicMock, patch
from data.connection import query as supabase
from services.cards_services import create_card, get_all_cards, get_card_by_id, update_card, delete_card

def test_create_card():
    with patch.object(supabase, 'table', return_value=MagicMock()) as mock_table:
        mock_response = MagicMock()
        mock_response.data = [{'id': 1, 'name': 'Test Card'}]
        mock_table.return_value.insert.return_value.execute.return_value = mock_response
        result = create_card({'name': 'Test Card'})
        assert result == {'id': 1, 'name': 'Test Card'}

def test_create_card_empty_data():
    with patch.object(supabase, 'table', return_value=MagicMock()) as mock_table:
        mock_response = MagicMock()
        mock_response.data = None
        mock_response.json.return_value = {'error': 'Insert error'}
        mock_table.return_value.insert.return_value.execute.return_value = mock_response
        with pytest.raises(Exception):
            create_card({})

def test_get_all_cards():
    with patch.object(supabase, 'table', return_value=MagicMock()) as mock_table:
        mock_response = MagicMock()
        mock_response.data = [{'id': 1, 'name': 'Test Card'}]
        mock_table.return_value.select.return_value.execute.return_value = mock_response
        result = get_all_cards()
        assert result == [{'id': 1, 'name': 'Test Card'}]

def test_get_all_cards_empty():
    with patch.object(supabase, 'table', return_value=MagicMock()) as mock_table:
        mock_response = MagicMock()
        mock_response.data = None
        mock_response.json.return_value = {'error': 'No cards found'}
        mock_table.return_value.select.return_value.execute.return_value = mock_response
        with pytest.raises(Exception):
            get_all_cards()

def test_get_card_by_id():
    with patch.object(supabase, 'table', return_value=MagicMock()) as mock_table:
        mock_response = MagicMock()
        mock_response.data = [{'id': 1, 'name': 'Test Card'}]
        mock_table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        result = get_card_by_id(1)
        assert result == {'id': 1, 'name': 'Test Card'}

def test_get_card_by_id_invalid():
    with patch.object(supabase, 'table', return_value=MagicMock()) as mock_table:
        mock_response = MagicMock()
        mock_response.data = []
        mock_response.json.return_value = {'error': 'Card not found'}
        mock_table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        with pytest.raises(Exception):
            get_card_by_id(999)

def test_update_card():
    with patch.object(supabase, 'table', return_value=MagicMock()) as mock_table:
        mock_response = MagicMock()
        mock_response.data = [{'id': 1, 'name': 'Updated Card'}]
        mock_table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        result = update_card(1, {'name': 'Updated Card'})
        assert result == {'id': 1, 'name': 'Updated Card'}

def test_update_card_invalid():
    with patch.object(supabase, 'table', return_value=MagicMock()) as mock_table:
        mock_response = MagicMock()
        mock_response.data = None
        mock_response.json.return_value = {'error': 'Update error'}
        mock_table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        with pytest.raises(Exception):
            update_card(999, {'name': 'Invalid Update'})

def test_delete_card():
    with patch.object(supabase, 'table', return_value=MagicMock()) as mock_table:
        mock_response = MagicMock()
        mock_response.data = [{'id': 1, 'name': 'Deleted Card'}]
        mock_table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_response
        result = delete_card(1)
        assert result == {'id': 1, 'name': 'Deleted Card'}

def test_delete_card_invalid():
    with patch.object(supabase, 'table', return_value=MagicMock()) as mock_table:
        mock_response = MagicMock()
        mock_response.data = None
        mock_response.json.return_value = {'error': 'Delete error'}
        mock_table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_response
        with pytest.raises(Exception):
            delete_card(999)
