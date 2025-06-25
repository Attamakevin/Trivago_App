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
    
    # Check if commission tracking columns already exist in reservation table
    cursor.execute("PRAGMA table_info(reservation)")
    columns = [column[1] for column in cursor.fetchall()]
    
    print("Current reservation table columns:", columns)
    print()
    
    # Track what columns we're adding
    columns_added = []
    
    # Add commission_paid column if it doesn't exist
    if 'commission_paid' not in columns:
        cursor.execute("ALTER TABLE reservation ADD COLUMN commission_paid BOOLEAN DEFAULT 0")
        columns_added.append('commission_paid (BOOLEAN)')
        print("✓ commission_paid column added successfully!")
    else:
        print("✓ commission_paid column already exists!")
    
    # Add commission_paid_at column if it doesn't exist
    if 'commission_paid_at' not in columns:
        cursor.execute("ALTER TABLE reservation ADD COLUMN commission_paid_at DATETIME")
        columns_added.append('commission_paid_at (DATETIME)')
        print("✓ commission_paid_at column added successfully!")
    else:
        print("✓ commission_paid_at column already exists!")
    
    # Commit changes
    conn.commit()
    
    # Show what was added
    if columns_added:
        print(f"\n📝 Added {len(columns_added)} new columns:")
        for col in columns_added:
            print(f"   - {col}")
    else:
        print("\n📝 No new columns needed - all commission tracking columns already exist!")
    
    # Show updated table structure
    print("\n📋 Updated reservation table structure:")
    cursor.execute("PRAGMA table_info(reservation)")
    for column in cursor.fetchall():
        is_new = column[1] in ['commission_paid', 'commission_paid_at']
        indicator = "🆕" if is_new else "  "
        print(f"{indicator} {column[1]} ({column[2]}) - Default: {column[4] if column[4] else 'None'}")
    
    # Show current record count
    cursor.execute("SELECT COUNT(*) FROM reservation")
    record_count = cursor.fetchone()[0]
    print(f"\n📊 Total reservations in database: {record_count}")
    
    if record_count > 0:
        # Show sample of existing records (to verify the new columns)
        print("\n🔍 Sample of existing reservations (showing new columns):")
        cursor.execute("""
            SELECT id, user_id, status, commission_earned, 
                   commission_paid, commission_paid_at, timestamp
            FROM reservation 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        print("   ID | User | Status     | Commission | Paid | Paid At             | Created")
        print("   ---|------|------------|------------|------|---------------------|--------")
        for row in results:
            paid_status = "Yes" if row[4] else "No"
            paid_at = row[5] if row[5] else "Not paid"
            print(f"   {row[0]:2} | {row[1]:4} | {row[2]:10} | ${row[3]:8.2f} | {paid_status:4} | {paid_at:19} | {row[6]}")
    
except sqlite3.Error as e:
    print(f"❌ SQLite error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if conn:
        conn.close()

print("\n✅ Done! Your reservation table now has commission tracking columns.")
print("\n💡 Next steps:")
print("   1. Update your Reservation model to include these new fields")
print("   2. Use the updated reservation routes from the previous code")
print("   3. Test the commission tracking functionality")