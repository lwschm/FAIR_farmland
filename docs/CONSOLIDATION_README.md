# Farmland Data Sources Consolidation & Deduplication Tool

## Overview

This tool analyzes the farmland data sources extracted from research papers and uses OpenAI to identify and consolidate duplicate/overlapping sources, creating a final comprehensive dataset with enhanced FAIR assessments.

## Features

### 🔍 **Intelligent Duplicate Detection**
- Uses OpenAI GPT-4o to identify duplicate data sources
- Considers multiple factors:
  - Similar source names (accounting for variations)
  - Geographic coverage overlap
  - Temporal period overlap
  - URL similarity
  - Content description similarity

### 🔄 **Smart Consolidation**
- Merges duplicate sources into comprehensive single entries
- Preserves the most complete information from all duplicates
- Uses the most descriptive names and broadest coverage
- Combines FAIR scores (uses highest available scores)
- Tracks which papers referenced each consolidated source

### 📊 **Enhanced FAIR Assessment**
- Recalculates FAIR scores for consolidated sources
- Provides letter grades (A-F) for easy interpretation
- Generates comprehensive FAIR statistics

### 📁 **Multiple Output Formats**
- **Detailed JSON**: Complete consolidated dataset with metadata
- **Analysis-ready CSV**: Flattened format for spreadsheet analysis
- **Consolidation Report**: Summary statistics and process details

## Prerequisites

1. **Completed Batch Processing**: Must have run the batch PDF processor first
2. **Required Input**: `batch_outputs/data_sources_summary.json`
3. **OpenAI API Key**: Set as `openaikey` in `.env` file
4. **Python Dependencies**: Same as batch processor (pandas, openai, python-dotenv)

## Quick Start

### 1. Verify Prerequisites
```bash
# Check that batch processing was completed
ls batch_outputs/data_sources_summary.json

# Verify API key is set
grep "openaikey" .env
```

### 2. Run Consolidation
```bash
python run_consolidation.py
```

The tool will:
- Validate your setup
- Show you what it will do
- Ask for confirmation
- Process all data sources
- Generate consolidated outputs

## Output Files

### `consolidated_outputs/consolidated_farmland_sources_YYYYMMDD_HHMMSS.json`
Complete consolidated dataset including:
- Metadata (original vs consolidated counts, etc.)
- All consolidated sources with full details
- Information about which sources were merged
- Duplicate groups identified

### `consolidated_outputs/consolidated_farmland_sources_YYYYMMDD_HHMMSS.csv`
Analysis-ready spreadsheet format with columns:
- `source_name`: Name of the data source
- `description`: Brief description (truncated for readability)
- `country`, `region`: Geographic coverage
- `earliest_year`, `latest_year`: Temporal coverage
- `transaction_types`: Types of farmland transactions covered
- `spatial_resolution`: Geographic detail level
- `accessibility`: How to access the data
- `number_of_observations`: Data volume
- `data_format`: Format of the dataset
- `url`: Access URL
- `data_license`: Licensing information
- `findability_score`, `accessibility_score`, `interoperability_score`, `reusability_score`: Individual FAIR dimensions
- `overall_fair_score`: Combined FAIR score (0-1)
- `fair_grade`: Letter grade (A-F)
- `source_papers_count`: Number of papers that referenced this source
- `source_papers`: List of papers (separated by semicolons)
- `consolidation_status`: Whether source was consolidated or unique

### `consolidated_outputs/consolidation_report.json`
Summary statistics including:
- Original vs consolidated source counts
- Deduplication efficiency metrics
- FAIR score statistics
- Quality assessments

## Advanced Usage

### Custom Input File
```python
from consolidate_data_sources import DataSourceConsolidator

consolidator = DataSourceConsolidator(
    input_file="path/to/your/data_sources.json",
    output_dir="custom_output_directory"
)
results = consolidator.run_consolidation()
```

### Batch Size Adjustment
For very large datasets, you can adjust the batch size for OpenAI processing:

```python
consolidator = DataSourceConsolidator()
consolidator.load_data_sources()
consolidator.identify_duplicates_with_openai(batch_size=5)  # Smaller batches
# ... continue with rest of process
```

## Process Details

### Phase 1: Data Loading
- Loads all data sources from the batch processing summary
- Validates data structure and completeness

### Phase 2: Duplicate Detection
- Processes sources in batches to manage API token limits
- Uses sophisticated OpenAI prompts to identify duplicates
- Considers multiple similarity factors
- Groups related sources together

### Phase 3: Consolidation
- Merges duplicate groups using OpenAI intelligence
- Preserves the most complete information
- Combines FAIR assessments optimally
- Adds consolidation metadata

### Phase 4: Enhancement
- Recalculates FAIR scores for consolidated sources
- Adds letter grades for easy interpretation
- Generates comprehensive statistics

### Phase 5: Output Generation
- Creates timestamped files
- Generates both JSON and CSV formats
- Creates detailed consolidation report

## Cost Estimation

**OpenAI API Usage**: 
- ~0.5-2 cents per data source for duplicate detection
- ~1-3 cents per duplicate group for consolidation
- Total: Usually $2-10 for typical research paper datasets

**Processing Time**:
- 2-5 seconds per source for duplicate detection
- 5-10 seconds per duplicate group for consolidation
- Total: 5-20 minutes for typical datasets

## Troubleshooting

### "Input file not found"
- Run the batch PDF processor first: `python run_batch_processor.py`
- Ensure it completed successfully and generated the summary file

### "OpenAI API key not found"
- Add your key to `.env`: `openaikey=your_actual_api_key_here`
- Ensure the key has sufficient credits

### "No duplicates found"
This is normal if your dataset has very diverse sources. The tool will still:
- Process all sources
- Enhance FAIR assessments
- Generate consolidated outputs

### Memory Issues
For very large datasets (1000+ sources):
- Reduce batch size: modify the `batch_size=10` parameter to `batch_size=5`
- Process in chunks: split your input file and run multiple times

### Rate Limiting
If you hit OpenAI rate limits:
- The tool includes automatic retry logic
- Wait a few minutes and restart
- Consider reducing batch size

## Quality Assurance

The tool includes multiple quality checks:
- **Input Validation**: Ensures proper file structure
- **API Response Validation**: Handles unexpected OpenAI responses
- **Fallback Mechanisms**: Uses intelligent defaults if AI consolidation fails
- **Comprehensive Logging**: Tracks all operations for debugging
- **Progress Reporting**: Shows real-time status updates

## Integration

The consolidated outputs are designed to integrate with:
- **Excel/Google Sheets**: Use the CSV file
- **R/Python Analysis**: Load the JSON file
- **Database Systems**: Import the CSV with proper data types
- **Visualization Tools**: Both formats work with Tableau, Power BI, etc.

## Support Files

- `consolidation.log`: Detailed processing log
- `consolidated_outputs/`: All output files directory
- `.env`: Configuration file (keep secure!)

## Next Steps

After consolidation, you can:

1. **Analyze Geographic Distribution**: Map sources by country/region
2. **Assess Temporal Coverage**: Identify data gaps across time periods
3. **Evaluate FAIR Compliance**: Focus improvement efforts on low-scoring sources
4. **Plan Data Integration**: Use consolidated sources for meta-analysis
5. **Generate Research Insights**: Analyze patterns across farmland data sources

---

For additional support or feature requests, refer to the main project documentation. 