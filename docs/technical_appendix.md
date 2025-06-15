# Technical Appendix: Implementation Details

## A. System Architecture and Code Structure

### A.1 Directory Structure
```
FAIR_farmland/
├── 00_pdfpapers/           # Input PDF research papers (21 files)
├── 01_mdpapers/            # Converted markdown files
├── batch_outputs/          # Processing results and metadata
├── consolidated_outputs/   # Final consolidated datasets
├── documentation/          # Project documentation
├── venv_py311/            # Python 3.11 virtual environment
├── batch_pdf_processor.py  # Main batch processing engine
├── run_batch_processor.py  # User interface for batch processing
├── consolidate_data_sources.py  # Consolidation engine
├── run_consolidation.py    # User interface for consolidation
└── .env                   # Environment configuration
```

### A.2 Core Processing Components

#### A.2.1 PDF Processing Engine (`batch_pdf_processor.py`)
```python
class FarmlandPDFProcessor:
    def __init__(self, pdf_dir, markdown_dir, output_dir):
        # Initialize MarkItDown converter
        self.markitdown = MarkItDown()
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv('openaikey'))
        
        # Data validation and storage
        self.processed_papers = []
        self.all_data_sources = []
```

**Key Methods:**
- `convert_pdf_to_markdown()`: PDF→Markdown conversion using MarkItDown
- `extract_data_sources()`: AI-powered metadata extraction 
- `assess_fair_compliance()`: FAIR principles evaluation
- `generate_summary_reports()`: Consolidated reporting

#### A.2.2 Consolidation Engine (`consolidate_data_sources.py`)
```python
class DataSourceConsolidator:
    def __init__(self, input_file, output_dir):
        self.client = OpenAI(api_key=os.getenv('openaikey'))
        self.duplicate_groups = []
        self.deduplicated_sources = []
```

**Key Methods:**
- `identify_duplicates_with_openai()`: Batch-based duplicate detection
- `consolidate_duplicates_with_openai()`: AI-guided source merging
- `calculate_enhanced_fair_scores()`: Enhanced FAIR assessment
- `save_consolidated_outputs()`: Multi-format output generation

## B. Data Extraction Schema

### B.1 Complete Field Definitions

| Field | Type | Description | Source |
|-------|------|-------------|---------|
| `source_name` | String | Official name of the data source | AI-extracted |
| `description` | String | Detailed description of dataset content | AI-extracted |
| `country` | String | Primary country of data coverage | AI-extracted |
| `region` | String | Specific region/state within country | AI-extracted |
| `earliest_year` | Integer | First year of data collection | AI-extracted |
| `latest_year` | Integer | Last year of data collection | AI-extracted |
| `transaction_types` | Array | Types of transactions recorded | AI-extracted |
| `spatial_resolution` | String | Geographic granularity level | AI-extracted |
| `accessibility` | String | Data access level (public/restricted/confidential) | AI-extracted |
| `access_conditions` | String | Specific conditions for data access | AI-extracted |
| `number_of_observations` | Integer | Count of records in dataset | AI-extracted |
| `url` | String | Web address for data access | AI-extracted |
| `data_format` | String | Technical format of the data | AI-extracted |
| `identifier_type` | String | Type of unique identifiers used | AI-extracted |
| `persistent_identifier` | Boolean | Whether dataset has DOI/persistent ID | Rule-based |
| `data_license` | String | Legal licensing terms | AI-extracted |
| `metadata_standard` | String | Metadata standard used | AI-extracted |
| `structured_metadata` | Boolean | Whether metadata is machine-readable | Rule-based |
| `semantic_vocabularies` | Array | Controlled vocabularies used | AI-extracted |
| `provenance_included` | Boolean | Whether data lineage is documented | Rule-based |
| `linked_entities` | Array | Connected datasets or resources | AI-extracted |
| `paper_title` | String | Title of source research paper | System-generated |
| `paper_filename` | String | Filename of source PDF | System-generated |

### B.2 FAIR Assessment Criteria

#### B.2.1 Findability Scoring
```python
def calculate_findability_score(source):
    score = 0.0
    
    # Persistent identifier (+0.4)
    if source.get('persistent_identifier', False):
        score += 0.4
    
    # Accessible URL (+0.3)
    if source.get('url') and source['url'].strip():
        score += 0.3
    
    # Structured metadata (+0.2)
    if source.get('structured_metadata', False):
        score += 0.2
    
    # Semantic vocabularies (+0.1)
    if source.get('semantic_vocabularies') and len(source['semantic_vocabularies']) > 0:
        score += 0.1
    
    return min(score, 1.0)
```

#### B.2.2 Accessibility Scoring
```python
def calculate_accessibility_score(source):
    accessibility = source.get('accessibility', '').lower()
    
    if 'public' in accessibility or 'open' in accessibility:
        return 1.0
    elif 'restricted' in accessibility:
        return 0.3
    elif 'confidential' in accessibility or 'private' in accessibility:
        return 0.0
    else:
        return 0.1  # Unknown accessibility
```

#### B.2.3 Interoperability Scoring
```python
def calculate_interoperability_score(source):
    score = 0.0
    
    # Structured metadata (+0.5)
    if source.get('structured_metadata', False):
        score += 0.5
    
    # Standard data format (+0.3)
    data_format = source.get('data_format', '').lower()
    standard_formats = ['csv', 'json', 'xml', 'rdf', 'geojson']
    if any(fmt in data_format for fmt in standard_formats):
        score += 0.3
    
    # Semantic vocabularies (+0.2)
    if source.get('semantic_vocabularies') and len(source['semantic_vocabularies']) > 0:
        score += 0.2
    
    return min(score, 1.0)
```

#### B.2.4 Reusability Scoring
```python
def calculate_reusability_score(source):
    score = 0.0
    
    # Clear license (+0.4)
    license_info = source.get('data_license', '').lower()
    if license_info and 'not specified' not in license_info:
        score += 0.4
    
    # Provenance information (+0.3)
    if source.get('provenance_included', False):
        score += 0.3
    
    # Structured metadata (+0.2)
    if source.get('structured_metadata', False):
        score += 0.2
    
    # Linked entities (+0.1)
    if source.get('linked_entities') and len(source['linked_entities']) > 0:
        score += 0.1
    
    return min(score, 1.0)
```

## C. AI Prompt Engineering

### C.1 Data Extraction Prompt Template

```python
EXTRACTION_SYSTEM_PROMPT = """You are a data management expert specializing in agricultural research data. 
Your task is to extract structured information about farmland datasets from research papers.

For each data source found in the paper, extract the following information:
- Basic identification (name, description)
- Geographic and temporal coverage
- Access and licensing information
- Technical specifications
- Data quality indicators

Return a JSON array of data source objects. Be precise and conservative in your assessments."""

def create_extraction_prompt(markdown_content, paper_title):
    return f"""
    Extract farmland data sources from this research paper:
    
    Title: {paper_title}
    
    Content:
    {markdown_content}
    
    Focus on datasets used for analysis, not just cited papers.
    """
```

### C.2 Deduplication Prompt Template

```python
DEDUPLICATION_SYSTEM_PROMPT = """You are a data analyst tasked with identifying duplicate farmland data sources.

Analyze the provided data sources and identify which ones refer to the same underlying dataset. Consider:
- Similar source names (accounting for slight variations in naming)
- Same geographic coverage (country/region)
- Overlapping time periods
- Similar URLs or domains
- Similar descriptions of data content

Return ONLY groups of duplicate sources as a JSON array. Each group should contain the indices of sources that are duplicates of each other."""

def create_deduplication_prompt(source_summaries):
    return f"""
    Identify duplicate data sources from this list:
    
    {json.dumps(source_summaries, indent=2)}
    
    Return format: [[0, 3, 7], [2, 5]] for duplicate groups.
    """
```

### C.3 Consolidation Prompt Template

```python
CONSOLIDATION_SYSTEM_PROMPT = """You are tasked with consolidating duplicate farmland data sources into a single, comprehensive entry.

Given multiple sources that refer to the same underlying dataset, create ONE consolidated source that:
1. Combines the most complete and accurate information
2. Uses the most descriptive source name
3. Merges descriptions to capture all relevant details
4. Uses the broadest geographic and temporal coverage
5. Selects the best available URL
6. Combines FAIR assessment scores (use highest scores)
7. Lists all paper titles that reference this source

Return a single JSON object with the consolidated source information."""
```

## D. Quality Control Mechanisms

### D.1 Data Validation Pipeline

```python
def validate_extracted_data(data_source):
    """Validate extracted data source against schema requirements"""
    
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Required fields validation
    required_fields = ['source_name', 'description', 'country']
    for field in required_fields:
        if not data_source.get(field):
            validation_results['errors'].append(f"Missing required field: {field}")
            validation_results['valid'] = False
    
    # Data type validation
    if 'earliest_year' in data_source:
        try:
            year = int(data_source['earliest_year'])
            if year < 1900 or year > 2025:
                validation_results['warnings'].append(f"Unusual year value: {year}")
        except (ValueError, TypeError):
            validation_results['errors'].append("Invalid year format")
    
    # URL validation
    if data_source.get('url'):
        url = data_source['url']
        if not (url.startswith('http://') or url.startswith('https://')):
            validation_results['warnings'].append("URL may be incomplete")
    
    return validation_results
```

### D.2 Error Handling and Recovery

```python
def safe_ai_extraction(content, retries=3):
    """Robust AI extraction with error handling and retries"""
    
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": content}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=4000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error on attempt {attempt + 1}: {e}")
            if attempt == retries - 1:
                return {"sources": []}  # Fallback empty result
                
        except Exception as e:
            logger.error(f"API error on attempt {attempt + 1}: {e}")
            if attempt == retries - 1:
                raise
            
            time.sleep(2 ** attempt)  # Exponential backoff
```

## E. Performance Optimization

### E.1 Batch Processing Strategy

```python
def process_papers_in_batches(papers, batch_size=5):
    """Process papers in batches to manage memory and API limits"""
    
    total_batches = (len(papers) + batch_size - 1) // batch_size
    
    for i in range(0, len(papers), batch_size):
        batch = papers[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        logger.info(f"Processing batch {batch_num}/{total_batches}")
        
        # Process batch with progress tracking
        for paper in batch:
            try:
                result = process_single_paper(paper)
                yield result
            except Exception as e:
                logger.error(f"Failed to process {paper}: {e}")
                continue
```

### E.2 Memory Management

```python
def optimize_memory_usage():
    """Memory optimization strategies for large datasets"""
    
    # Use generators for large data processing
    def data_generator(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                yield json.loads(line)
    
    # Chunk processing for large files
    def process_in_chunks(data, chunk_size=1000):
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            yield process_chunk(chunk)
    
    # Garbage collection optimization
    import gc
    gc.collect()  # Force garbage collection after intensive operations
```

## F. Output Format Specifications

### F.1 JSON Structure

```json
{
  "metadata": {
    "created_at": "2025-06-14T18:25:29.491118",
    "original_sources_count": 31,
    "consolidated_sources_count": 27,
    "duplicate_groups_found": 4,
    "deduplication_savings": 4
  },
  "sources": [
    {
      "source_name": "Committee of Land Valuation Experts",
      "description": "Dataset of land transactions...",
      "country": "Germany",
      "region": "Lower Saxony",
      "earliest_year": 1990,
      "latest_year": 2018,
      "transaction_types": ["sale"],
      "spatial_resolution": "county level",
      "accessibility": "restricted",
      "number_of_observations": 72547,
      "url": "https://www.forland.hu-berlin.de",
      "data_format": "transaction records",
      "data_license": "not specified",
      "findability_score": 0.0,
      "accessibility_score": 0.0,
      "interoperability_score": 0.0,
      "reusability_score": 0.0,
      "overall_fair_score": 0.0,
      "fair_grade": "F",
      "consolidation_info": {
        "original_count": 2,
        "source_papers": ["Paper 1", "Paper 2"],
        "consolidated_at": "2025-06-14T18:25:29.491118",
        "status": "consolidated"
      }
    }
  ],
  "duplicate_groups": [
    [0, 15],  // Indices of sources that were merged
    [5, 12],
    [8, 9, 21],
    [1, 6]
  ]
}
```

### F.2 CSV Structure

The CSV output contains flattened data optimized for spreadsheet analysis:

- **Identification**: source_name, country, region
- **Temporal**: earliest_year, latest_year
- **Content**: description, transaction_types, number_of_observations
- **Technical**: data_format, spatial_resolution, accessibility
- **Access**: url, data_license
- **FAIR Scores**: findability_score, accessibility_score, interoperability_score, reusability_score, overall_fair_score, fair_grade
- **Provenance**: source_papers_count, source_papers, consolidation_status

## G. Monitoring and Logging

### G.1 Comprehensive Logging System

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processing.log'),
        logging.StreamHandler()
    ]
)

def setup_processing_logger(process_name):
    """Setup specialized logger for different processing stages"""
    
    logger = logging.getLogger(process_name)
    
    # Add process-specific file handler
    handler = logging.FileHandler(f'{process_name}.log')
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

### G.2 Progress Tracking

```python
from tqdm import tqdm
import time

def track_processing_progress(items, description):
    """Track processing progress with detailed metrics"""
    
    start_time = time.time()
    processed_count = 0
    error_count = 0
    
    with tqdm(total=len(items), desc=description) as pbar:
        for item in items:
            try:
                result = process_item(item)
                processed_count += 1
                pbar.set_postfix({
                    'processed': processed_count,
                    'errors': error_count,
                    'rate': f"{processed_count/(time.time()-start_time):.1f}/s"
                })
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing {item}: {e}")
            
            pbar.update(1)
    
    return {
        'total_processed': processed_count,
        'total_errors': error_count,
        'processing_time': time.time() - start_time
    }
```

---

*Technical Appendix compiled by: AI-Assisted Data Processing System*  
*Version: 1.0*  
*Last Updated: June 14, 2025* 