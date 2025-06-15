# 🌾 Farmland PDF Batch Processing System

This system processes all PDF files in the `00_pdfpapers` directory using the existing farmland metadata extraction methodologies, now extended for batch processing.

## ✨ Features

- **PDF to Markdown Conversion**: Uses Microsoft's MarkItDown for high-quality text extraction
- **Metadata Extraction**: Leverages OpenAI GPT-4 for structured metadata extraction
- **FAIR Assessment**: Evaluates data sources against FAIR principles (Findable, Accessible, Interoperable, Reusable)
- **Batch Processing**: Processes all PDFs automatically with progress tracking
- **Multiple Output Formats**: JSON, CSV, and consolidated reports

## 📁 Output Structure

```
01_mdpapers/           # Converted markdown files from PDFs
batch_outputs/         # Processing results
├── *_metadata.json    # Individual PDF metadata
├── consolidated_metadata.json  # All results combined
├── papers_summary.csv # Summary in CSV format
├── data_sources.csv   # All data sources found
├── data_sources_summary.json
└── fair_assessment_report.json
```

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.11+ (installed via Homebrew)
- OpenAI API key

### 2. Environment Setup
The system uses a Python 3.11 virtual environment located at `venv_py311/`.

Activate the environment:
```bash
source venv_py311/bin/activate
```

### 3. Configure API Key
Edit the `batch_processing.env` file and replace the placeholder with your actual OpenAI API key:
```bash
OPENAI_API_KEY=your_actual_api_key_here
```

### 4. Run Processing
Execute the batch processor:
```bash
source venv_py311/bin/activate
python run_batch_processor.py
```

## 📊 What Gets Extracted

### Publication Metadata
- Authors, journal, title, DOI, year
- Publisher, language, keywords, license

### Data Source Information
For each farmland dataset mentioned in papers:
- Source name and description
- Geographic coverage (country/region)
- Temporal coverage (earliest/latest years)
- Transaction types (sales, leases, etc.)
- Spatial resolution and accessibility
- Data format, URLs, licenses
- FAIR compliance metrics

### FAIR Assessment
Each data source is scored on:
- **Findability**: DOI presence, metadata quality
- **Accessibility**: URL availability, access protocols
- **Interoperability**: Standard formats, vocabularies
- **Reusability**: Licenses, provenance information

## 🔧 Technical Details

### Architecture
- **PDF Processing**: MarkItDown v0.1.2 with full dependency support
- **LLM Integration**: OpenAI GPT-4 with structured JSON schema
- **Error Handling**: Comprehensive logging and error recovery
- **Progress Tracking**: Real-time progress bars and status updates

### Dependencies
All dependencies are pre-installed in the `venv_py311` environment:
- markitdown[all] 0.1.2
- openai 1.86.0
- pandas, tqdm, python-dotenv
- And all required PDF/document processing libraries

## 📈 Performance

The system processes approximately:
- 1-3 minutes per PDF (depending on size and complexity)
- Concurrent API calls optimized for rate limits
- Automatic retry logic for network issues

## ⚠️ Important Notes

1. **API Costs**: Processing uses OpenAI API calls (~$0.01-0.10 per PDF depending on length)
2. **Rate Limits**: Built-in handling for OpenAI rate limits
3. **Error Recovery**: Failed PDFs are logged but don't stop the entire batch
4. **Data Storage**: All intermediate results are saved for review/reprocessing

## 🔍 Troubleshooting

### Common Issues

**"No API key" error**:
- Ensure `batch_processing.env` contains your actual OpenAI API key
- Check that the file is in the project root directory

**Import errors**:
- Make sure you're using the Python 3.11 virtual environment: `source venv_py311/bin/activate`

**PDF processing failures**:
- Check `batch_processing.log` for detailed error messages
- Individual failures won't stop the entire batch

### Getting Help

Check the log file `batch_processing.log` for detailed processing information and error messages.

## 📚 Research Context

This system is designed specifically for farmland data research, focusing on:
- Agricultural land transaction data
- Farm-level datasets
- Spatial agricultural information
- Farmland market research papers

Non-farmland data (weather, census, etc.) is filtered out during processing to maintain focus on core farmland research datasets. 