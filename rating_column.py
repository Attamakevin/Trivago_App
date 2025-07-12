#!/usr/bin/env python3
"""
Enhanced Database Schema Synchronization Tool
Syncs SQLAlchemy models with SQLite database schema
Supports adding new models like UserHotelAssignment and updating existing tables
"""

import os
import re
import sqlite3
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Any

class DatabaseSchemaSyncer:
    def __init__(self, models_file: str = "hotel_app/models.py", db_path: str = "instance/hotel_app.db"):
        self.models_file = models_file
        self.db_path = db_path
        self.found_models = {}
        self.db_schema = {}
        
    def debug_models_file(self):
        """Debug version that shows what it's finding in the models file"""
        print(f"🔍 DEBUGGING MODELS FILE: {self.models_file}")
        print("=" * 60)
        
        if not os.path.exists(self.models_file):
            print(f"❌ File not found: {self.models_file}")
            return False
        
        with open(self.models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        print(f"📄 Total lines in file: {len(lines)}")
        
        # Parse models and columns
        self._parse_models(content)
        
        # Show summary
        print("\n" + "=" * 60)
        print("📊 MODELS SUMMARY:")
        for model_name, model_info in self.found_models.items():
            print(f"  🏷️  {model_name}:")
            print(f"    Table: {model_info['table_name']}")
            print(f"    Columns: {len(model_info['columns'])}")
            for col_name, col_info in model_info['columns'].items():
                constraints_str = ' '.join(col_info['constraints']) if col_info['constraints'] else ''
                print(f"      - {col_name}: {col_info['type']} {constraints_str}")
            
            # Show relationships
            if model_info.get('relationships'):
                print(f"    Relationships: {len(model_info['relationships'])}")
                for rel_name, rel_info in model_info['relationships'].items():
                    print(f"      - {rel_name}: {rel_info}")
        
        return True
    
    def _parse_models(self, content: str):
        """Parse SQLAlchemy models from file content"""
        lines = content.split('\n')
        current_model = None
        current_model_info = {}
        in_class = False
        indent_level = 0
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            line = line.strip()
            
            # Detect class definition
            class_match = re.search(r'class\s+(\w+)\s*\(.*db\.Model.*\)', line)
            if class_match:
                # Save previous model
                if current_model and current_model_info:
                    self.found_models[current_model] = current_model_info
                
                current_model = class_match.group(1)
                current_model_info = {
                    'table_name': self._get_table_name(current_model),
                    'columns': {},
                    'relationships': {},
                    'constraints': [],
                    'line_num': line_num
                }
                in_class = True
                indent_level = len(original_line) - len(original_line.lstrip())
                print(f"  ✓ Found model: {current_model} (line {line_num})")
                continue
            
            # Check if we're still in the class
            if in_class and line and not line.startswith('#'):
                current_indent = len(original_line) - len(original_line.lstrip())
                if current_indent <= indent_level and not line.startswith('class'):
                    in_class = False
                    current_model = None
                    continue
            
            if not in_class or not current_model:
                continue
            
            # Look for table name override
            if '__tablename__' in line:
                table_match = re.search(r'__tablename__\s*=\s*[\'"](\w+)[\'"]', line)
                if table_match:
                    current_model_info['table_name'] = table_match.group(1)
                    print(f"    📋 Table name: {table_match.group(1)}")
                continue
            
            # Look for table constraints
            if '__table_args__' in line:
                print(f"    ⚙️  Table constraints found (line {line_num})")
                current_model_info['constraints'].append(line)
                continue
            
            # Look for column definitions
            column_match = re.search(r'(\w+)\s*=\s*db\.Column\s*\((.*)\)', line)
            if column_match:
                col_name = column_match.group(1)
                col_definition = column_match.group(2)
                
                col_info = self._parse_column_definition(col_definition)
                current_model_info['columns'][col_name] = col_info
                constraints_str = ' '.join(col_info['constraints']) if col_info['constraints'] else ''
                print(f"    ✓ Column: {col_name} -> {col_info['type']} {constraints_str}")
                continue
            
            # Look for relationships
            relationship_match = re.search(r'(\w+)\s*=\s*db\.relationship\s*\((.*)\)', line)
            if relationship_match:
                rel_name = relationship_match.group(1)
                rel_definition = relationship_match.group(2)
                current_model_info['relationships'][rel_name] = rel_definition
                print(f"    🔗 Relationship: {rel_name} -> {rel_definition}")
                continue
        
        # Add the last model
        if current_model and current_model_info:
            self.found_models[current_model] = current_model_info
    
    def _get_table_name(self, model_name: str) -> str:
        """Convert model name to table name (lowercase with underscores)"""
        # Convert CamelCase to snake_case
        table_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', model_name)
        table_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', table_name).lower()
        return table_name
    
    def _parse_column_definition(self, definition: str) -> Dict[str, Any]:
        """Parse column definition to extract type and constraints"""
        col_info = {
            'type': 'TEXT',
            'constraints': [],
            'nullable': True,
            'default': None,
            'foreign_key': None
        }
        
        # Extract column type with length parameter
        type_patterns = [
            (r'db\.String\((\d+)\)', lambda m: f"VARCHAR({m.group(1)})"),
            (r'db\.Integer', lambda m: "INTEGER"),
            (r'db\.Text', lambda m: "TEXT"),
            (r'db\.DateTime', lambda m: "DATETIME"),
            (r'db\.Boolean', lambda m: "BOOLEAN"),
            (r'db\.Float', lambda m: "REAL"),
            (r'db\.Numeric', lambda m: "NUMERIC"),
            (r'db\.LargeBinary', lambda m: "BLOB"),
        ]
        
        for pattern, type_func in type_patterns:
            type_match = re.search(pattern, definition)
            if type_match:
                col_info['type'] = type_func(type_match)
                break
        
        # Check for constraints
        if 'primary_key=True' in definition:
            col_info['constraints'].append('PRIMARY KEY')
        if 'nullable=False' in definition:
            col_info['constraints'].append('NOT NULL')
            col_info['nullable'] = False
        if 'unique=True' in definition:
            col_info['constraints'].append('UNIQUE')
        if 'autoincrement=True' in definition:
            col_info['constraints'].append('AUTOINCREMENT')
        
        # Extract foreign key
        fk_match = re.search(r'db\.ForeignKey\s*\(\s*[\'"]([^\'"]+)[\'"]', definition)
        if fk_match:
            col_info['foreign_key'] = fk_match.group(1)
            # Add REFERENCES constraint for display
            col_info['constraints'].append(f"REFERENCES {fk_match.group(1)}")
        
        # Extract default value
        default_patterns = [
            r'default=([^,)]+)',
            r'server_default=([^,)]+)'
        ]
        
        for pattern in default_patterns:
            default_match = re.search(pattern, definition)
            if default_match:
                col_info['default'] = default_match.group(1)
                break
        
        return col_info
    
    def analyze_database(self):
        """Analyze existing database schema"""
        print(f"\n🔍 ANALYZING DATABASE: {self.db_path}")
        print("=" * 60)
        
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            print("💡 This is OK if you're creating a new database")
            return True  # Return True to continue with table creation
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"📊 Found {len(tables)} tables in database:")
            
            for (table_name,) in tables:
                if table_name.startswith('sqlite_'):
                    continue  # Skip system tables
                    
                print(f"  📋 Table: {table_name}")
                
                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                table_schema = {}
                for col_info in columns:
                    col_name = col_info[1]
                    col_type = col_info[2]
                    not_null = col_info[3]
                    default_val = col_info[4]
                    is_pk = col_info[5]
                    
                    table_schema[col_name] = {
                        'type': col_type,
                        'not_null': bool(not_null),
                        'default': default_val,
                        'primary_key': bool(is_pk)
                    }
                    
                    constraints = []
                    if is_pk:
                        constraints.append('PRIMARY KEY')
                    if not_null:
                        constraints.append('NOT NULL')
                    if default_val:
                        constraints.append(f'DEFAULT {default_val}')
                    
                    constraints_str = ' '.join(constraints) if constraints else ''
                    print(f"    - {col_name}: {col_type} {constraints_str}")
                
                self.db_schema[table_name] = table_schema
                
                # Get foreign keys
                cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                foreign_keys = cursor.fetchall()
                if foreign_keys:
                    print(f"    🔗 Foreign Keys:")
                    for fk in foreign_keys:
                        print(f"      - {fk[3]} -> {fk[2]}.{fk[4]}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error analyzing database: {e}")
            return False
    
    def find_missing_tables_and_columns(self):
        """Find missing tables and columns"""
        print(f"\n🔍 FINDING MISSING TABLES AND COLUMNS")
        print("=" * 60)
        
        missing_tables = []
        missing_columns = {}
        
        for model_name, model_info in self.found_models.items():
            table_name = model_info['table_name']
            
            if table_name not in self.db_schema:
                missing_tables.append((model_name, table_name, model_info))
                print(f"❌ Missing table: {table_name} (for model {model_name})")
            else:
                # Check for missing columns
                db_columns = set(self.db_schema[table_name].keys())
                model_columns = set(model_info['columns'].keys())
                missing_cols = model_columns - db_columns
                
                if missing_cols:
                    missing_columns[table_name] = []
                    print(f"⚠️  Table {table_name} missing columns:")
                    for col_name in missing_cols:
                        col_info = model_info['columns'][col_name]
                        missing_columns[table_name].append((col_name, col_info))
                        constraints_str = ' '.join(col_info['constraints']) if col_info['constraints'] else ''
                        print(f"    - {col_name}: {col_info['type']} {constraints_str}")
        
        if not missing_tables and not missing_columns:
            print("✅ All tables and columns are up to date!")
        
        return missing_tables, missing_columns
    
    def generate_sql_statements(self, missing_tables: List, missing_columns: Dict):
        """Generate SQL statements to create missing tables and columns"""
        print(f"\n🔧 GENERATING SQL STATEMENTS")
        print("=" * 60)
        
        sql_statements = []
        
        # Create missing tables
        for model_name, table_name, model_info in missing_tables:
            create_table_sql = f"CREATE TABLE {table_name} (\n"
            column_definitions = []
            
            for col_name, col_info in model_info['columns'].items():
                col_def = f"  {col_name} {col_info['type']}"
                
                # Add constraints
                constraints = []
                for constraint in col_info['constraints']:
                    if constraint.startswith('REFERENCES'):
                        # Handle foreign key constraints
                        constraints.append(f"REFERENCES {col_info['foreign_key']}")
                    else:
                        constraints.append(constraint)
                
                if constraints:
                    col_def += " " + " ".join(constraints)
                
                # Add default value
                if col_info['default'] and 'DEFAULT' not in col_def:
                    col_def += f" DEFAULT {col_info['default']}"
                
                column_definitions.append(col_def)
            
            create_table_sql += ",\n".join(column_definitions)
            create_table_sql += "\n);"
            
            sql_statements.append(create_table_sql)
            print(f"📝 CREATE TABLE {table_name}:")
            print(create_table_sql)
            print()
        
        # Add missing columns
        for table_name, columns in missing_columns.items():
            for col_name, col_info in columns:
                col_def = f"{col_name} {col_info['type']}"
                
                # Handle constraints for ALTER TABLE (some constraints can't be added via ALTER)
                safe_constraints = []
                for constraint in col_info['constraints']:
                    if constraint not in ['PRIMARY KEY', 'AUTOINCREMENT']:
                        if constraint.startswith('REFERENCES'):
                            # Foreign key constraints need special handling in ALTER TABLE
                            safe_constraints.append(constraint)
                        else:
                            safe_constraints.append(constraint)
                
                if safe_constraints:
                    col_def += " " + " ".join(safe_constraints)
                
                # Add default value
                if col_info['default'] and 'DEFAULT' not in col_def:
                    col_def += f" DEFAULT {col_info['default']}"
                
                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_def};"
                sql_statements.append(alter_sql)
                print(f"📝 ALTER TABLE {table_name}:")
                print(alter_sql)
                print()
        
        return sql_statements
    
    def apply_database_changes(self, sql_statements: List[str], dry_run: bool = True):
        """Apply the generated SQL statements to the database"""
        print(f"\n{'🔍 DRY RUN' if dry_run else '⚡ APPLYING'} DATABASE CHANGES")
        print("=" * 60)
        
        if not sql_statements:
            print("✅ No changes needed!")
            return True
        
        if dry_run:
            print("📋 SQL statements that would be executed:")
            for i, statement in enumerate(sql_statements, 1):
                print(f"{i}. {statement}")
            print("\n💡 Run with dry_run=False to apply changes")
            return True
        
        try:
            # Create backup if database exists
            if os.path.exists(self.db_path):
                backup_path = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                print(f"📦 Creating backup: {backup_path}")
                
                with open(self.db_path, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
            
            # Apply changes
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            for i, statement in enumerate(sql_statements, 1):
                print(f"⚡ Executing statement {i}/{len(sql_statements)}")
                print(f"   {statement}")
                cursor.execute(statement)
            
            conn.commit()
            conn.close()
            
            print("✅ Database changes applied successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error applying changes: {e}")
            if os.path.exists(backup_path):
                print(f"💡 Database backup available at: {backup_path}")
            return False
    
    def sync_database(self, dry_run: bool = True):
        """Main function to sync database with models"""
        print("🚀 STARTING DATABASE SCHEMA SYNC")
        print("=" * 80)
        
        # Step 1: Parse models
        if not self.debug_models_file():
            return False
        
        # Step 2: Analyze database
        if not self.analyze_database():
            return False
        
        # Step 3: Find differences
        missing_tables, missing_columns = self.find_missing_tables_and_columns()
        
        # Step 4: Generate SQL
        sql_statements = self.generate_sql_statements(missing_tables, missing_columns)
        
        # Step 5: Apply changes
        return self.apply_database_changes(sql_statements, dry_run=dry_run)
    
    def generate_model_template(self, model_name: str = "UserHotelAssignment"):
        """Generate a template for the UserHotelAssignment model"""
        print(f"\n📝 GENERATING MODEL TEMPLATE: {model_name}")
        print("=" * 60)
        
        template = f'''
class {model_name}(db.Model):
    __tablename__ = '{self._get_table_name(model_name)}'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='hotel_assignments')
    hotel = db.relationship('Hotel', backref='user_assignments')
    assigned_by_user = db.relationship('User', foreign_keys=[assigned_by])
    
    # Ensure unique user-hotel pairs
    __table_args__ = (
        db.UniqueConstraint('user_id', 'hotel_id', name='unique_user_hotel'),
    )
    
    def __repr__(self):
        return f'<{model_name} {{self.user_id}}-{{self.hotel_id}}>'
'''
        
        print("📋 Add this model to your models.py file:")
        print(template)
        
        return template


def main():
    """Main entry point"""
    models_file = "hotel_app/models.py"
    db_path = "instance/hotel_app.db"
    
    # Check if custom paths provided
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("🔧 Database Schema Synchronization Tool")
            print("Usage: python sync_db.py [models_file] [db_path] [--template]")
            print("  --template: Generate UserHotelAssignment model template")
            return
        elif sys.argv[1] == '--template':
            syncer = DatabaseSchemaSyncer(models_file, db_path)
            syncer.generate_model_template()
            return
        else:
            models_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        db_path = sys.argv[2]
    
    syncer = DatabaseSchemaSyncer(models_file, db_path)
    
    print("🔧 Database Schema Synchronization Tool")
    print("=" * 50)
    print(f"Models file: {models_file}")
    print(f"Database: {db_path}")
    print()
    
    # Check if models file exists
    if not os.path.exists(models_file):
        print(f"❌ Models file not found: {models_file}")
        print("💡 Make sure you're running this from the correct directory")
        return
    
    # First run in dry-run mode
    success = syncer.sync_database(dry_run=True)
    
    if success:
        print("\n" + "=" * 80)
        response = input("🤔 Apply these changes to the database? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            syncer.sync_database(dry_run=False)
            print("\n💡 Don't forget to update your routes.py imports:")
            print("from hotel_app.models import User, Hotel, UserHotelAssignment")
        else:
            print("❌ Changes not applied.")
    
    print("\n💡 To generate a UserHotelAssignment model template:")
    print("python sync_db.py --template")


if __name__ == "__main__":
    main()