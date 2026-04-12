"""
Database Migration Script
Run this once to add missing columns to existing database
"""

import sqlite3
import os

def migrate_database():
    """Add missing columns to users table"""
    
    # Database file path
    db_path = os.path.join('instance', 'database.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file not found at:", db_path)
        print("👉 Just restart the app, it will create a new database")
        return
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    print(f"📊 Existing columns: {columns}")
    
    # Columns to add
    new_columns = {
        'avatar': 'VARCHAR(255)',
        'city': 'VARCHAR(100)',
        'education': 'VARCHAR(255)',
        'institution': 'VARCHAR(255)',
        'field_of_study': 'VARCHAR(255)',
        'graduation_year': 'INTEGER',
        'bio': 'TEXT',
        'phone': 'VARCHAR(20)',
        'website': 'VARCHAR(255)',
        'linkedin': 'VARCHAR(255)',
        'twitter': 'VARCHAR(255)',
        'github': 'VARCHAR(255)',
        'updated_at': 'DATETIME',
        'email_verified': 'BOOLEAN DEFAULT 0',
        'email_verified_at': 'DATETIME'
    }
    
    # Add missing columns
    added = 0
    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added column: {col_name}")
                added += 1
            except Exception as e:
                print(f"❌ Error adding {col_name}: {e}")
    
    conn.commit()
    conn.close()
    
    if added == 0:
        print("✅ No new columns needed - database is up to date")
    else:
        print(f"✅ Migration complete! Added {added} new columns")

if __name__ == "__main__":
    print("=" * 50)
    print("Database Migration Tool")
    print("=" * 50)
    migrate_database()
    print("\n👉 Now restart your Flask app: python app.py")