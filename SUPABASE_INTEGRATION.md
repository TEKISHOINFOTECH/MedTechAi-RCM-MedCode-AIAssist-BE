# 🚀 Supabase Integration Guide

This guide explains how to integrate and use Supabase with the MedTechAI RCM Assistant application.

---

## 📋 **Overview**

The application now includes comprehensive Supabase integration with:
- **Authentication** (sign up, sign in, sign out)
- **Database operations** (CRUD operations)
- **File storage** (upload, download, delete files)
- **Real-time subscriptions** (coming soon)

---

## 🔧 **Setup Instructions**

### 1. **Install Dependencies**

The Supabase Python client is already included in `requirements.txt`:
```bash
pip install supabase>=2.0.0
```

### 2. **Configure Environment Variables**

Add these variables to your `.env` file:

```env
# Supabase Project URL (Required)
SUPABASE_URL=https://your-project-id.supabase.co

# Supabase Anon Key (Required)
SUPABASE_KEY=your-supabase-anon-key-here

# Supabase Service Role Key (Optional - for admin operations)
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key-here

# Supabase JWT Secret (Optional - for token verification)
SUPABASE_JWT_SECRET=your-supabase-jwt-secret-here
```

### 3. **Get Your Supabase Credentials**

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **Settings** → **API**
4. Copy the following:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_KEY`
   - **service_role** key → `SUPABASE_SERVICE_ROLE_KEY`
   - **JWT Secret** → `SUPABASE_JWT_SECRET`

---

## 🎯 **API Endpoints**

### **Authentication**

#### Sign Up
```http
POST /supabase/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "user_metadata": {
    "name": "John Doe",
    "role": "user"
  }
}
```

#### Sign In
```http
POST /supabase/auth/signin
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Sign Out
```http
POST /supabase/auth/signout
```

#### Get Current User
```http
GET /supabase/auth/user
```

### **Database Operations**

#### Insert Data
```http
POST /supabase/db/insert
Content-Type: application/json

{
  "table": "users",
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
  }
}
```

#### Select Data
```http
POST /supabase/db/select
Content-Type: application/json

{
  "table": "users",
  "columns": "*",
  "filters": {
    "age": {"gte": 18}
  }
}
```

#### Update Data
```http
PUT /supabase/db/update
Content-Type: application/json

{
  "table": "users",
  "data": {
    "age": 31
  },
  "filters": {
    "email": "john@example.com"
  }
}
```

#### Delete Data
```http
DELETE /supabase/db/delete
Content-Type: application/json

{
  "table": "users",
  "filters": {
    "email": "john@example.com"
  }
}
```

### **File Storage**

#### Get Public URL
```http
GET /supabase/storage/public-url/{bucket}/{file_path}
```

### **Health Check**
```http
GET /supabase/health
```

---

## 💻 **Usage Examples**

### **Python Client Usage**

```python
from app.utils.supabase_client import get_supabase_service

# Get service instance
supabase = await get_supabase_service()

# Sign up a user
user_data = await supabase.sign_up(
    email="user@example.com",
    password="securepassword",
    user_metadata={"name": "John Doe"}
)

# Insert data
result = await supabase.insert(
    table="users",
    data={"name": "Jane Doe", "email": "jane@example.com"}
)

# Select data
users = await supabase.select(
    table="users",
    columns="name, email",
    filters={"age": {"gte": 18}}
)

# Upload file
with open("document.pdf", "rb") as f:
    file_data = f.read()
    
upload_result = await supabase.upload_file(
    bucket="documents",
    file_path="user-docs/document.pdf",
    file_data=file_data,
    content_type="application/pdf"
)
```

### **FastAPI Dependency Injection**

```python
from fastapi import Depends
from app.utils.supabase_client import get_supabase_service

@app.get("/my-endpoint")
async def my_endpoint(
    supabase: SupabaseService = Depends(get_supabase_service)
):
    # Use supabase client here
    user = await supabase.get_user()
    return {"user": user}
```

---

## 🗄️ **Database Schema Examples**

### **Users Table**
```sql
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  age INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **Medical Codes Table**
```sql
CREATE TABLE medical_codes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  code VARCHAR(50) NOT NULL,
  description TEXT,
  category VARCHAR(100),
  user_id UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🔒 **Security Best Practices**

1. **Environment Variables**: Never commit Supabase keys to version control
2. **Row Level Security**: Enable RLS on your tables
3. **API Keys**: Use anon key for client-side, service role for server-side
4. **Authentication**: Always verify user authentication for sensitive operations
5. **Validation**: Validate all input data before database operations

### **Example RLS Policy**
```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data
CREATE POLICY "Users can view own data" ON users
  FOR SELECT USING (auth.uid() = id);

-- Policy: Users can only update their own data
CREATE POLICY "Users can update own data" ON users
  FOR UPDATE USING (auth.uid() = id);
```

---

## 🚨 **Error Handling**

The Supabase service includes comprehensive error handling:

```python
try:
    result = await supabase.insert(table="users", data=user_data)
except Exception as e:
    # Handle specific errors
    if "duplicate key" in str(e):
        return {"error": "User already exists"}
    else:
        return {"error": f"Database error: {str(e)}"}
```

---

## 📊 **Monitoring and Logging**

Monitor your Supabase usage:
1. **Dashboard**: Check Supabase dashboard for usage metrics
2. **Logs**: Monitor application logs for Supabase operations
3. **Health Check**: Use `/supabase/health` endpoint for monitoring

---

## 🔄 **Next Steps**

1. **Set up your Supabase project**
2. **Configure environment variables**
3. **Create your database tables**
4. **Test the API endpoints**
5. **Implement authentication in your frontend**
6. **Add real-time subscriptions** (coming soon)

---

## 📚 **Additional Resources**

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase/supabase-py)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## 🆘 **Troubleshooting**

### **Common Issues**

1. **Connection Error**: Check your `SUPABASE_URL` and `SUPABASE_KEY`
2. **Authentication Error**: Verify user credentials and RLS policies
3. **Permission Error**: Check if service role key is needed for admin operations
4. **File Upload Error**: Ensure bucket exists and has proper permissions

### **Debug Mode**

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

This will show detailed Supabase operation logs.

---

## ✅ **Success Indicators**

- ✅ Supabase client connects successfully
- ✅ Authentication endpoints work
- ✅ Database operations complete without errors
- ✅ File storage operations work
- ✅ Health check returns healthy status

Your Supabase integration is now ready to use! 🎉
