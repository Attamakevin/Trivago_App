#!/usr/bin/env python3
"""
Database Schema Synchronization Tool
Syncs SQLAlchemy models with SQLite database schema
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
                print(f"      - {col_name}: {col_info['type']} {' '.join(col_info['constraints'])}")
        
        return True
    
    def _parse_models(self, content: str):
        """Parse SQLAlchemy models from file content"""
        lines = content.split('\n')
        current_model = None
        current_model_info = {}
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Look for class definitions
            class_match = re.search(r'class\s+(\w+)\s*\(.*db\.Model.*\)', line)
            if class_match:
                if current_model and current_model_info:
                    self.found_models[current_model] = current_model_info
                
                current_model = class_match.group(1)
                current_model_info = {
                    'table_name': self._get_table_name(current_model),
                    'columns': {},
                    'line_num': line_num
                }
                print(f"  ✓ Found model: {current_model} (line {line_num})")
                continue
            
            # Look for table name override
            if current_model and '__tablename__' in line:
                table_match = re.search(r'__tablename__\s*=\s*[\'"](\w+)[\'"]', line)
                if table_match:
                    current_model_info['table_name'] = table_match.group(1)
                    print(f"    📋 Table name: {table_match.group(1)}")
                continue
            
            # Look for column definitions
            if current_model:
                column_match = re.search(r'(\w+)\s*=\s*db\.Column\s*\((.*)\)', line)
                if column_match:
                    col_name = column_match.group(1)
                    col_definition = column_match.group(2)
                    
                    col_info = self._parse_column_definition(col_definition)
                    current_model_info['columns'][col_name] = col_info
                    print(f"    ✓ Column: {col_name} -> {col_info['type']} {' '.join(col_info['constraints'])}")
        
        # Add the last model
        if current_model and current_model_info:
            self.found_models[current_model] = current_model_info
    
    def _get_table_name(self, model_name: str) -> str:
        """Convert model name to table name (lowercase)"""
        return model_name.lower()
    
    def _parse_column_definition(self, definition: str) -> Dict[str, Any]:
        """Parse column definition to extract type and constraints"""
        col_info = {
            'type': 'TEXT',
            'constraints': [],
            'nullable': True,
            'default': None
        }
        
        # Extract column type with length parameter
        type_patterns = [
            r'db\.String\((\d+)\)',  # String with length
            r'db\.(\w+)',            # Other types
        ]
        
        for pattern in type_patterns:
            type_match = re.search(pattern, definition)
            if type_match:
                if 'String' in pattern:
                    col_info['type'] = f"VARCHAR({type_match.group(1)})"
                else:
                    col_info['type'] = self._map_sqlalchemy_type(type_match.group(1))
                break
        
        # Check for constraints
        if 'primary_key=True' in definition:
            col_info['constraints'].append('PRIMARY KEY')
        if 'nullable=False' in definition:
            col_info['constraints'].append('NOT NULL')
            col_info['nullable'] = False
        if 'unique=True' in definition:
            col_info['constraints'].append('UNIQUE')
        
        # Extract default value
        default_match = re.search(r'default=([^,)]+)', definition)
        if default_match:
            col_info['default'] = default_match.group(1)
        
        return col_info
    
    def _map_sqlalchemy_type(self, sa_type: str) -> str:
        """Map SQLAlchemy types to SQLite types"""
        type_map = {
            'Integer': 'INTEGER',
            'String': 'VARCHAR(255)',
            'Text': 'TEXT',
            'DateTime': 'DATETIME',
            'Boolean': 'BOOLEAN',
            'Float': 'REAL',
            'Numeric': 'NUMERIC',
            'LargeBinary': 'BLOB'
        }
        return type_map.get(sa_type, 'TEXT')
    
    def analyze_database(self):
        """Analyze existing database schema"""
        print(f"\n🔍 ANALYZING DATABASE: {self.db_path}")
        print("=" * 60)
        
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"📊 Found {len(tables)} tables in database:")
            
            for (table_name,) in tables:
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
                    
                    print(f"    - {col_name}: {col_type} {'NOT NULL' if not_null else 'NULL'}")
                
                self.db_schema[table_name] = table_schema
            
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
                        print(f"    - {col_name}: {col_info['type']} {' '.join(col_info['constraints'])}")
        
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
                if col_info['constraints']:
                    col_def += " " + " ".join(col_info['constraints'])
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
                if col_info['constraints'] and 'PRIMARY KEY' not in col_info['constraints']:
                    # Can't add PRIMARY KEY constraint via ALTER TABLE
                    constraints = [c for c in col_info['constraints'] if c != 'PRIMARY KEY']
                    if constraints:
                        col_def += " " + " ".join(constraints)
                
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
            # Backup database first
            backup_path = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"📦 Creating backup: {backup_path}")
            
            with open(self.db_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            
            # Apply changes
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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


def main():
    """Main entry point"""
    models_file = "hotel_app/models.py"
    db_path = "instance/hotel_app.db"
    
    # Check if custom paths provided
    if len(sys.argv) > 1:
        models_file = sys.argv[1]
    if len(sys.argv) > 2:
        db_path = sys.argv[2]
    
    syncer = DatabaseSchemaSyncer(models_file, db_path)
    
    print("🔧 Database Schema Synchronization Tool")
    print("=" * 50)
    print(f"Models file: {models_file}")
    print(f"Database: {db_path}")
    print()
    
    # First run in dry-run mode
    success = syncer.sync_database(dry_run=True)
    
    if success:
        print("\n" + "=" * 80)
        response = input("🤔 Apply these changes to the database? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            syncer.sync_database(dry_run=False)
        else:
            print("❌ Changes not applied.")


if __name__ == "__main__":
    main()