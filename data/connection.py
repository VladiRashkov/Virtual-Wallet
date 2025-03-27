from supabase import create_client

# Supabase URL and Key
url = 'https://beviwnsnskrneunyxxzq.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJldml3bnNuc2tybmV1bnl4eHpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIxOTcxNDcsImV4cCI6MjA1Nzc3MzE0N30.5xykwrIHKWK7vomyEqh9Ifdl4h1g3wNRPFz5sR-qHZk'


# Create Supabase client
query = create_client(url, key)

