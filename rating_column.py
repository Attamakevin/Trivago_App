#!/usr/bin/env python3
"""
Debug version to troubleshoot column detection issues
"""

import os
import re
import sqlite3
import sys
from pathlib import Path

def debug_model_parsing(models_file="hotel_app/models.py"):
    """Debug model parsing to see what's being detected"""
    
    print("="*60)
    print("DEBUG: Model Parsing")
    print("="*60)
    
    if not Path(models_file).exists():
        print(f"❌ Models file not found: {models_file}")
        return
    
    with open(models_file, 'r') as f:
        content = f.read()
    
    print(f"📁 Reading from: {models_file}")
    print(f"📄 File size: {len(content)} characters")
    
    # Look for class definitions
    class_pattern = r'class\s+(\w+)\s*\(.*db\.Model.*\)'
    classes = re.findall(class_pattern, content)
    print(f"🔍 Found classes: {classes}")
    
    # Look for column definitions
    column_pattern = r'(\w+)\s*=\s*db\.Column\s*\([^)]*\)'
    columns = re.findall(column_pattern, content)
    print(f"🔍 Found columns: {columns}")
    
    # Show actual lines with db.Column
    lines = content.split('\n')
    column_lines = []
    for i, line in enumerate(lines, 1):
        if 'db.Column' in line:
            column_lines.append(f"Line {i}: {line.strip()}")
    
    print(f"\n📋 Lines with db.Column:")
    for line in column_lines:
        print(f"  {line}")
    
    return classes, columns

def debug_database_schema(db_path="instance/hotel_app.db"):
    """Debug database schema to see current structure"""
    
    print("\n" + "="*60)
    print("DEBUG: Database Schema")
    print("="*60)
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return {}
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    
    print(f"🗄️  Found tables: {[t[0] for t in tables]}")
    
    schema = {}
    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        schema[table_name] = {}
        print(f"\n📋 Table: {table_name}")
        for col_info in columns:
            col_name = col_info[1]
            col_type = col_info[2]
            schema[table_name][col_name] = col_info
            print(f"  - {col_name}: {col_type}")
    
    conn.close()
    return schema

def debug_differences(models_file="hotel_app/models.py", db_path="instance/hotel_app.db"):
    """Debug what differences are found"""
    
    print("\n" + "="*60)
    print("DEBUG: Finding Differences")
    print("="*60)
    
    # Simple model parsing for User class
    with open(models_file, 'r') as f:
        content = f.read()
    
    # Find User class columns
    user_section = re.search(r'class User\(.*?\):(.*?)(?=class|\Z)', content, re.DOTALL)
    if not user_section:
        print("❌ User class not found")
        return
    
    user_content = user_section.group(1)
    user_columns = re.findall(r'(\w+)\s*=\s*db\.Column', user_content)
    print(f"🔍 User model columns: {user_columns}")
    
    # Get database columns
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if user table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
    if not cursor.fetchone():
        print("❌ User table not found in database")
        conn.close()
        return
    
    cursor.execute("PRAGMA table_info(user)")
    db_columns = [col[1] for col in cursor.fetchall()]
    print(f"🗄️  Database user table columns: {db_columns}")
    
    # Find missing columns
    missing = set(user_columns) - set(db_columns)
    print(f"❌ Missing columns: {missing}")
    
    conn.close()
    return missing

def quick_fix_missing_columns(db_path="instance/hotel_app.db"):
    """Quick fix to add the missing location columns"""
    
    print("\n" + "="*60)
    print("QUICK FIX: Adding Missing Columns")
    print("="*60)
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    # Define the missing columns that are causing the error
    missing_columns = [
        "ALTER TABLE user ADD COLUMN ip_address TEXT;",
        "ALTER TABLE user ADD COLUMN country TEXT;",
        "ALTER TABLE user ADD COLUMN country_code TEXT;",
        "ALTER TABLE user ADD COLUMN region TEXT;",
        "ALTER TABLE user ADD COLUMN city TEXT;",
        "ALTER TABLE user ADD COLUMN latitude REAL;",
        "ALTER TABLE user ADD COLUMN longitude REAL;",
        "ALTER TABLE user ADD COLUMN timezone TEXT;",
        "ALTER TABLE user ADD COLUMN isp TEXT;",
        "ALTER TABLE user ADD COLUMN last_location_update DATETIME;"
    ]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current columns
        cursor.execute("PRAGMA table_info(user)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Add missing columns
        for sql in missing_columns:
            column_name = sql.split("ADD COLUMN ")[1].split()[0]
            if column_name not in existing_columns:
                print(f"Adding column: {column_name}")
                cursor.execute(sql)
            else:
                print(f"Column already exists: {column_name}")
        
        conn.commit()
        print("✅ Successfully added missing columns")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(user)")
        new_columns = [col[1] for col in cursor.fetchall()]
        print(f"New columns: {new_columns}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """Main debug function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "parse":
            debug_model_parsing()
        elif sys.argv[1] == "db":
            debug_database_schema()
        elif sys.argv[1] == "diff":
            debug_differences()
        elif sys.argv[1] == "fix":
            quick_fix_missing_columns()
        else:
            print("Usage: python debug_script.py [parse|db|diff|fix]")
    else:
        print("Running full debug...")
        debug_model_parsing()
        debug_database_schema()
        debug_differences()
        
        response = input("\nWould you like to apply the quick fix? (y/n): ")
        if response.lower() == 'y':
            quick_fix_missing_columns()

if __name__ == "__main__":
    main()