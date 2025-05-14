"""
Script to verify the project setup and dependencies.
"""

import os
import sys
from pathlib import Path

def check_directory_structure():
    """Check if all required directories and files exist"""
    required_dirs = [
        'src',
        'src/amazon_bulk_generator',
        'src/amazon_bulk_generator/core',
        'src/amazon_bulk_generator/utils',
        'src/amazon_bulk_generator/web',
        'templates',
        'output',
        'tests'
    ]
    
    required_files = [
        'src/amazon_bulk_generator/__init__.py',
        'src/amazon_bulk_generator/core/generator.py',
        'src/amazon_bulk_generator/core/validators.py',
        'src/amazon_bulk_generator/utils/file_handlers.py',
        'src/amazon_bulk_generator/utils/formatters.py',
        'src/amazon_bulk_generator/web/app.py',
        'templates/keywords_template.csv',
        'templates/skus_template.csv',
        'requirements.txt',
        'streamlit_app.py',
        'README.md'
    ]
    
    print("Checking directory structure...")
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ Found directory: {directory}")
        else:
            print(f"✗ Missing directory: {directory}")
            os.makedirs(directory)
            print(f"  Created directory: {directory}")
    
    print("\nChecking required files...")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ Found file: {file_path}")
        else:
            print(f"✗ Missing file: {file_path}")

def check_python_path():
    """Check if src directory is in Python path"""
    src_path = str(Path(__file__).parent / 'src')
    if src_path not in sys.path:
        print("\nAdding src directory to Python path...")
        sys.path.append(src_path)
        print(f"Added {src_path} to Python path")

def check_dependencies():
    """Check if all required packages are installed"""
    try:
        import streamlit
        import pandas
        import openpyxl
        print("\n✓ All core dependencies are installed")
    except ImportError as e:
        print(f"\n✗ Missing dependency: {str(e)}")
        print("Please run: pip install -r requirements.txt")

if __name__ == "__main__":
    print("Amazon Bulk Campaign Generator - Setup Check\n")
    check_directory_structure()
    check_python_path()
    check_dependencies()
    
    print("\nSetup check complete. If any issues were found, please fix them and run this script again.")
    print("\nTo start the application, run:")
    print("streamlit run streamlit_app.py")
