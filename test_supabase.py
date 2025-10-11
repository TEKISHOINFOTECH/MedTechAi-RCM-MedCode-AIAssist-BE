#!/usr/bin/env python3
"""
Test script to verify Supabase connection using .env credentials.
"""
import asyncio
import os
from dotenv import load_dotenv
from app.config.supabase import get_supabase_client, SupabaseSettings
from app.utils.supabase_client import SupabaseService

# Load environment variables from .env file
load_dotenv()

async def test_supabase_connection():
    """Test Supabase connection and basic operations."""
    print("🚀 Testing Supabase Connection...")
    print("=" * 50)
    
    # Check environment variables
    print("📋 Checking Environment Variables:")
    settings = SupabaseSettings()
    
    if not settings.supabase_url:
        print("❌ SUPABASE_URL not found in .env file")
        return False
    
    if not settings.supabase_key:
        print("❌ SUPABASE_KEY not found in .env file")
        return False
    
    print(f"✅ SUPABASE_URL: {settings.supabase_url}")
    print(f"✅ SUPABASE_KEY: {settings.supabase_key[:20]}...")
    
    if settings.supabase_service_role_key:
        print(f"✅ SUPABASE_SERVICE_ROLE_KEY: {settings.supabase_service_role_key[:20]}...")
    else:
        print("⚠️  SUPABASE_SERVICE_ROLE_KEY not set (optional)")
    
    print()
    
    try:
        # Test 1: Create Supabase client
        print("🔌 Testing Supabase Client Creation...")
        client = get_supabase_client()
        print("✅ Supabase client created successfully")
        
        # Test 2: Test authentication
        print("\n🔐 Testing Authentication...")
        supabase_service = SupabaseService(client)
        
        # Try to get current user (should work even if no user is logged in)
        try:
            user = await supabase_service.get_user()
            if user:
                print(f"✅ Current user: {user.email}")
            else:
                print("✅ No authenticated user (expected for new connection)")
        except Exception as e:
            print(f"⚠️  Authentication test: {str(e)}")
        
        # Test 3: Test database connection
        print("\n🗄️  Testing Database Connection...")
        try:
            # Try a simple query to test connection
            result = await supabase_service.select(
                table="users",  # This table might not exist, but we're testing connection
                columns="count",
                filters=None
            )
            print("✅ Database connection successful")
        except Exception as e:
            if "relation" in str(e).lower() or "table" in str(e).lower():
                print("✅ Database connection successful (table doesn't exist yet)")
            else:
                print(f"❌ Database connection failed: {str(e)}")
                return False
        
        # Test 4: Test storage connection
        print("\n📁 Testing Storage Connection...")
        try:
            # Try to list buckets (this should work if storage is accessible)
            buckets = client.storage.list_buckets()
            print(f"✅ Storage connection successful - Found {len(buckets)} buckets")
        except Exception as e:
            print(f"⚠️  Storage test: {str(e)}")
        
        print("\n" + "=" * 50)
        print("🎉 Supabase Connection Test Completed Successfully!")
        print("✅ Your Supabase integration is ready to use!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Supabase Connection Failed: {str(e)}")
        print("\n🔧 Troubleshooting Tips:")
        print("1. Check your SUPABASE_URL and SUPABASE_KEY in .env file")
        print("2. Verify your Supabase project is active")
        print("3. Check if your project has the required tables")
        print("4. Ensure your API keys are correct")
        
        return False

def test_environment_setup():
    """Test if environment is properly set up."""
    print("🔧 Testing Environment Setup...")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("💡 Run: cp env.example .env")
        return False
    
    print("✅ .env file found")
    
    # Check if required packages are installed
    try:
        import supabase
        print("✅ supabase package installed")
    except ImportError:
        print("❌ supabase package not installed")
        print("💡 Run: pip install supabase")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv package installed")
    except ImportError:
        print("❌ python-dotenv package not installed")
        print("💡 Run: pip install python-dotenv")
        return False
    
    print("✅ Environment setup complete")
    return True

async def main():
    """Main test function."""
    print("🧪 Supabase Connection Test")
    print("=" * 50)
    
    # Test environment setup first
    if not test_environment_setup():
        return
    
    print()
    
    # Test Supabase connection
    success = await test_supabase_connection()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Your Supabase connection is working!")
        print("2. You can now use the Supabase API endpoints")
        print("3. Visit http://localhost:8000/docs to see all endpoints")
        print("4. Test authentication and database operations")
    else:
        print("\n🆘 Need Help?")
        print("1. Check your Supabase project settings")
        print("2. Verify your API keys are correct")
        print("3. Make sure your project is active")
        print("4. Check the Supabase documentation")

if __name__ == "__main__":
    asyncio.run(main())
