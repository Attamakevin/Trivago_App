import sqlite3
import os
import re
from datetime import datetime

# Database file path
db_path = 'instance/hotel_app.db'
file_path = 'hotel_app/models.py'

def parse_models_file_improved(file_path):
    """
    Improved parser that handles more Flask-SQLAlchemy patterns
    """
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    models = {}
    current_class = None
    current_table = None
    current_columns = []
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        # Look for class definitions - more flexible patterns
        class_patterns = [
            r'class\s+(\w+)\s*\(.*db\.Model.*\)',      # db.Model
            r'class\s+(\w+)\s*\(.*Model.*\)',          # Model
            r'class\s+(\w+)\s*\(.*Base.*\)',           # Base
            r'class\s+(\w+)\s*\(.*SQLAlchemy.*\)',     # SQLAlchemy
        ]
        
        for pattern in class_patterns:
            class_match = re.match(pattern, line)
            if class_match:
                # Save previous class if exists
                if current_class and current_columns:
                    table_name = current_table or current_class.lower() + 's'
                    models[table_name] = current_columns
                
                current_class = class_match.group(1)
                current_table = None
                current_columns = []
                break
        
        # Look for __tablename__
        if current_class and '__tablename__' in line:
            table_match = re.search(r'__tablename__\s*=\s*[\'"](\w+)[\'"]', line)
            if table_match:
                current_table = table_match.group(1)
                continue
        
        # Look for column definitions - more flexible patterns
        column_patterns = [
            r'(\w+)\s*=\s*db\.Column',     # db.Column
            r'(\w+)\s*=\s*Column',         # Column (imported directly)
        ]
        
        if current_class:
            for pattern in column_patterns:
                if re.search(pattern, line):
                    column_info = parse_column_definition_improved(line)
                    if column_info:
                        current_columns.append(column_info)
                    break
    
    # Don't forget the last class
    if current_class and current_columns:
        table_name = current_table or current_class.lower() + 's'
        models[table_name] = current_columns
    
    return models

def parse_column_definition_improved(line):
    """
    Improved column parser that handles more patterns
    """
    try:
        # Extract column name (variable name before =)
        name_match = re.match(r'\s*(\w+)\s*=', line)
        if not name_match:
            return None
        
        column_name = name_match.group(1)
        
        # Skip special columns
        if column_name in ['id', '__tablename__', '__table_args__']:
            return None
        
        # Extract column type with more flexible patterns
        column_type = 'TEXT'  # default
        
        type_patterns = [
            (r'(db\.)?Integer', 'INTEGER'),
            (r'(db\.)?String\((\d+)\)', lambda m: f'VARCHAR({m.group(2)})'),
            (r'(db\.)?String', 'VARCHAR(255)'),
            (r'(db\.)?Text', 'TEXT'),
            (r'(db\.)?Boolean', 'BOOLEAN'),
            (r'(db\.)?DateTime', 'DATETIME'),
            (r'(db\.)?Date', 'DATE'),
            (r'(db\.)?Time', 'TIME'),
            (r'(db\.)?Float', 'REAL'),
            (r'(db\.)?Numeric', 'NUMERIC'),
        ]
        
        for pattern, sql_type in type_patterns:
            match = re.search(pattern, line)
            if match:
                if callable(sql_type):
                    column_type = sql_type(match)
                else:
                    column_type = sql_type
                break
        
        # Check for nullable=False
        nullable = 'nullable=False' not in line
        
        # Check for default values
        default_value = None
        if 'default=' in line:
            default_match = re.search(r'default=([^,)]+)', line)
            if default_match:
                default_val = default_match.group(1).strip()
                if default_val.startswith("'") or default_val.startswith('"'):
                    default_value = default_val
                elif default_val in ['True', 'False']:
                    default_value = '1' if default_val == 'True' else '0'
                elif default_val.replace('.','').replace('-','').isdigit():
                    default_value = default_val
                elif 'datetime' in default_val.lower() or 'now' in default_val.lower():
                    default_value = 'CURRENT_TIMESTAMP'
        
        return {
            'column': column_name,
            'type': column_type,
            'nullable': nullable,
            'default': default_value
        }
    
    except Exception as e:
        print(f"⚠️  Could not parse column from line: {line[:50]}...")
        return None
def parse_column_definition(line):
    """
    Parse a db.Column definition line and extract column information
    """
    try:
        # Extract column name (variable name before =)
        name_match = re.match(r'\s*(\w+)\s*=', line)
        if not name_match:
            return None
        
        column_name = name_match.group(1)
        
        # Skip special columns
        if column_name in ['id', '__tablename__', '__table_args__']:
            return None
        
        # Extract column type
        column_type = 'TEXT'  # default
        default_value = None
        nullable = True
        
        # Common type mappings
        if 'db.Integer' in line or 'Integer' in line:
            column_type = 'INTEGER'
        elif 'db.String' in line or 'String' in line:
            # Extract length if specified
            length_match = re.search(r'String\((\d+)\)', line)
            if length_match:
                column_type = f'VARCHAR({length_match.group(1)})'
            else:
                column_type = 'VARCHAR(255)'
        elif 'db.Text' in line or 'Text' in line:
            column_type = 'TEXT'
        elif 'db.Boolean' in line or 'Boolean' in line:
            column_type = 'BOOLEAN'
        elif 'db.DateTime' in line or 'DateTime' in line:
            column_type = 'DATETIME'
        elif 'db.Date' in line or 'Date' in line:
            column_type = 'DATE'
        elif 'db.Time' in line or 'Time' in line:
            column_type = 'TIME'
        elif 'db.Float' in line or 'Float' in line:
            column_type = 'REAL'
        elif 'db.Numeric' in line or 'Numeric' in line:
            column_type = 'NUMERIC'
        
        # Check for nullable=False
        if 'nullable=False' in line:
            nullable = False
        
        # Check for default values
        if 'default=' in line:
            default_match = re.search(r'default=([^,)]+)', line)
            if default_match:
                default_val = default_match.group(1).strip()
                if default_val.startswith("'") or default_val.startswith('"'):
                    default_value = default_val
                elif default_val == 'True':
                    default_value = '1'
                elif default_val == 'False':
                    default_value = '0'
                elif default_val.replace('.','').isdigit():
                    default_value = default_val
                elif 'datetime' in default_val.lower() or 'now' in default_val.lower():
                    default_value = 'CURRENT_TIMESTAMP'
        
        return {
            'column': column_name,
            'type': column_type,
            'nullable': nullable,
            'default': default_value
        }
    
    except Exception as e:
        print(f"⚠️  Could not parse column from line: {line[:50]}...")
        return None

def get_existing_tables(cursor):
    """Get all existing tables in the database"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    return [table[0] for table in cursor.fetchall()]

def get_table_columns(cursor, table_name):
    """Get current columns for a table"""
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [column[1] for column in cursor.fetchall()]
    except sqlite3.Error:
        return []

def add_column_if_not_exists(cursor, table_name, column_info):
    """Add column to table if it doesn't exist"""
    column_name = column_info['column']
    column_type = column_info['type']
    default_value = column_info['default']
    nullable = column_info.get('nullable', True)
    
    columns = get_table_columns(cursor, table_name)
    
    if column_name not in columns:
        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        
        if not nullable and default_value:
            alter_query += f" NOT NULL DEFAULT {default_value}"
        elif default_value:
            alter_query += f" DEFAULT {default_value}"
        
        try:
            cursor.execute(alter_query)
            return True
        except sqlite3.Error as e:
            print(f"⚠️  Could not add column {column_name}: {e}")
            return False
    return False

# Main execution
print("🔧 SAFE DATABASE UPDATE SCRIPT")
print("=" * 50)

# Look for models file
models_paths = [
    'models.py',
    'app/models.py',
    'hotel_app/models.py',
    'src/models.py'
]

models_file = None
for path in models_paths:
    if os.path.exists(path):
        models_file = path
        break

if not models_file:
    print("❌ Could not find models.py file in common locations!")
    print("Available files in current directory:")
    for item in os.listdir('.'):
        if item.endswith('.py'):
            print(f"  - {item}")
    
    models_file = input("\nEnter the path to your models file: ").strip()
    if not os.path.exists(models_file):
        print("❌ File not found!")
        exit(1)

print(f"📁 Using models file: {models_file}")

# Check database
if not os.path.exists(db_path):
    print(f"❌ Database not found: {db_path}")
    exit(1)

try:
    # Parse models file
    print("\n🔍 Parsing models file...")
    discovered_models = parse_models_file_improved('hotel_app/models.py')
    
    if not discovered_models:
        print("❌ No models found! Check your models.py file format.")
        exit(1)
    
    print(f"✓ Found {len(discovered_models)} models:")
    for table_name, columns in discovered_models.items():
        print(f"  - {table_name} ({len(columns)} columns)")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get existing tables
    existing_tables = get_existing_tables(cursor)
    print(f"\n📊 Database has {len(existing_tables)} tables: {', '.join(existing_tables)}")
    
    print(f"\n🔄 Starting updates...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    total_changes = 0
    
    # Process each model
    for table_name, columns in discovered_models.items():
        if table_name not in existing_tables:
            print(f"⚠️  Table '{table_name}' not found in database - skipping")
            continue
        
        print(f"\n🏷️  Processing table: {table_name}")
        columns_added = 0
        
        for column_info in columns:
            if add_column_if_not_exists(cursor, table_name, column_info):
                nullable_str = "NULL" if column_info.get('nullable', True) else "NOT NULL"
                default_str = f" DEFAULT {column_info['default']}" if column_info['default'] else ""
                print(f"  ✓ Added: {column_info['column']} ({column_info['type']} {nullable_str}{default_str})")
                columns_added += 1
                total_changes += 1
            else:
                print(f"  📝 Exists: {column_info['column']}")
        
        if columns_added == 0:
            print(f"  ✅ No updates needed for {table_name}")
    
    # Commit changes
    conn.commit()
    
    # Show final summary
    print("\n" + "=" * 50)
    print("📋 UPDATED DATABASE STRUCTURE")
    print("=" * 50)
    
    for table_name in existing_tables:
        if table_name in discovered_models:
            print(f"\n🏷️  Table: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            for col in columns_info:
                col_name, col_type, not_null, default_val, pk = col[1], col[2], col[3], col[4], col[5]
                pk_indicator = "🔑" if pk else "  "
                null_indicator = "NOT NULL" if not_null else "NULL"
                default_info = f"DEFAULT {default_val}" if default_val else ""
                print(f"  {pk_indicator} {col_name:<20} {col_type:<15} {null_indicator:<8} {default_info}")
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  📊 Records: {count}")
    
    print(f"\n✅ UPDATE COMPLETED!")
    print(f"📊 Total changes made: {total_changes}")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if total_changes > 0:
        print("\n🎉 Database successfully updated!")
    else:
        print("\n💡 Database was already up to date!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.rollback()
finally:
    if 'conn' in locals():
        conn.close()

print("\n💡 This script safely parsed your models.py without importing it")
print("   to avoid SQLAlchemy conflicts. If some columns weren't detected,")
print("   they might use complex syntax that needs manual addition.")
