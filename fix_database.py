# fix_database.py - Run this script to remove the unique constraint

import sqlite3
import os

# Path to your SQLite database (adjust this path)
db_path = 'instance/hotel_app.db'  # or whatever your database file is called

# Check if database exists
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    print("Please check your database path and update the db_path variable")
    exit(1)

try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Connected to database successfully")
    
    # Check current table structure
    cursor.execute("PRAGMA table_info(user_hotel_assignment)")
    columns = cursor.fetchall()
    print("Current table structure:")
    for col in columns:
        print(f"  {col}")
    
    # Check for existing unique constraints
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user_hotel_assignment'")
    table_def = cursor.fetchone()
    print(f"\nCurrent table definition: {table_def[0] if table_def else 'Not found'}")
    
    # Backup existing data
    cursor.execute("SELECT * FROM user_hotel_assignment")
    existing_data = cursor.fetchall()
    print(f"\nFound {len(existing_data)} existing records")
    
    # Create new table without unique constraint
    cursor.execute("""
        CREATE TABLE user_hotel_assignment_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            hotel_id TEXT NOT NULL,
            session_type TEXT NOT NULL,
            custom_commission REAL,
            assigned_by INTEGER NOT NULL,
            created_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES user (id),
            FOREIGN KEY (assigned_by) REFERENCES user (id)
        )
    """)
    
    # Copy data to new table
    if existing_data:
        cursor.execute("""
            INSERT INTO user_hotel_assignment_new 
            SELECT * FROM user_hotel_assignment
        """)
        print(f"Copied {len(existing_data)} records to new table")
    
    # Drop old table and rename new one
    cursor.execute("DROP TABLE user_hotel_assignment")
    cursor.execute("ALTER TABLE user_hotel_assignment_new RENAME TO user_hotel_assignment")
    
    # Commit changes
    conn.commit()
    print("Database updated successfully!")
    print("UNIQUE constraint removed from user_hotel_assignment table")
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
    conn.rollback()
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
        print("Database connection closed")

print("\nDone! You can now assign duplicate hotel assignments without constraint errors.")