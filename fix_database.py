import sqlite3

print("🔧 Starting enhanced database fix...")

# ✅ Replace this with your actual database file path
db_path = "instance/hotel_app.db"

# Currency mapping by country code
CURRENCY_MAP = {
    'US': '$',      # United States Dollar
    'GB': '£',      # British Pound
    'EU': '€',      # Euro (for EU countries)
    'DE': '€',      # Germany
    'FR': '€',      # France
    'IT': '€',      # Italy
    'ES': '€',      # Spain
    'NL': '€',      # Netherlands
    'BE': '€',      # Belgium
    'AT': '€',      # Austria
    'PT': '€',      # Portugal
    'IE': '€',      # Ireland
    'GR': '€',      # Greece
    'JP': '¥',      # Japanese Yen
    'CN': '¥',      # Chinese Yuan
    'KR': '₩',      # South Korean Won
    'IN': '₹',      # Indian Rupee
    'NG': '₦',      # Nigerian Naira
    'ZA': 'R',      # South African Rand
    'BR': 'R$',     # Brazilian Real
    'MX': '$',      # Mexican Peso
    'CA': 'C$',     # Canadian Dollar
    'AU': 'A$',     # Australian Dollar
    'NZ': 'NZ$',    # New Zealand Dollar
    'CH': 'CHF',    # Swiss Franc
    'SE': 'kr',     # Swedish Krona
    'NO': 'kr',     # Norwegian Krone
    'DK': 'kr',     # Danish Krone
    'PL': 'zł',     # Polish Zloty
    'RU': '₽',      # Russian Ruble
    'TR': '₺',      # Turkish Lira
    'SA': 'SR',     # Saudi Riyal
    'AE': 'د.إ',    # UAE Dirham
    'SG': 'S$',     # Singapore Dollar
    'HK': 'HK$',    # Hong Kong Dollar
    'TH': '฿',      # Thai Baht
    'MY': 'RM',     # Malaysian Ringgit
    'ID': 'Rp',     # Indonesian Rupiah
    'PH': '₱',      # Philippine Peso
    'VN': '₫',      # Vietnamese Dong
    'EG': 'E£',     # Egyptian Pound
    'KE': 'KSh',    # Kenyan Shilling
    'GH': 'GH₵',    # Ghanaian Cedi
    'AR': '$',      # Argentine Peso
    'CL': '$',      # Chilean Peso
    'CO': '$',      # Colombian Peso
    'PE': 'S/',     # Peruvian Sol
}

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("✅ Connected to database successfully\n")

    # ========================================
    # STEP 1: Add currency column to user table
    # ========================================
    print("💰 Adding 'currency' column to user table...")
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN currency VARCHAR(10) DEFAULT '$'")
        conn.commit()
        print("✅ Currency column added successfully!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("✅ Currency column already exists!")
        else:
            print(f"⚠️ Warning: {e}")

    # ========================================
    # STEP 2: Populate currency based on country
    # ========================================
    print("\n🌍 Populating currency based on user countries...")
    
    cursor.execute("SELECT id, country_code FROM user WHERE country_code IS NOT NULL")
    users = cursor.fetchall()
    
    updated_count = 0
    for user_id, country_code in users:
        if country_code in CURRENCY_MAP:
            currency = CURRENCY_MAP[country_code]
            cursor.execute("UPDATE user SET currency = ? WHERE id = ?", (currency, user_id))
            updated_count += 1
    
    conn.commit()
    print(f"✅ Updated currency for {updated_count} users based on their country")

    # ========================================
    # STEP 3: Rebuild user_hotel_assignment table
    # ========================================
    print("\n🚧 Rebuilding 'user_hotel_assignment' table with ON DELETE CASCADE...")

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

    # ========================================
    # STEP 4: Verify the changes
    # ========================================
    print("\n🔍 Verifying changes...")
    
    # Check if currency column exists
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    currency_exists = any(col[1] == 'currency' for col in columns)
    
    if currency_exists:
        print("✅ Currency column verified in user table")
    else:
        print("❌ Currency column NOT found in user table")
    
    # Show currency distribution
    cursor.execute("""
        SELECT currency, COUNT(*) as count 
        FROM user 
        GROUP BY currency 
        ORDER BY count DESC
    """)
    currency_dist = cursor.fetchall()
    
    print("\n📊 Currency distribution:")
    for currency, count in currency_dist:
        print(f"   {currency}: {count} users")
    
    # Check user_hotel_assignment table
    cursor.execute("PRAGMA foreign_key_list(user_hotel_assignment)")
    foreign_keys = cursor.fetchall()
    
    cascade_count = sum(1 for fk in foreign_keys if fk[6] == 'CASCADE')
    print(f"\n✅ Found {cascade_count} ON DELETE CASCADE constraints in user_hotel_assignment")
    
    # Count users
    cursor.execute("SELECT COUNT(*) FROM user")
    user_count = cursor.fetchone()[0]
    print(f"✅ Total users in database: {user_count}")
    
    print("\n🎉 Database migration completed successfully!")
    print("\n💡 Note: New users will automatically get currency based on their country")
    
except sqlite3.Error as e:
    print(f"❌ SQLite Error: {e}")
    if conn:
        conn.rollback()
        print("🔄 Changes rolled back")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    if conn:
        conn.rollback()
        print("🔄 Changes rolled back")
finally:
    if conn:
        conn.close()
        print("🔒 Database connection closed.")