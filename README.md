# FAIR Farmland Data Analysis Toolkit

[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive toolkit for extracting, analyzing, and assessing farmland data from scientific publications according to FAIR (Findable, Accessible, Interoperable, Reusable) principles.

## 🌾 Overview

This toolkit helps researchers and data managers:
- **Extract** structured metadata from scientific publications about farmland data
- **Consolidate** and deduplicate farmland data sources across publications
- **Analyze** data patterns, geographic coverage, and temporal trends
- **Assess** FAIRness of farmland data sources
- **Generate** comprehensive reports and visualizations

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/FAIR_farmland.git
   cd FAIR_farmland
   ```

2. **Install the package:**
   ```bash
   pip install -e .
   ```
   
   Or install from requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up configuration:**
   ```bash
   cp config/batch_processing.env .env
   # Edit .env and add your OpenAI API key
   ```

### Basic Usage

1. **Add PDF papers** to `data/input/pdf_papers/`

2. **Run batch processing:**
   ```bash
   python scripts/run_batch_processor.py
   ```

3. **Consolidate data sources:**
   ```bash
   python scripts/run_consolidation.py
   ```

4. **Generate analysis:**
   ```bash
   python scripts/run_analysis.py
   ```

5. **Launch web interface:**
   ```bash
   fair-farmland-webapp
   # or
   streamlit run src/fair_farmland/web_app/main.py
   ```

## 📁 Project Structure

```
FAIR_farmland/
├── src/fair_farmland/           # Main package
│   ├── core/                    # Core processing modules
│   │   ├── batch_processor.py   # PDF processing and metadata extraction
│   │   ├── consolidator.py      # Data source consolidation
│   │   └── analyzer.py          # Data analysis (moved to analysis/)
│   ├── analysis/                # Analysis and visualization
│   │   └── analyzer.py          # Comprehensive data analysis
│   ├── web_app/                 # Streamlit web application
│   │   ├── main.py              # Main Streamlit app
│   │   ├── pdf_processor.py     # PDF processing utilities
│   │   └── metadata_extractor.py # Metadata extraction
│   └── utils/                   # Utility functions
├── data/                        # Data directories
│   ├── input/                   # Input data
│   │   ├── pdf_papers/          # PDF publications
│   │   ├── md_papers/           # Converted markdown files
│   │   └── DataQualityVocabulary/ # Vocabulary data
│   └── output/                  # Generated outputs
│       ├── analysis_outputs/    # Analysis results
│       ├── batch_outputs/       # Batch processing results
│       └── consolidated_outputs/ # Consolidated data
├── scripts/                     # Executable scripts
│   ├── run_batch_processor.py   # Run batch processing
│   ├── run_consolidation.py     # Run consolidation
│   ├── run_analysis.py          # Run analysis
│   └── simple_analysis.py       # Simple analysis script
├── config/                      # Configuration files
│   ├── batch_processing.env     # Environment template
│   ├── requirements_batch.txt   # Batch processing requirements
│   └── web_app_requirements.txt # Web app requirements
├── docs/                        # Documentation
│   ├── technical_appendix.md    # Technical details
│   ├── farmland_data_extraction_process.md
│   ├── CONSOLIDATION_README.md  # Consolidation guide
│   └── BATCH_PROCESSING_README.md # Batch processing guide
├── examples/                    # Example usage
├── tests/                       # Test suite
├── requirements.txt             # Main requirements
├── setup.py                     # Package setup
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🔧 Features

### 1. Batch PDF Processing
- **PDF to Markdown Conversion**: Using MarkItDown for accurate text extraction
- **Metadata Extraction**: AI-powered extraction using OpenAI GPT-4
- **FAIR Assessment**: Automated evaluation of data source FAIRness
- **Structured Output**: JSON and CSV formats for further processing

### 2. Data Consolidation
- **Duplicate Detection**: AI-powered identification of overlapping data sources
- **Smart Merging**: Consolidates duplicate entries while preserving information
- **Enhanced Metadata**: Enriched metadata with consolidation information
- **Quality Metrics**: Improved FAIR scores through consolidation

### 3. Comprehensive Analysis
- **Temporal Analysis**: Data coverage over time
- **Geographic Analysis**: Regional distribution patterns
- **FAIR Assessment Visualization**: Data quality metrics
- **Research Impact**: Analysis of contributing publications
- **Export Options**: Multiple output formats

### 4. Web Interface
- **Interactive Processing**: Upload and process PDFs via web interface
- **Real-time Feedback**: Progress tracking and error handling
- **Visual Results**: Expandable data source views
- **Export Functionality**: Download results in JSON format

## 📊 Analysis Outputs

The toolkit generates comprehensive analysis including:

- **Temporal Coverage Analysis**: Distribution of data start/end years, time spans
- **Geographic Coverage Analysis**: Country and region distributions
- **FAIR Assessment Analysis**: Detailed FAIRness scoring and grading
- **Data Characteristics Analysis**: Format, accessibility, and license patterns
- **Research Papers Analysis**: Contributing publications and impact metrics

## 🛠️ Development

### Setting up Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/FAIR_farmland.git
cd FAIR_farmland

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black src/
flake8 src/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Format code with black
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📋 Requirements

- **Python**: 3.8+
- **OpenAI API Key**: Required for metadata extraction and consolidation
- **Dependencies**: See `requirements.txt` for full list

### Key Dependencies
- `pandas`: Data manipulation and analysis
- `openai`: AI-powered metadata extraction
- `streamlit`: Web interface
- `matplotlib/seaborn`: Data visualization
- `markitdown`: PDF to markdown conversion

## 🔑 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI Configuration
openaikey=your_openai_api_key_here

# Optional: Custom paths
PDF_INPUT_DIR=data/input/pdf_papers
OUTPUT_DIR=data/output
```

### Processing Configuration

Adjust processing parameters in the respective modules:
- **Batch size**: Number of sources processed simultaneously
- **Temperature**: AI model creativity (0.1 for consistent results)
- **Token limits**: Maximum tokens per API call

## 📈 Usage Examples

### Command Line Interface

```bash
# Process all PDFs in input directory
fair-farmland-batch

# Consolidate extracted data sources
fair-farmland-consolidate

# Generate comprehensive analysis
fair-farmland-analyze

# Launch web application
fair-farmland-webapp
```

### Python API

```python
from fair_farmland.core import batch_processor, consolidator
from fair_farmland.analysis import analyzer

# Process PDFs
processor = batch_processor.BatchPDFProcessor()
results = processor.process_all_pdfs()

# Consolidate sources
consolidator_obj = consolidator.DataSourceConsolidator()
consolidated = consolidator_obj.run_consolidation()

# Analyze results
analyzer_obj = analyzer.FarmlandDataAnalyzer()
analyzer_obj.run_complete_analysis()
```

## 🆘 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is set in `.env`
   - Check API key validity and credits

2. **PDF Processing Failures**
   - Verify PDF files are not corrupted
   - Check file permissions
   - Ensure sufficient disk space

3. **Memory Issues**
   - Reduce batch size for large datasets
   - Close unnecessary applications
   - Consider processing in smaller chunks

### Getting Help

- Check the [documentation](docs/) for detailed guides
- Review [existing issues](https://github.com/lwschm/FAIR_farmland/issues)
- Create a new issue with detailed error information

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built upon concepts from the FAIR Evaluation Repository
- Uses OpenAI's GPT-4 for intelligent metadata extraction
- Streamlit for the web interface
- The scientific community for farmland data research



---

**Made with 🌾 for better farmland data management** 