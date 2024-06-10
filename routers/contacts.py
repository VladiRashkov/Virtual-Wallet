from fastapi import APIRouter, Depends, HTTPException, status
from common.authorization import get_current_user
from services.contacts_services import get_contacts_of_user, find_contact_by_attribute

router_contacts = APIRouter(prefix='/contacts')


@router_contacts.get('/', tags=['Contacts'])
def all_users_contacts(logged_user_id: int = Depends(get_current_user)): 
    '''Retrieve contact details for a given user.'''
    result = get_contacts_of_user(logged_user_id)
    return result

@router_contacts.get('/find', tags=['Contacts'])
def find_contact(logged_user_id:int = Depends(get_current_user), search: str = '', value: str = ''):
    '''Find a user's contact by a specific attribute (phone number, username, or email).'''
    contact = find_contact_by_attribute(logged_user_id, search, value)
    if contact:
        return contact
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found.')