#!/usr/bin/env python3
"""
Batch PDF Processor for Farmland Data Extraction
Processes all PDFs in 00_pdfpapers directory using existing methodologies
"""

import os
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime
import pandas as pd
from tqdm import tqdm
import logging

# Add the farmland-metadata-extractor app to path
sys.path.append('farmland-metadata-extractor/app')

from markitdown import MarkItDown
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BatchPDFProcessor:
    def __init__(self, pdf_directory="00_pdfpapers", output_directory="batch_outputs", md_directory="01_mdpapers"):
        self.pdf_directory = Path(pdf_directory)
        self.output_directory = Path(output_directory)
        self.md_directory = Path(md_directory)
        self.output_directory.mkdir(exist_ok=True)
        self.md_directory.mkdir(exist_ok=True)
        
        # Initialize OpenAI client
        self.openai_api_key = os.getenv('openaikey')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        
        # Initialize MarkItDown
        self.md = MarkItDown()
        
        # Storage for results
        self.results = []
        self.errors = []
        
    def pdf_to_markdown(self, pdf_path):
        """Convert PDF to markdown text using MarkItDown"""
        try:
            result = self.md.convert_local(str(pdf_path))
            return result.text_content
        except Exception as e:
            logger.error(f"Error converting {pdf_path} to markdown: {str(e)}")
            raise
    
    def extract_metadata(self, markdown_text, pdf_filename):
        """Extract metadata using OpenAI API with the existing schema"""
        try:
            system_prompt = """Extract metadata from scientific publications, including authors, journal, title, DOI, year of publication, and detailed information about the farmland data used in the study.

You are tasked with scanning scientific publications to identify and extract critical metadata, as well as providing detailed descriptions of the farmland source(s) used within each study.
Only consider the data which includes farmland data like transaction data of farmland sales or leases or other farmland related data. 
Do not consider additional data like census data or other non-farmland data.
Do not consider the data which includes non-farmland data like weather data or other non-farmland related data.

- Metadata to Extract:
  - Authors
  - Journal
  - Title
  - DOI
  - Year of Publication

- Data Description: Include a detailed summary of each data source used in the study, providing contextual information such as:
  - Type of Data
  - Purpose within the study
  - Collection methods
  - Sample sizes
  - Key findings or conclusions drawn from the data
  - Any unique characteristics or limitations of the data

# Steps

1. **Identify Metadata**: Scan the publication for metadata sections or headers that typically contain details like authors, journal name, title, DOI, and publication year.
2. **Locate Data Sources**: Examine sections of the publication like "Methods," "Materials and Methods," or "Data" for information on the datasets used.
3. **Extract and Describe Data**: Extract pertinent information about each dataset, including type, purpose, collection methods, sample sizes, and any unique details about the data.
4. **Summarize each dataset:** Provide a concise yet comprehensive description of each dataset, highlighting its role and significance in the study.

# Notes

- Ensure accurate extraction and detail, especially regarding data source descriptions, to support comprehensible summaries for future use.
- Pay attention to the context and nuances in the description of data sources, as these can vary widely between studies."""

            user_prompt = f"Extract metadata from the scientific publication and list the data sources used in the model.\n\n{markdown_text}"
            
            # Define the JSON schema (same as in the original)
            schema = {
                "type": "object",
                "properties": {
                    "metadata": {
                        "type": "object",
                        "description": "Bibliographic and descriptive metadata of the scientific publication.",
                        "properties": {
                            "authors": {
                                "type": "array",
                                "description": "A list of full names of all authors as stated in the publication.",
                                "items": {"type": "string"}
                            },
                            "journal": {
                                "type": "string",
                                "description": "The name of the scientific journal in which the article was published."
                            },
                            "title": {
                                "type": "string",
                                "description": "The full title of the publication."
                            },
                            "doi": {
                                "type": "string",
                                "description": "The Digital Object Identifier (DOI) of the publication."
                            },
                            "year": {
                                "type": "number",
                                "description": "The year the article was published."
                            },
                            "publisher": {
                                "type": "string",
                                "description": "The name of the organization or company that published the article."
                            },
                            "language": {
                                "type": "string",
                                "description": "The primary language of the publication."
                            },
                            "keywords": {
                                "type": "array",
                                "description": "A list of keywords describing the subject or topic areas of the publication.",
                                "items": {"type": "string"}
                            },
                            "license": {
                                "type": "string",
                                "description": "The usage license of the publication."
                            }
                        },
                        "required": ["authors", "journal", "title", "doi", "year", "publisher", "language", "keywords", "license"],
                        "additionalProperties": False
                    },
                    "data_sources": {
                        "type": "array",
                        "description": "A list of datasets used or referenced in the publication.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source_name": {"type": "string"},
                                "description": {"type": "string"},
                                "country": {"type": "string"},
                                "region": {"type": "string"},
                                "earliest_year": {"type": "number"},
                                "latest_year": {"type": "number"},
                                "transaction_types": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "spatial_resolution": {"type": "string"},
                                "accessibility": {"type": "string"},
                                "access_conditions": {"type": "string"},
                                "number_of_observations": {"type": "integer"},
                                "url": {"type": "string"},
                                "data_format": {"type": "string"},
                                "identifier_type": {"type": "string"},
                                "persistent_identifier": {"type": "boolean"},
                                "data_license": {"type": "string"},
                                "metadata_standard": {"type": "string"},
                                "structured_metadata": {"type": "boolean"},
                                "semantic_vocabularies": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "provenance_included": {"type": "boolean"},
                                "linked_entities": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": [
                                "source_name", "description", "country", "region", "earliest_year", "latest_year",
                                "transaction_types", "spatial_resolution", "accessibility", "access_conditions",
                                "number_of_observations", "url", "data_format", "identifier_type", "persistent_identifier",
                                "data_license", "metadata_standard", "structured_metadata", "semantic_vocabularies",
                                "provenance_included", "linked_entities"
                            ]
                        }
                    },
                    "assessment": {
                        "type": "object",
                        "properties": {
                            "findability": {"type": "number"},
                            "findability_reason": {"type": "string"},
                            "accessibility": {"type": "number"},
                            "accessibility_reason": {"type": "string"},
                            "interoperability": {"type": "number"},
                            "interoperability_reason": {"type": "string"},
                            "reusability": {"type": "number"},
                            "reusability_reason": {"type": "string"}
                        },
                        "required": [
                            "findability", "findability_reason", "accessibility", "accessibility_reason",
                            "interoperability", "interoperability_reason", "reusability", "reusability_reason"
                        ]
                    }
                },
                "required": ["metadata", "data_sources", "assessment"]
            }
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_schema", "json_schema": {"name": "metadata_extraction", "schema": schema}},
                temperature=0.1,
                max_tokens=4000
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error extracting metadata for {pdf_filename}: {str(e)}")
            return self._create_error_response(pdf_filename, str(e))
    
    def _create_error_response(self, filename, error_msg):
        """Create a minimal response structure for failed extractions"""
        return {
            "metadata": {
                "authors": [f"Error processing {filename}"],
                "journal": "Error",
                "title": f"Failed to process: {error_msg[:100]}",
                "doi": "Unknown",
                "year": 0,
                "publisher": "Unknown",
                "language": "en",
                "keywords": ["error"],
                "license": "Unknown"
            },
            "data_sources": [],
            "assessment": {
                "findability": 0.0,
                "findability_reason": "Processing failed",
                "accessibility": 0.0,
                "accessibility_reason": "Processing failed",
                "interoperability": 0.0,
                "interoperability_reason": "Processing failed",
                "reusability": 0.0,
                "reusability_reason": "Processing failed"
            },
            "processing_error": error_msg
        }
    
    def process_single_pdf(self, pdf_path):
        """Process a single PDF file"""
        logger.info(f"Processing {pdf_path.name}")
        
        try:
            # Convert PDF to markdown
            markdown_text = self.pdf_to_markdown(pdf_path)
            
            # Save markdown file to 01_mdpapers directory
            md_file = self.md_directory / f"{pdf_path.stem}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown_text)
            logger.info(f"Saved markdown to {md_file}")
            
            # Extract metadata
            metadata = self.extract_metadata(markdown_text, pdf_path.name)
            
            # Add processing metadata
            metadata["processing_info"] = {
                "filename": pdf_path.name,
                "markdown_file": str(md_file),
                "processed_at": datetime.now().isoformat(),
                "file_size": pdf_path.stat().st_size,
                "markdown_length": len(markdown_text)
            }
            
            # Save individual result
            output_file = self.output_directory / f"{pdf_path.stem}_metadata.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.results.append(metadata)
            logger.info(f"Successfully processed {pdf_path.name}")
            
            return metadata
            
        except Exception as e:
            error_info = {
                "filename": pdf_path.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.errors.append(error_info)
            logger.error(f"Failed to process {pdf_path.name}: {str(e)}")
            return None
    
    def process_all_pdfs(self):
        """Process all PDFs in the directory"""
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Process each PDF with progress bar
        for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):
            self.process_single_pdf(pdf_path)
        
        # Generate consolidated outputs
        self.generate_consolidated_outputs()
        
        logger.info(f"Batch processing complete. Processed {len(self.results)} files successfully, {len(self.errors)} errors")
    
    def generate_consolidated_outputs(self):
        """Generate consolidated reports and analyses"""
        if not self.results:
            logger.warning("No successful results to consolidate")
            return
        
        # Save consolidated JSON
        consolidated_file = self.output_directory / "consolidated_metadata.json"
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total_papers": len(self.results),
                    "processing_errors": len(self.errors),
                    "generated_at": datetime.now().isoformat()
                },
                "papers": self.results,
                "errors": self.errors
            }, f, indent=2, ensure_ascii=False)
        
        # Generate CSV summary
        self.generate_csv_summary()
        
        # Generate FAIR assessment report
        self.generate_fair_report()
        
        # Generate data sources summary
        self.generate_data_sources_summary()
        
        logger.info("Consolidated outputs generated successfully")
    
    def generate_csv_summary(self):
        """Generate CSV summary of all papers"""
        summary_data = []
        
        for result in self.results:
            metadata = result["metadata"]
            assessment = result["assessment"]
            
            row = {
                "filename": result.get("processing_info", {}).get("filename", "unknown"),
                "title": metadata.get("title", ""),
                "authors": "; ".join(metadata.get("authors", [])),
                "journal": metadata.get("journal", ""),
                "year": metadata.get("year", 0),
                "doi": metadata.get("doi", ""),
                "num_data_sources": len(result.get("data_sources", [])),
                "findability_score": assessment.get("findability", 0),
                "accessibility_score": assessment.get("accessibility", 0),
                "interoperability_score": assessment.get("interoperability", 0),
                "reusability_score": assessment.get("reusability", 0),
                "overall_fair_score": (
                    assessment.get("findability", 0) + 
                    assessment.get("accessibility", 0) + 
                    assessment.get("interoperability", 0) + 
                    assessment.get("reusability", 0)
                ) / 4
            }
            summary_data.append(row)
        
        df = pd.DataFrame(summary_data)
        csv_file = self.output_directory / "papers_summary.csv"
        df.to_csv(csv_file, index=False)
        logger.info(f"CSV summary saved to {csv_file}")
    
    def generate_fair_report(self):
        """Generate detailed FAIR assessment report"""
        fair_scores = {
            "findability": [],
            "accessibility": [],
            "interoperability": [],
            "reusability": []
        }
        
        for result in self.results:
            assessment = result["assessment"]
            for dimension in fair_scores.keys():
                fair_scores[dimension].append(assessment.get(dimension, 0))
        
        # Calculate statistics
        fair_stats = {}
        for dimension, scores in fair_scores.items():
            fair_stats[dimension] = {
                "mean": sum(scores) / len(scores) if scores else 0,
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0,
                "count": len(scores)
            }
        
        # Save FAIR report
        fair_report = {
            "summary": fair_stats,
            "generated_at": datetime.now().isoformat(),
            "total_papers": len(self.results)
        }
        
        fair_file = self.output_directory / "fair_assessment_report.json"
        with open(fair_file, 'w', encoding='utf-8') as f:
            json.dump(fair_report, f, indent=2)
        
        logger.info(f"FAIR assessment report saved to {fair_file}")
    
    def generate_data_sources_summary(self):
        """Generate summary of all data sources found"""
        all_sources = []
        
        for result in self.results:
            paper_title = result["metadata"].get("title", "Unknown")
            for source in result.get("data_sources", []):
                source_info = source.copy()
                source_info["paper_title"] = paper_title
                source_info["paper_filename"] = result.get("processing_info", {}).get("filename", "unknown")
                all_sources.append(source_info)
        
        # Save data sources summary
        sources_file = self.output_directory / "data_sources_summary.json"
        with open(sources_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_data_sources": len(all_sources),
                "sources": all_sources,
                "generated_at": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        # Generate CSV of data sources
        if all_sources:
            sources_df = pd.json_normalize(all_sources)
            sources_csv = self.output_directory / "data_sources.csv"
            sources_df.to_csv(sources_csv, index=False)
            logger.info(f"Data sources summary saved to {sources_file} and {sources_csv}")

def main():
    """Main execution function"""
    try:
        processor = BatchPDFProcessor()
        processor.process_all_pdfs()
        print(f"\nBatch processing completed!")
        print(f"Results saved to: {processor.output_directory}")
        print(f"Successfully processed: {len(processor.results)} files")
        print(f"Errors: {len(processor.errors)} files")
        
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 