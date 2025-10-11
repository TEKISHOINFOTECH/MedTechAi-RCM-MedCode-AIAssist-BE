from supabase import create_client
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------
# 1️⃣ INSERT data
# ---------------------------
data = {
    "name": "John smith",
    "email": "john.smith@example.com",
    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

insert_response = supabase.table("users").insert(data).execute()
print("✅ Insert Response:", insert_response.data)

# ---------------------------
# 2️⃣ FETCH (READ) data
# ---------------------------
fetch_response = supabase.table("users").select("*").eq("email", "john.doe1@example.com").execute()
print("📦 Fetch Response:", fetch_response.data)

# ---------------------------
# 3️⃣ UPDATE data
# ---------------------------
if fetch_response.data:
    user_id = fetch_response.data[0].get("id")  # assuming your table has a primary key "id"
    update_response = (
        supabase.table("users")
        .update({"name": "John Doe Updated"})
        .eq("id", user_id)
        .execute()
    )
    print("🔄 Update Response:", update_response.data)
else:
    print("⚠️ No user found to update.")
