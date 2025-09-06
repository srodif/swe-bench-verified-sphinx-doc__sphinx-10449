#!/usr/bin/env python3
"""Test script to reproduce the issue with autodoc_typehints="description" and classes."""

import tempfile
import os
import subprocess
import sys
from pathlib import Path

def create_test_setup():
    """Create a temporary directory with the test setup."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix='sphinx_test_')
    temp_path = Path(temp_dir)
    
    # Create package directory
    package_dir = temp_path / 'sample_package'
    package_dir.mkdir()
    
    # Create __init__.py with the test class
    init_file = package_dir / '__init__.py'
    init_file.write_text('''class Square:
    """A class representing a square figure."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
''')
    
    # Create docs directory
    docs_dir = temp_path / 'docs'
    docs_dir.mkdir()
    
    # Create conf.py
    conf_file = docs_dir / 'conf.py'
    conf_file.write_text('''
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'test-project'
extensions = ['sphinx.ext.autodoc']
autodoc_typehints = "description"
''')
    
    # Create index.rst
    index_file = docs_dir / 'index.rst'
    index_file.write_text('''Test Documentation
==================

.. autoclass:: sample_package.Square
   :members:
''')
    
    return str(temp_path)

def build_docs(temp_dir):
    """Build the documentation and return the output."""
    docs_dir = os.path.join(temp_dir, 'docs')
    build_dir = os.path.join(docs_dir, '_build')
    
    # Run sphinx-build
    cmd = [sys.executable, '-m', 'sphinx', '-b', 'text', docs_dir, build_dir]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=temp_dir)
    
    if result.returncode != 0:
        print("Sphinx build failed:")
        print(result.stdout)
        print(result.stderr)
        return None
    
    # Read the output
    output_file = os.path.join(build_dir, 'index.txt')
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            return f.read()
    return None

def main():
    print("Reproducing the issue...")
    temp_dir = create_test_setup()
    
    try:
        output = build_docs(temp_dir)
        if output:
            print("Generated documentation:")
            print("=" * 50)
            print(output)
            print("=" * 50)
            
            # Check if the issue exists
            if "Return type:" in output and "None" in output:
                print("\n❌ ISSUE CONFIRMED: Class shows 'Return type: None'")
                return True
            else:
                print("\n✅ No issue found")
                return False
        else:
            print("Failed to build documentation")
            return False
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    main()