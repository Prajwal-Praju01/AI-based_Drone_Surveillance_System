"""
Initialize authentication tables and default users
Run this script once to set up authentication
"""

from database import get_database_manager
from auth import init_default_users

def main():
    print("🔐 Initializing Authentication System...")
    print("=" * 60)
    
    try:
        # Get database manager
        db_manager = get_database_manager()
        print("✅ Database connection established")
        
        # Initialize users
        init_default_users(db_manager)
        
        print("=" * 60)
        print("✅ Authentication system initialized successfully!")
        print("\nDefault users created:")
        print("  • admin/admin123 (Administrator)")
        print("  • operator/operator123 (Operator)")
        print("  • viewer/viewer123 (Viewer)")
        print("\n⚠️  CHANGE THESE PASSWORDS IN PRODUCTION!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
