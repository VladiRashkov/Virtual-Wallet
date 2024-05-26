from data.connection import query
from fastapi import HTTPException, status

def get_contacts_of_user(logged_user_id:int):
    '''Retrieve contact details for a given user.'''
    all_contacts = query.table('contacts').select('*').eq('current_user',logged_user_id).execute()
    contacts_details = []
    if all_contacts.data:
        for contact in all_contacts.data:
            
            contact_name_id = contact['contact_name_id']
            contacts_details.append(query.table('users')
                                    .select('username', 'email', 'phone_number')
                                    .eq('id',contact_name_id)
                                    .execute().data[0])
            
        return contacts_details
        
    else: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No contacts found!')
    