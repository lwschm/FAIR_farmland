#!/usr/bin/env python3
"""
Run script for data consolidation.
Updated to work with the new package structure.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from fair_farmland.core.consolidator import DataSourceConsolidator, main

if __name__ == "__main__":
    main() 