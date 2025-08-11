#!/usr/bin/env python3
"""
Universal Database Schema Updater
Analyzes all Flask-SQLAlchemy models and synchronizes database schema
"""

import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import argparse
from datetime import datetime

class ModelAnalyzer:
    """Analyzes Flask-SQLAlchemy models to extract schema information"""
    
    def __init__(self, models_file: str = "hotel_app/models.py"):
        self.models_file = models_file
        self.models = {}
        self.content = ""
    
    def load_models(self) -> bool:
        """Load and parse the models file"""
        if not Path(self.models_file).exists():
            print(f"❌ Models file not found: {self.models_file}")
            return False
        
        with open(self.models_file, 'r') as f:
            self.content = f.read()
        
        return True
    
    def extract_models(self) -> Dict:
        """Extract all model classes and their information"""
        if not self.content:
            return {}
        
        # Find all model classes
        class_pattern = r'class\s+(\w+)\s*\([^)]*db\.Model[^)]*\):(.*?)(?=class|\Z)'
        matches = re.findall(class_pattern, self.content, re.DOTALL)
        
        for class_name, class_content in matches:
            table_name = self._extract_table_name(class_name, class_content)
            columns = self._extract_columns(class_content)
            foreign_keys = self._extract_foreign_keys(class_content)
            
            self.models[class_name] = {
                'table_name': table_name,
                'columns': columns,
                'foreign_keys': foreign_keys
            }
        
        return self.models
    
    def _extract_table_name(self, class_name: str, class_content: str) -> str:
        """Extract table name from model class"""
        # Look for __tablename__ = 'table_name'
        tablename_match = re.search(r'__tablename__\s*=\s*["\']([^"\']+)["\']', class_content)
        if tablename_match:
            return tablename_match.group(1)
        
        # Default to lowercase class name
        return class_name.lower()
    
    def _extract_columns(self, class_content: str) -> Dict:
        """Extract column definitions from class content"""
        columns = {}
        
        # Pattern to match column definitions
        column_pattern = r'(\w+)\s*=\s*db\.Column\s*\(([^)]+(?:\([^)]*\))?[^)]*)\)'
        matches = re.findall(column_pattern, class_content)
        
        for col_name, col_definition in matches:
            col_type, nullable, default = self._parse_column_definition(col_definition)
            columns[col_name] = {
                'type': col_type,
                'nullable': nullable,
                'default': default,
                'definition': col_definition.strip()
            }
        
        return columns
    
    def _parse_column_definition(self, definition: str) -> Tuple[str, bool, Optional[str]]:
        """Parse column definition to extract type, nullable, default"""
        # Extract column type (first argument)
        type_match = re.search(r'db\.(\w+)(?:\([^)]*\))?', definition)
        col_type = type_match.group(1) if type_match else 'Unknown'
        
        # Check if nullable
        nullable = 'nullable=False' not in definition
        
        # Extract default value
        default_match = re.search(r'default=([^,)]+)', definition)
        default = default_match.group(1) if default_match else None
        
        return col_type, nullable, default
    
    def _extract_foreign_keys(self, class_content: str) -> List:
        """Extract foreign key relationships"""
        foreign_keys = []
        fk_pattern = r'db\.ForeignKey\s*\(\s*["\']([^"\']+)["\']'
        matches = re.findall(fk_pattern, class_content)
        
        for fk in matches:
            foreign_keys.append(fk)
        
        return foreign_keys

class DatabaseInspector:
    """Inspects existing database schema"""
    
    def __init__(self, db_path: str = "instance/hotel_app.db"):
        self.db_path = db_path
        self.schema = {}
    
    def inspect_schema(self) -> Dict:
        """Inspect current database schema"""
        if not Path(self.db_path).exists():
            print(f"❌ Database not found: {self.db_path}")
            return {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                self.schema[table_name] = self._get_table_info(cursor, table_name)
        
        finally:
            conn.close()
        
        return self.schema
    
    def _get_table_info(self, cursor, table_name: str) -> Dict:
        """Get detailed table information"""
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        table_info = {
            'columns': {},
            'foreign_keys': []
        }
        
        for col_info in columns:
            col_name = col_info[1]
            table_info['columns'][col_name] = {
                'type': col_info[2],
                'nullable': not col_info[3],  # notnull is inverted
                'default': col_info[4],
                'primary_key': bool(col_info[5])
            }
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fks = cursor.fetchall()
        for fk in fks:
            table_info['foreign_keys'].append({
                'column': fk[3],
                'referenced_table': fk[2],
                'referenced_column': fk[4]
            })
        
        return table_info

class SchemaSynchronizer:
    """Synchronizes model schema with database schema"""
    
    def __init__(self, models: Dict, db_schema: Dict, db_path: str):
        self.models = models
        self.db_schema = db_schema
        self.db_path = db_path
        self.changes = []
    
    def analyze_differences(self) -> List:
        """Analyze differences between models and database"""
        self.changes = []
        
        for class_name, model_info in self.models.items():
            table_name = model_info['table_name']
            model_columns = model_info['columns']
            
            if table_name not in self.db_schema:
                self._add_create_table_change(class_name, model_info)
            else:
                db_columns = self.db_schema[table_name]['columns']
                self._analyze_column_differences(table_name, model_columns, db_columns)
        
        return self.changes
    
    def _add_create_table_change(self, class_name: str, model_info: Dict):
        """Add change to create new table"""
        self.changes.append({
            'type': 'CREATE_TABLE',
            'class': class_name,
            'table': model_info['table_name'],
            'columns': model_info['columns']
        })
    
    def _analyze_column_differences(self, table_name: str, model_columns: Dict, db_columns: Dict):
        """Analyze column differences for a table"""
        model_col_set = set(model_columns.keys())
        db_col_set = set(db_columns.keys())
        
        # Missing columns (in model but not in database)
        missing_columns = model_col_set - db_col_set
        for col_name in missing_columns:
            self.changes.append({
                'type': 'ADD_COLUMN',
                'table': table_name,
                'column': col_name,
                'definition': model_columns[col_name]
            })
        
        # Extra columns (in database but not in model)
        extra_columns = db_col_set - model_col_set
        for col_name in extra_columns:
            self.changes.append({
                'type': 'EXTRA_COLUMN',
                'table': table_name,
                'column': col_name,
                'info': f"Column exists in database but not in model"
            })
    
    def generate_sql_commands(self) -> List[str]:
        """Generate SQL commands to apply changes"""
        sql_commands = []
        
        for change in self.changes:
            if change['type'] == 'ADD_COLUMN':
                sql = self._generate_add_column_sql(change)
                if sql:
                    sql_commands.append(sql)
            elif change['type'] == 'CREATE_TABLE':
                # Note: CREATE TABLE is complex, suggest using Flask-Migrate instead
                sql_commands.append(f"-- CREATE TABLE {change['table']} (complex, use Flask-Migrate)")
        
        return sql_commands
    
    def _generate_add_column_sql(self, change: Dict) -> str:
        """Generate ADD COLUMN SQL"""
        table = change['table']
        column = change['column']
        definition = change['definition']
        
        # Map SQLAlchemy types to SQLite types
        type_mapping = {
            'Integer': 'INTEGER',
            'String': 'TEXT',
            'Text': 'TEXT',
            'Boolean': 'BOOLEAN',
            'DateTime': 'DATETIME',
            'Date': 'DATE',
            'Float': 'REAL',
            'Numeric': 'NUMERIC'
        }
        
        col_type = definition['type']
        sqlite_type = type_mapping.get(col_type, 'TEXT')
        
        sql = f"ALTER TABLE {table} ADD COLUMN {column} {sqlite_type}"
        
        if not definition['nullable']:
            # SQLite doesn't support adding NOT NULL columns to existing tables easily
            # We'll add as nullable and note this limitation
            sql += " -- Note: Should be NOT NULL but SQLite limitation"
        
        if definition['default']:
            sql += f" DEFAULT {definition['default']}"
        
        return sql + ";"
    
    def apply_changes(self, dry_run: bool = True) -> bool:
        """Apply the schema changes"""
        if not self.changes:
            print("✅ No changes needed - schema is up to date!")
            return True
        
        sql_commands = self.generate_sql_commands()
        
        if dry_run:
            print("\n🔍 DRY RUN - SQL commands that would be executed:")
            for sql in sql_commands:
                print(f"  {sql}")
            return True
        
        # Create backup
        backup_path = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._create_backup(backup_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for sql in sql_commands:
                if not sql.startswith('--'):  # Skip comments
                    print(f"Executing: {sql}")
                    cursor.execute(sql)
            
            conn.commit()
            print("✅ Successfully applied all changes!")
            return True
            
        except Exception as e:
            print(f"❌ Error applying changes: {e}")
            conn.rollback()
            print(f"💾 Database backup available at: {backup_path}")
            return False
            
        finally:
            conn.close()
    
    def _create_backup(self, backup_path: str):
        """Create database backup"""
        import shutil
        shutil.copy2(self.db_path, backup_path)
        print(f"💾 Created backup: {backup_path}")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Universal Database Schema Updater")
    parser.add_argument("--models", default="hotel_app/models.py", help="Path to models file")
    parser.add_argument("--db", default="instance/hotel_app.db", help="Path to database file")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying them")
    parser.add_argument("--apply", action="store_true", help="Apply changes to database")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("="*80)
    print("🔄 Universal Database Schema Updater")
    print("="*80)
    
    # Step 1: Analyze models
    print("\n📋 Step 1: Analyzing models...")
    analyzer = ModelAnalyzer(args.models)
    
    if not analyzer.load_models():
        return 1
    
    models = analyzer.extract_models()
    print(f"✅ Found {len(models)} model classes:")
    for class_name, info in models.items():
        print(f"  📋 {class_name} -> {info['table_name']} ({len(info['columns'])} columns)")
        if args.verbose:
            for col_name, col_info in info['columns'].items():
                print(f"    - {col_name}: {col_info['type']}")
    
    # Step 2: Inspect database
    print(f"\n🗄️  Step 2: Inspecting database...")
    inspector = DatabaseInspector(args.db)
    db_schema = inspector.inspect_schema()
    
    if not db_schema:
        print("⚠️  Database not found or empty")
    else:
        print(f"✅ Found {len(db_schema)} tables in database:")
        for table_name, info in db_schema.items():
            print(f"  🗄️  {table_name} ({len(info['columns'])} columns)")
    
    # Step 3: Analyze differences
    print(f"\n🔍 Step 3: Analyzing differences...")
    synchronizer = SchemaSynchronizer(models, db_schema, args.db)
    changes = synchronizer.analyze_differences()
    
    if not changes:
        print("✅ Schema is up to date - no changes needed!")
        return 0
    
    print(f"📝 Found {len(changes)} changes needed:")
    for change in changes:
        if change['type'] == 'ADD_COLUMN':
            print(f"  + Add column: {change['table']}.{change['column']} ({change['definition']['type']})")
        elif change['type'] == 'EXTRA_COLUMN':
            print(f"  ⚠️  Extra column: {change['table']}.{change['column']} (in DB but not model)")
        elif change['type'] == 'CREATE_TABLE':
            print(f"  + Create table: {change['table']} (class: {change['class']})")
    
    # Step 4: Apply changes
    if args.apply:
        print(f"\n⚡ Step 4: Applying changes...")
        success = synchronizer.apply_changes(dry_run=False)
        return 0 if success else 1
    else:
        print(f"\n🔍 Step 4: Dry run (use --apply to execute)")
        synchronizer.apply_changes(dry_run=True)
        print(f"\n💡 To apply these changes, run: python {sys.argv[0]} --apply")
        return 0

if __name__ == "__main__":
    sys.exit(main())