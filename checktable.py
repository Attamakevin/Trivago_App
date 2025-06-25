import sqlite3
import os

# Database file path
db_path = 'instance/hotel_app.db'

# Check if database exists
if not os.path.exists(db_path):
    print(f"Database file '{db_path}' not found!")
    print("Current directory contents:")
    for file in os.listdir('.'):
        if file.endswith('.db'):
            print(f"  Found database: {file}")
    exit(1)

try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Show all tables
    print("Tables in database:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  {table[0]}")
    
    # Check hotel table structure
    print("\nHotel table structure:")
    cursor.execute("PRAGMA table_info(hotel)")
    columns = cursor.fetchall()
    
    if not columns:
        print("  Hotel table not found!")
    else:
        for column in columns:
            print(f"  {column[1]} ({column[2]}) - {column}")
    
    # Check if rating column exists
    column_names = [col[1] for col in columns]
    if 'rating' in column_names:
        print("\n✓ Rating column EXISTS")
    else:
        print("\n✗ Rating column MISSING")
        print("Adding rating column now...")
        cursor.execute("ALTER TABLE hotel ADD COLUMN rating REAL DEFAULT 0.0")
        conn.commit()
        print("✓ Rating column added!")
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()