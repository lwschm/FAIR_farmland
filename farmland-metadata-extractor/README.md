# Farmland Data Metadata Extractor

A Streamlit application that extracts and analyzes metadata from scientific publications about farmland data. The application uses OpenAI's GPT-4.1 to intelligently extract metadata and assess the FAIRness of farmland data sources mentioned in publications.

## Overview

This tool helps researchers and data managers:
- Extract structured metadata from scientific publications about farmland data
- Identify and document farmland data sources mentioned in publications
- Assess the FAIRness (Findable, Accessible, Interoperable, Reusable) of farmland data sources
- Generate standardized metadata in JSON format

## Features

### Metadata Extraction
- **Publication Metadata**: Extracts title, authors, journal, year, DOI, and other bibliographic information
- **Data Source Identification**: Identifies and documents farmland data sources mentioned in the publication
- **Detailed Data Source Information**: Captures comprehensive details about each data source:
  - Source name and description
  - Geographic coverage (country and region)
  - Temporal coverage (earliest and latest years)
  - Transaction types (sales, leases, etc.)
  - Spatial resolution
  - Accessibility information
  - Number of observations
  - Data format and URL
  - License and metadata standards

### FAIR Assessment
- **Automated Scoring**: Evaluates data sources against FAIR principles
- **Detailed Metrics**: Provides scores and explanations for:
  - Findability (presence of DOI, metadata richness)
  - Accessibility (URL availability, access protocols)
  - Interoperability (standard formats, vocabularies)
  - Reusability (licenses, provenance)
- **Overall Score**: Calculates a comprehensive FAIRness score

### User Interface
- **Interactive Web Interface**: Built with Streamlit for easy use
- **Expandable Data Source Views**: Detailed information in collapsible sections
- **Download Options**: Export metadata in JSON format
- **Visual Metrics**: Clear presentation of FAIR assessment scores

## Installation

### Using Docker (Recommended)

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/farmland-metadata-extractor.git
   cd farmland-metadata-extractor
   ```

2. Set up environment:
   ```bash
   cp env.template .env
   # Edit .env and add your OpenAI API key
   ```

3. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the application at http://localhost:8501

### Local Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/farmland-metadata-extractor.git
   cd farmland-metadata-extractor
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment:
   ```bash
   cp env.template .env
   # Edit .env and add your OpenAI API key
   ```

5. Run the Streamlit app:
   ```bash
   streamlit run app/main.py
   ```

## Usage

1. **Upload a PDF**:
   - Click the "Choose a PDF file" button
   - Select a scientific publication about farmland data

2. **Wait for Processing**:
   - The app will convert the PDF to text
   - OpenAI will analyze the content and extract metadata
   - FAIR assessment will be performed

3. **Review Results**:
   - Check the extracted publication metadata
   - Explore farmland data sources in expandable sections
   - Review FAIR assessment scores and explanations

4. **Download Results**:
   - Click "Download Metadata (JSON)" to save the results
   - The JSON file includes all extracted metadata and FAIR assessment

## Project Structure

```
farmland-metadata-extractor/
├── app/
│   ├── main.py              # Streamlit application
│   ├── pdf_processor.py     # PDF to text conversion
│   └── metadata_extractor.py # OpenAI integration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── .env.template           # Environment variables template
```

## Dependencies

- Python 3.8+
- Streamlit
- OpenAI API
- PDF processing libraries
- Docker (optional)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project is built upon concepts from the FAIR Evaluation Repository (FAIR-ER) project, adapting its approach to metadata standardization and FAIR principles evaluation for farmland data. 