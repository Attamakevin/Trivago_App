import os
import re

def debug_models_file(file_path):
    """Debug version that shows what it's finding in the models file"""
    print(f"🔍 DEBUGGING MODELS FILE: {file_path}")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    print(f"📄 Total lines in file: {len(lines)}")
    
    # Show first few lines
    print("\n📋 First 10 lines:")
    for i, line in enumerate(lines[:10], 1):
        print(f"{i:2d}: {repr(line)}")
    
    # Look for class definitions
    print("\n🔍 Looking for class definitions...")
    class_patterns = [
        r'class\s+(\w+)\s*\(.*db\.Model.*\)',
        r'class\s+(\w+)\s*\(.*Model.*\)',
        r'class\s+(\w+)\s*\(.*Base.*\)',
        r'class\s+(\w+)\s*\(.*SQLAlchemy.*\)',
    ]
    
    found_classes = []
    for line_num, line in enumerate(lines, 1):
        for pattern_name, pattern in enumerate(class_patterns):
            match = re.search(pattern, line)
            if match:
                found_classes.append((line_num, match.group(1), line.strip()))
                print(f"  ✓ Line {line_num}: Found class '{match.group(1)}' (pattern {pattern_name})")
                print(f"    Code: {line.strip()}")
    
    if not found_classes:
        print("  ❌ No class definitions found!")
        print("\n🔍 Looking for ANY class definitions...")
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('class '):
                print(f"  Line {line_num}: {line.strip()}")
    
    # Look for column definitions
    print("\n🔍 Looking for column definitions...")
    column_patterns = [
        r'(\w+)\s*=\s*db\.Column',
        r'(\w+)\s*=\s*Column',
    ]
    
    found_columns = []
    for line_num, line in enumerate(lines, 1):
        for pattern in column_patterns:
            match = re.search(pattern, line)
            if match:
                found_columns.append((line_num, match.group(1), line.strip()))
                print(f"  ✓ Line {line_num}: Found column '{match.group(1)}'")
                print(f"    Code: {line.strip()}")
    
    if not found_columns:
        print("  ❌ No column definitions found!")
        print("\n🔍 Looking for ANY lines with '=' and 'Column'...")
        for line_num, line in enumerate(lines, 1):
            if 'Column' in line and '=' in line:
                print(f"  Line {line_num}: {line.strip()}")
    
    # Look for imports
    print("\n🔍 Looking for imports...")
    import_lines = []
    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith('from ') or line.strip().startswith('import '):
            import_lines.append((line_num, line.strip()))
            print(f"  Line {line_num}: {line.strip()}")
    
    # Show some context around classes
    if found_classes:
        print("\n📖 Context around found classes:")
        for line_num, class_name, class_line in found_classes:
            print(f"\n  🏷️  Class: {class_name} (line {line_num})")
            start = max(0, line_num - 3)
            end = min(len(lines), line_num + 10)
            for i in range(start, end):
                marker = ">>>" if i == line_num - 1 else "   "
                print(f"  {marker} {i+1:2d}: {lines[i]}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print(f"  Classes found: {len(found_classes)}")
    print(f"  Columns found: {len(found_columns)}")
    print(f"  Import lines: {len(import_lines)}")
    
    if not found_classes:
        print("\n💡 SUGGESTIONS:")
        print("  1. Make sure your models inherit from db.Model")
        print("  2. Check if imports are correct (from flask_sqlalchemy import SQLAlchemy)")
        print("  3. Verify class syntax: class ModelName(db.Model):")
        print("  4. Make sure the file isn't corrupted or has encoding issues")

if __name__ == "__main__":
    models_file = "hotel_app/models.py"
    debug_models_file(models_file)