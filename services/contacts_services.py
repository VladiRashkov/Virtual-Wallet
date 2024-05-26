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
    
    
def find_contact_by_attribute(logged_user_id: int, search_by_criteria: str, value: str):
    '''Find a user's contact by a specific attribute (phone number, username, or email).'''
    # Map the attribute to the corresponding column name in the 'users' table
    column_map = {
        'phone_number': 'phone_number',
        'username': 'username',
        'email': 'email'
    }
    column_name = column_map.get(search_by_criteria)
    if column_name:
        # Search for the contact using the specified attribute and value
        contact = query.table('contacts') \
            .select('contact_name_id') \
            .eq('current_user', logged_user_id) \
            .execute()
        
        if contact.data:
            contact_name_ids = [c['contact_name_id'] for c in contact.data]
            user = query.table('users') \
                .select('id', 'username', 'email', 'phone_number') \
                .in_('id', contact_name_ids) \
                .eq(column_name, value) \
                .execute().data
            return user[0] if user else None
    return None