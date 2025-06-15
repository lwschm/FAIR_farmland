"""
Data Standardization Utilities

This module provides functions to standardize data categories across the FAIR Farmland toolkit
to ensure consistent analysis and reporting.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)

# Accessibility standardization mapping
ACCESSIBILITY_MAPPING = {
    # Public variants
    'public': 'Public',
    'Public': 'Public',
    'publicly available': 'Public',
    'Publicly available': 'Public',
    'publicly_available': 'Public',
    'open': 'Public',
    'Open': 'Public',
    'open access': 'Public',
    'Open Access': 'Public',
    
    # Restricted variants
    'restricted': 'Restricted',
    'Restricted': 'Restricted',
    'limited': 'Restricted',
    'Limited': 'Restricted',
    'limited access': 'Restricted',
    'Limited Access': 'Restricted',
    
    # Confidential variants
    'confidential': 'Confidential',
    'Confidential': 'Confidential',
    'private': 'Confidential',
    'Private': 'Confidential',
    
    # Mixed categories
    'confidential and restricted': 'Confidential and Restricted',
    'Confidential and Restricted': 'Confidential and Restricted',
    'restricted and confidential': 'Confidential and Restricted',
    'Restricted and Confidential': 'Confidential and Restricted',
    'private and restricted': 'Confidential and Restricted',
    'Private and Restricted': 'Confidential and Restricted',
    
    # Not specified variants
    'not specified': 'Not Specified',
    'Not specified': 'Not Specified',
    'Not Specified': 'Not Specified',
    'unknown': 'Not Specified',
    'Unknown': 'Not Specified',
    '': 'Not Specified',
    'N/A': 'Not Specified',
    'n/a': 'Not Specified',
    'na': 'Not Specified',
    'NA': 'Not Specified'
}

# Data format standardization mapping
FORMAT_MAPPING = {
    'csv': 'CSV',
    'CSV': 'CSV',
    'json': 'JSON',
    'JSON': 'JSON',
    'xml': 'XML',
    'XML': 'XML',
    'excel': 'Excel',
    'Excel': 'Excel',
    'xls': 'Excel',
    'xlsx': 'Excel',
    'XLS': 'Excel',
    'XLSX': 'Excel',
    'pdf': 'PDF',
    'PDF': 'PDF',
    'shapefile': 'Shapefile',
    'Shapefile': 'Shapefile',
    'shp': 'Shapefile',
    'SHP': 'Shapefile',
    'database': 'Database',
    'Database': 'Database',
    'db': 'Database',
    'DB': 'Database',
    'sql': 'Database',
    'SQL': 'Database',
    'sqlite': 'Database',
    'SQLite': 'Database',
    'mysql': 'Database',
    'MySQL': 'Database',
    'postgresql': 'Database',
    'PostgreSQL': 'Database',
    'text': 'Text',
    'Text': 'Text',
    'txt': 'Text',
    'TXT': 'Text',
    'api': 'API',
    'API': 'API',
    'rest': 'API',
    'REST': 'API',
    'web service': 'API',
    'Web Service': 'API'
}

# Country standardization mapping
COUNTRY_MAPPING = {
    'usa': 'United States',
    'USA': 'United States', 
    'us': 'United States',
    'US': 'United States',
    'united states': 'United States',
    'United states': 'United States',
    'United States of America': 'United States',
    'uk': 'United Kingdom',
    'UK': 'United Kingdom',
    'united kingdom': 'United Kingdom',
    'United kingdom': 'United Kingdom',
    'england': 'United Kingdom',
    'England': 'United Kingdom',
    'scotland': 'United Kingdom',
    'Scotland': 'United Kingdom',
    'wales': 'United Kingdom',
    'Wales': 'United Kingdom',
    'germany': 'Germany',
    'Deutschland': 'Germany',
    'france': 'France',
    'canada': 'Canada',
    'australia': 'Australia',
    'brasil': 'Brazil',
    'brasil': 'Brazil',
    'china': 'China',
    'india': 'India'
}

# Spatial resolution standardization mapping
SPATIAL_RESOLUTION_MAPPING = {
    # Plot level variants
    'plot level': 'Plot Level',
    'Plot level': 'Plot Level',
    'plot-level': 'Plot Level',
    'Plot-level': 'Plot Level',
    'plot_level': 'Plot Level',
    'Plot_level': 'Plot Level',
    'parcel level': 'Plot Level',
    'Parcel level': 'Plot Level',
    'parcel-level': 'Plot Level',
    'Parcel-level': 'Plot Level',
    'field level': 'Plot Level',
    'Field level': 'Plot Level',
    
    # Municipality level variants
    'municipality level': 'Municipality Level',
    'Municipality level': 'Municipality Level',
    'municipal level': 'Municipality Level',
    'Municipal level': 'Municipality Level',
    'municipality-level': 'Municipality Level',
    'Municipality-level': 'Municipality Level',
    
    # County level variants
    'county level': 'County Level',
    'County level': 'County Level',
    'county-level': 'County Level',
    'County-level': 'County Level',
    'county and municipality level': 'County Level',
    'County and municipality level': 'County Level',
    'county and federal state level': 'County Level',
    'County and federal state level': 'County Level',
    
    # District level variants
    'district level': 'District Level',
    'District level': 'District Level',
    'district-level': 'District Level',
    'District-level': 'District Level',
    
    # State/Regional level variants
    'state level': 'State Level',
    'State level': 'State Level',
    'regional level': 'State Level',
    'Regional level': 'State Level',
    'federal state level': 'State Level',
    'Federal state level': 'State Level',
    
    # National level variants
    'national': 'National',
    'National': 'National',
    'national level': 'National',
    'National level': 'National',
    'country level': 'National',
    'Country level': 'National',
    
    # Local variants
    'local': 'Local',
    'Local': 'Local',
    'local level': 'Local',
    'Local level': 'Local',
    'local (within a simulated region)': 'Local',
    'Local (within a simulated region)': 'Local',
    '10 m, plot-level, local': 'Local',
    '10 m, Plot-level, Local': 'Local',
    
    # Specific spatial units
    'plot level and county-level': 'Multi-Level',
    'Plot level and county-level': 'Multi-Level',
    'plot and county level': 'Multi-Level',
    'Plot and county level': 'Multi-Level',
    
    # Zone-based
    'land value zones': 'Zone Level',
    'Land value zones': 'Zone Level',
    'value zones': 'Zone Level',
    'Value zones': 'Zone Level',
    
    # Plot-specific variants
    'plot-specific': 'Plot Level',
    'Plot-specific': 'Plot Level',
    'plot specific': 'Plot Level',
    'Plot specific': 'Plot Level',
    
    # Not specified variants
    'not specified': 'Not Specified',
    'Not specified': 'Not Specified',
    'Not Specified': 'Not Specified',
    'n/a': 'Not Specified',
    'N/A': 'Not Specified',
    'na': 'Not Specified',
    'NA': 'Not Specified',
    'unknown': 'Not Specified',
    'Unknown': 'Not Specified',
    '': 'Not Specified'
}

def standardize_accessibility(value):
    """
    Standardize accessibility values to consistent categories.
    
    Args:
        value: Original accessibility value
        
    Returns:
        str: Standardized accessibility value
    """
    if not value or str(value).strip() == '':
        return 'Not Specified'
    
    str_value = str(value).strip()
    return ACCESSIBILITY_MAPPING.get(str_value, str_value)

def standardize_data_format(value):
    """
    Standardize data format values to consistent categories.
    
    Args:
        value: Original data format value
        
    Returns:
        str: Standardized data format value
    """
    if not value or str(value).strip() == '':
        return 'Not Specified'
    
    str_value = str(value).strip()
    return FORMAT_MAPPING.get(str_value, str_value)

def standardize_country(value):
    """
    Standardize country values to consistent names.
    
    Args:
        value: Original country value
        
    Returns:
        str: Standardized country value
    """
    if not value or str(value).strip() == '':
        return value
    
    str_value = str(value).strip()
    return COUNTRY_MAPPING.get(str_value, str_value)

def standardize_data_source(source):
    """
    Standardize all relevant fields in a data source dictionary.
    
    Args:
        source (dict): Data source dictionary
        
    Returns:
        dict: Data source with standardized fields
    """
    if 'accessibility' in source:
        source['accessibility'] = standardize_accessibility(source['accessibility'])
    
    if 'data_format' in source:
        source['data_format'] = standardize_data_format(source['data_format'])
    
    if 'country' in source:
        source['country'] = standardize_country(source['country'])
    
    return source

def standardize_data_sources(sources):
    """
    Standardize a list of data sources.
    
    Args:
        sources (list): List of data source dictionaries
        
    Returns:
        list: List of standardized data sources
    """
    standardized_sources = []
    
    for source in sources:
        standardized_source = standardize_data_source(source.copy())
        standardized_sources.append(standardized_source)
    
    logger.info(f"Standardized {len(standardized_sources)} data sources")
    
    return standardized_sources

def get_standardization_report(sources):
    """
    Generate a report showing what standardizations were applied.
    
    Args:
        sources (list): List of data source dictionaries
        
    Returns:
        dict: Report of standardization statistics
    """
    accessibility_counts = {}
    format_counts = {}
    country_counts = {}
    
    for source in sources:
        # Count accessibility values
        if 'accessibility' in source and source['accessibility']:
            acc_val = source['accessibility']
            accessibility_counts[acc_val] = accessibility_counts.get(acc_val, 0) + 1
        
        # Count data format values
        if 'data_format' in source and source['data_format']:
            fmt_val = source['data_format']
            format_counts[fmt_val] = format_counts.get(fmt_val, 0) + 1
        
        # Count country values
        if 'country' in source and source['country']:
            country_val = source['country']
            country_counts[country_val] = country_counts.get(country_val, 0) + 1
    
    return {
        'total_sources': len(sources),
        'accessibility_distribution': accessibility_counts,
        'format_distribution': format_counts,
        'country_distribution': country_counts,
        'unique_accessibility_values': len(accessibility_counts),
        'unique_format_values': len(format_counts),
        'unique_country_values': len(country_counts)
    }

def standardize_spatial_resolution(value):
    """
    Standardize spatial resolution values to consistent categories.
    
    Args:
        value: Raw spatial resolution value
        
    Returns:
        str: Standardized spatial resolution category
    """
    if pd.isna(value) or value == '' or value is None:
        return 'Not Specified'
    
    # Convert to string and strip whitespace
    value_str = str(value).strip()
    
    # Direct mapping lookup
    if value_str in SPATIAL_RESOLUTION_MAPPING:
        return SPATIAL_RESOLUTION_MAPPING[value_str]
    
    # Case-insensitive lookup
    value_lower = value_str.lower()
    for key, mapped_value in SPATIAL_RESOLUTION_MAPPING.items():
        if key.lower() == value_lower:
            return mapped_value
    
    # If no mapping found, return original value
    return value_str 