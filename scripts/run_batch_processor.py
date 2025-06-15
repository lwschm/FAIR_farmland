#!/usr/bin/env python3
"""
Run script for batch PDF processing.
Updated to work with the new package structure.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from fair_farmland.core.batch_processor import BatchPDFProcessor, main

if __name__ == "__main__":
    main() 