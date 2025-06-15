"""
FAIR Farmland Data Analysis Toolkit

A comprehensive toolkit for extracting, analyzing, and assessing farmland data 
from scientific publications according to FAIR principles.
"""

__version__ = "1.0.0"
__author__ = "FAIR Farmland Research Team"
__description__ = "Toolkit for FAIR farmland data analysis and metadata extraction"

from .core import batch_processor, consolidator, analyzer
from .web_app import main as web_app

__all__ = ["batch_processor", "consolidator", "analyzer", "web_app"] 