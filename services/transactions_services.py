from data.connection import supabase_data

def all_user_transations(sender_id:int):
    data = supabase_data.table('transactions').select('*').eq('sender_id', sender_id).execute()
    
    return data

def transfer_money(sender_id:int, receiver_id:int, amount:float): # token
    sender = supabase_data.table('users').select('amount').eq('id', sender_id).execute()
    receiver = supabase_data.table('users').select('amount').eq('id', receiver_id).execute()
    
   
    sender_data = sender.data
    receiver_data = receiver.data

    if not sender_data or not receiver_data:
        return "Error: Sender or receiver not found"
    
    sender_balance = sender_data[0]['amount']
    receiver_balance = receiver_data[0]['amount']

    if sender_balance < amount:
        return 'Insufficient balance'
    
    new_sender_balance = sender_balance-amount
    new_receiver_balance = receiver_balance+amount
    
    supabase_data.table('users').update({'amount': new_sender_balance}).eq('id', sender_id).execute()
    supabase_data.table('users').update({'amount': new_receiver_balance}).eq('id', receiver_id).execute()
    
    transaction_data = {
        'sender_id':sender_id,
        'receiver_id':receiver_id,
        'amount': amount
    }
    
    supabase_data.table('transactions').insert(transaction_data).execute()
    
    return 'Successful'
