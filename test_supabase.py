
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not url or not key:
    raise ValueError("Supabase URL or publishable key is missing from .env")

supabase = create_client(url, key)

response = supabase.table("search_history").select("id").limit(1).execute()

print("Supabase connection successful!")
print("Search history table is accessible.")
print("Rows returned:", len(response.data))
