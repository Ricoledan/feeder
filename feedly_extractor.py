#!/usr/bin/env python3
"""
Feeder

A command-line tool to fetch articles from your Feedly feeds with flexible date ranges
and export options.

This is the main entry point that uses the modular structure.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from feedly_extractor.cli import main

if __name__ == "__main__":
    main()