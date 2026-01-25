"""
Database migration script to add profile fields to User table.
Run this to add username, bio, avatar_url, and settings columns.
"""
import sqlite3
import os

# Path to your database
DB_PATH = "app.db"

def migrate_database():
    print("=" * 60)
    print("DATABASE MIGRATION: Adding Profile Fields")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"✗ Database file not found: {DB_PATH}")
        print("  The database will be created automatically when you start the backend.")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"\nCurrent columns in 'users' table: {columns}")
        
        # Add missing columns
        columns_to_add = {
            'username': 'TEXT',
            'bio': 'TEXT',
            'avatar_url': 'TEXT',
            'settings': 'TEXT DEFAULT "{}"'
        }
        
        added_count = 0
        for column_name, column_type in columns_to_add.items():
            if column_name not in columns:
                print(f"\n✓ Adding column: {column_name} ({column_type})")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                added_count += 1
            else:
                print(f"  - Column '{column_name}' already exists, skipping")
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        if added_count > 0:
            print(f"✓ SUCCESS: Added {added_count} new column(s) to users table!")
            print("  You can now restart the backend server.")
        else:
            print("✓ All columns already exist. No migration needed.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_database()
