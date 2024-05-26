from data.connection import query
from fastapi import HTTPException, status
from data.models import Contacts

def get_contacts_of_user(logged_user_id:int):
    all_contacts = query.table('contacts').select('*').eq('current_user',logged_user_id).execute()
    if all_contacts.data:
        return all_contacts
    else: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No contacts found!')
    