# 🌾 FAIR Farmland Metadata Extraction Tool

[![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A streamlined tool for extracting farmland research metadata from PDF and markdown files using OpenAI Responses API and generating Schema.org-compliant JSON-LD metadata.

## 🎯 What it does

This tool helps researchers **extract structured metadata** from farmland research papers and generate **Schema.org-compliant JSON-LD files** ready for:

- 🌐 **Web indexing** (Google Dataset Search, etc.)
- 📚 **Repository submission** (BonaRes, DataCite, etc.)
- 🔍 **Enhanced discoverability** through search engines
- ⭐ **FAIR principles compliance** assessment

## ✨ Key Features

- **🤖 AI-Powered Extraction**: Uses OpenAI Responses API with structured outputs
- **📄 Multi-Format Support**: Handles both PDF and markdown files intelligently
- **🌐 Schema.org Compliant**: Generates JSON-LD metadata ready for web indexing
- **⭐ FAIR Assessment**: Evaluates datasets against FAIR principles
- **🚀 One-Command Processing**: Simple command-line interface
- **📊 Batch Processing**: Process entire directories of research papers

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/FAIR_farmland.git
cd FAIR_farmland

# Install dependencies
pip install -r requirements.txt
```

### 2. Set up OpenAI API Key

```bash
# Option 1: Environment variable
export OPENAI_API_KEY='your_key_here'

# Option 2: Create .env file
echo 'OPENAI_API_KEY=your_key_here' > .env
```

### 3. Run the Tool

```bash
# Process a directory of papers
python run_farmland_extraction.py path/to/your/papers/

# Specify custom output directory
python run_farmland_extraction.py path/to/papers/ path/to/output/

# Enable verbose logging
python run_farmland_extraction.py path/to/papers/ -v
```

## 📖 Usage Examples

### Process PDF Files
```bash
# Your directory contains PDF files
ls papers/
# farm_study_2023.pdf
# land_prices_germany.pdf
# agricultural_analysis.pdf

python run_farmland_extraction.py papers/
```

### Process Markdown Files
```bash
# Your directory contains markdown files (no conversion needed)
ls documents/
# research_paper_1.md
# dataset_description.md
# farmland_study.markdown

python run_farmland_extraction.py documents/
```

### Mixed File Types
```bash
# Directory with both PDFs and markdown files
ls research_data/
# study1.pdf
# dataset_info.md
# analysis.pdf
# methodology.markdown

python run_farmland_extraction.py research_data/ results/
```

## 📁 Output Structure

After processing, you'll get:

```
output_20241214_143022/
├── study1_schema.json              # Schema.org JSON-LD for study1.pdf
├── dataset_info_schema.json        # Schema.org JSON-LD for dataset_info.md
├── analysis_schema.json            # Schema.org JSON-LD for analysis.pdf
└── processing_summary.json         # Processing summary and statistics
```

### Example Schema.org Output

```json
{
  "@context": "https://schema.org/",
  "@type": "ScholarlyArticle",
  "name": "Farmland Market Analysis in Saxony-Anhalt, 2014-2017",
  "author": [
    {"type": "Person", "name": "Dr. Anna Müller"},
    {"type": "Person", "name": "Jonas Schmidt"}
  ],
  "datePublished": "2025-03-01",
  "keywords": ["farmland sale", "land transaction", "Germany"],
  "dataset": [
    {
      "type": "Dataset",
      "name": "Farmland Sales Transactions – Saxony-Anhalt (2014-2017)",
      "description": "Dataset of 150 farmland sale transactions...",
      "spatialCoverage": {
        "type": "Place",
        "name": "Saxony-Anhalt, DE",
        "geo": {"type": "GeoShape", "box": "50.7 10.9 53.1 13.1"}
      },
      "temporalCoverage": "2014-01/2017-12",
      "variableMeasured": [
        {
          "type": "PropertyValue",
          "name": "Sale Price",
          "unitText": "EUR",
          "description": "Sale price in Euros"
        }
      ]
    }
  ]
}
```

## 🛠️ How It Works

1. **📄 File Detection**: Automatically identifies PDF and markdown files
2. **🔄 Smart Processing**: 
   - PDFs → Convert to markdown using MarkItDown
   - Markdown → Process directly (no conversion)
3. **🤖 AI Extraction**: Uses OpenAI Responses API to extract metadata
4. **🌐 Schema.org Generation**: Creates JSON-LD metadata following Schema.org standards
5. **⭐ FAIR Assessment**: Evaluates datasets against FAIR principles
6. **💾 Clean Output**: Saves well-formatted JSON files ready for use

## 🔧 Command Line Options

```bash
python run_farmland_extraction.py --help
```

### Arguments
- `input_directory`: Directory containing PDF/markdown files (required)
- `output_directory`: Output directory for JSON files (optional, auto-generated if not specified)

### Options
- `-v, --verbose`: Enable detailed logging
- `-h, --help`: Show help message

## 📊 Processing Statistics

After completion, you'll see a summary like:

```
🎉 FARMLAND METADATA EXTRACTION COMPLETE
============================================================
📊 Processing Results:
   Total files: 5
   ✅ Successful: 4
   ❌ Failed: 1
   📄 PDFs converted: 3
   📝 Markdowns processed: 1

📈 Extraction Statistics:
   🌾 Total datasets found: 7
   🎯 Average confidence: 0.89
   ⏱️  Processing time: 45.3 seconds

✅ Successfully generated Schema.org-compliant metadata!
   Ready for web indexing and repository submission
```

## 🎓 What Gets Extracted

The tool identifies and extracts:

### 📖 Publication Metadata
- Title, authors, publication date
- Publisher, DOI, keywords
- License information

### 🗂️ Dataset Information
- Dataset names and descriptions
- Spatial coverage (geographic regions)
- Temporal coverage (time periods)
- Variable descriptions (data columns)
- Access conditions and licenses

### 📊 Specific to Farmland Data
- Transaction types (sales, leases, etc.)
- Land use classifications
- Geographic coverage (states, regions)
- Price information and units
- Buyer/seller categories

## 🔑 Requirements

- **Python 3.11+**
- **OpenAI API Key** (GPT-4 access recommended)
- **Internet connection** for AI processing

### Key Dependencies
- `openai` - OpenAI Responses API
- `markitdown` - PDF to markdown conversion
- `pydantic` - Data validation
- Standard libraries: `pathlib`, `json`, `argparse`

## 🆘 Troubleshooting

### Common Issues

**❌ "OpenAI API key not found"**
```bash
# Set the environment variable
export OPENAI_API_KEY='your_key_here'
# or create a .env file
echo 'OPENAI_API_KEY=your_key_here' > .env
```

**❌ "No PDF or markdown files found"**
- Check your input directory path
- Ensure files have correct extensions: `.pdf`, `.md`, `.markdown`

**❌ PDF conversion fails**
- Verify PDF files are not corrupted or password-protected
- Check file permissions
- Some complex PDFs may not convert properly

**❌ AI extraction fails**
- Check your OpenAI API key and credits
- Ensure you have access to GPT-4
- Very long documents may hit token limits

## 📈 Next Steps After Processing

1. **🔍 Review Output**: Check generated JSON-LD files
2. **✅ Validate**: Use Schema.org validation tools if needed
3. **📤 Submit**: Upload to research data repositories
4. **🌐 Index**: Make discoverable through search engines
5. **📊 Analyze**: Use metadata for research synthesis

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the Responses API with structured outputs
- Schema.org for the metadata vocabulary
- MarkItDown for PDF processing capabilities
- FAIR principles community for data management standards

---

**🌾 Making farmland data FAIR, one paper at a time!** 