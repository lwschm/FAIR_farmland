"""
FAIR Farmland Data Analysis Toolkit

A comprehensive toolkit for extracting, analyzing, and assessing farmland data 
from scientific publications according to FAIR principles.
"""

__version__ = "1.0.0"
__author__ = "FAIR Farmland Research Team"
__description__ = "Toolkit for FAIR farmland data analysis and metadata extraction"

from .core import ai_metadata_extractor, simple_processor

__all__ = ["ai_metadata_extractor", "simple_processor"] 