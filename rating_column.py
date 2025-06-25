import sqlite3
import os

# Database file path
db_path = 'instance/hotel_app.db'

# Check if database exists
if not os.path.exists(db_path):
    print(f"Database file '{db_path}' not found!")
    print("Please make sure you're in the correct directory.")
    exit(1)

try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if rating column already exists
    cursor.execute("PRAGMA table_info(hotel)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'rating' in columns:
        print("Rating column already exists!")
    else:
        # Add the rating column
        cursor.execute("ALTER TABLE hotel ADD COLUMN rating REAL DEFAULT 0.0")
        print("Rating column added successfully!")
        
        # Optionally, you can set some default ratings for existing hotels
        # cursor.execute("UPDATE hotel SET rating = 4.0 WHERE rating IS NULL")
        
    # Commit changes
    conn.commit()
    
    # Show current table structure
    print("\nCurrent hotel table structure:")
    cursor.execute("PRAGMA table_info(hotel)")
    for column in cursor.fetchall():
        print(f"  {column[1]} ({column[2]})")
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()

print("\nDone!")