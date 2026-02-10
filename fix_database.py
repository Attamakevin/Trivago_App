import sqlite3

print("🔧 Starting database fix...")

# ✅ Replace this with your actual database file path
db_path = "instance/hotel_app.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("✅ Connected to database successfully\n")

    print("🚧 Rebuilding 'user_hotel_assignment' table with ON DELETE CASCADE...")

    cursor.executescript("""
    PRAGMA foreign_keys=off;

    -- Step 1: Backup existing table
    CREATE TABLE IF NOT EXISTS user_hotel_assignment_backup AS
    SELECT * FROM user_hotel_assignment;

    -- Step 2: Drop old table
    DROP TABLE IF EXISTS user_hotel_assignment;

    -- Step 3: Recreate with ON DELETE CASCADE enabled
    CREATE TABLE user_hotel_assignment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        hotel_id INTEGER NOT NULL,
        session_type TEXT,
        custom_commission REAL,
        assigned_by INTEGER NOT NULL,
        created_at DATETIME,
        used BOOLEAN NOT NULL DEFAULT 0,
        used_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
        FOREIGN KEY (hotel_id) REFERENCES hotel (id) ON DELETE CASCADE,
        FOREIGN KEY (assigned_by) REFERENCES user (id)
    );

    -- Step 4: Restore data (ensure compatible columns)
    INSERT INTO user_hotel_assignment (
        id, user_id, hotel_id, session_type, custom_commission,
        assigned_by, created_at, used, used_at
    )
    SELECT
        id, user_id, hotel_id, session_type, custom_commission,
        assigned_by, created_at, used, used_at
    FROM user_hotel_assignment_backup;

    -- Step 5: Drop backup
    DROP TABLE user_hotel_assignment_backup;

    PRAGMA foreign_keys=on;
    """)

    conn.commit()
    print("✅ Table successfully rebuilt with ON DELETE CASCADE.")
    
except sqlite3.Error as e:
    print(f"❌ SQLite Error: {e}")
    conn.rollback()
finally:
    conn.close()
    print("🔒 Database connection closed.")
