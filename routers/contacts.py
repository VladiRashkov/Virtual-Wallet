from fastapi import APIRouter, Depends, HTTPException
from data.models import Contacts
from common.authorization import get_current_user
from services.contacts_services import get_contacts_of_user

router_contacts = APIRouter(prefix='/contacts')


@router_contacts.get('/')
def all_users_contacts(logged_user_id: int = Depends(get_current_user)): 
    result = get_contacts_of_user(logged_user_id)
    return result.data