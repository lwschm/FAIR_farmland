#!/usr/bin/env python3
"""
Simple File Processor for Farmland Metadata Extraction

This module provides a streamlined approach to process PDF and markdown files
and extract farmland metadata using OpenAI Responses API.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Union

from markitdown import MarkItDown
from .ai_metadata_extractor import AIMetadataExtractor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleFileProcessor:
    """Simple processor for farmland metadata extraction from PDF/markdown files"""
    
    def __init__(self, output_directory: Union[str, Path] = None):
        """
        Initialize the simple file processor
        
        Args:
            output_directory: Directory to save output files (default: ./output)
        """
        self.output_directory = Path(output_directory) if output_directory else Path("output")
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.md_converter = MarkItDown()
        self.ai_extractor = AIMetadataExtractor()
        
        # Processing statistics
        self.stats = {
            "files_processed": 0,
            "files_failed": 0,
            "pdfs_converted": 0,
            "markdowns_processed": 0,
            "total_datasets_found": 0,
            "processing_start_time": None,
            "processing_end_time": None
        }
    
    def is_pdf_file(self, file_path: Path) -> bool:
        """Check if file is a PDF"""
        return file_path.suffix.lower() == '.pdf'
    
    def is_markdown_file(self, file_path: Path) -> bool:
        """Check if file is a markdown file"""
        return file_path.suffix.lower() in ['.md', '.markdown']
    
    def convert_pdf_to_markdown(self, pdf_path: Path) -> str:
        """
        Convert PDF file to markdown text
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            str: Markdown content
        """
        try:
            logger.info(f"Converting PDF to markdown: {pdf_path.name}")
            result = self.md_converter.convert(str(pdf_path))
            self.stats["pdfs_converted"] += 1
            return result.text_content
        except Exception as e:
            logger.error(f"Failed to convert PDF {pdf_path.name}: {str(e)}")
            raise
    
    def read_markdown_file(self, md_path: Path) -> str:
        """
        Read markdown file content
        
        Args:
            md_path: Path to markdown file
            
        Returns:
            str: Markdown content
        """
        try:
            logger.info(f"Reading markdown file: {md_path.name}")
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.stats["markdowns_processed"] += 1
            return content
        except Exception as e:
            logger.error(f"Failed to read markdown {md_path.name}: {str(e)}")
            raise
    
    def process_single_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single file (PDF or markdown) and extract metadata
        
        Args:
            file_path: Path to file to process
            
        Returns:
            Dict: Processing result with metadata and status
        """
        file_path = Path(file_path)
        
        try:
            # Get markdown content based on file type
            if self.is_pdf_file(file_path):
                markdown_content = self.convert_pdf_to_markdown(file_path)
            elif self.is_markdown_file(file_path):
                markdown_content = self.read_markdown_file(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
            # Extract metadata using AI
            logger.info(f"Extracting metadata from: {file_path.name}")
            extraction_result = self.ai_extractor.extract_metadata(
                markdown_content, 
                file_path.name
            )
            
            # Generate JSON-LD output
            jsonld_data = self.ai_extractor.extract_to_jsonld(
                markdown_content,
                file_path.name
            )
            
            # Save Schema.org JSON-LD file
            output_filename = f"{file_path.stem}_schema.json"
            output_path = self.output_directory / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(jsonld_data, f, indent=2, ensure_ascii=False)
            
            # Update statistics
            self.stats["files_processed"] += 1
            self.stats["total_datasets_found"] += len(extraction_result.scholarly_article.dataset)
            
            result = {
                "status": "success",
                "input_file": str(file_path),
                "output_file": str(output_path),
                "extraction_confidence": extraction_result.extraction_confidence,
                "datasets_found": len(extraction_result.scholarly_article.dataset),
                "article_title": extraction_result.scholarly_article.name,
                "authors": [author.name for author in extraction_result.scholarly_article.author],
                "processing_time": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Successfully processed: {file_path.name}")
            logger.info(f"   Output: {output_filename}")
            logger.info(f"   Confidence: {extraction_result.extraction_confidence:.2f}")
            logger.info(f"   Datasets found: {len(extraction_result.scholarly_article.dataset)}")
            
            return result
            
        except Exception as e:
            self.stats["files_failed"] += 1
            error_result = {
                "status": "error",
                "input_file": str(file_path),
                "error": str(e),
                "processing_time": datetime.now().isoformat()
            }
            
            logger.error(f"❌ Failed to process: {file_path.name} - {str(e)}")
            return error_result
    
    def process_directory(self, input_directory: Union[str, Path]) -> Dict[str, Any]:
        """
        Process all PDF and markdown files in a directory
        
        Args:
            input_directory: Directory containing files to process
            
        Returns:
            Dict: Summary of processing results
        """
        input_directory = Path(input_directory)
        
        if not input_directory.exists():
            raise ValueError(f"Input directory does not exist: {input_directory}")
        
        # Find all PDF and markdown files
        pdf_files = list(input_directory.glob("*.pdf"))
        md_files = list(input_directory.glob("*.md")) + list(input_directory.glob("*.markdown"))
        all_files = pdf_files + md_files
        
        if not all_files:
            logger.warning(f"No PDF or markdown files found in: {input_directory}")
            return {"error": "No suitable files found"}
        
        logger.info(f"Found {len(all_files)} files to process:")
        logger.info(f"  - {len(pdf_files)} PDF files")
        logger.info(f"  - {len(md_files)} markdown files")
        
        # Initialize processing
        self.stats["processing_start_time"] = datetime.now()
        results = []
        
        # Process each file
        for file_path in all_files:
            result = self.process_single_file(file_path)
            results.append(result)
        
        # Finalize processing
        self.stats["processing_end_time"] = datetime.now()
        processing_duration = (self.stats["processing_end_time"] - self.stats["processing_start_time"]).total_seconds()
        
        # Generate summary
        successful_results = [r for r in results if r["status"] == "success"]
        failed_results = [r for r in results if r["status"] == "error"]
        
        summary = {
            "processing_summary": {
                "total_files": len(all_files),
                "successful_files": len(successful_results),
                "failed_files": len(failed_results),
                "pdfs_converted": self.stats["pdfs_converted"],
                "markdowns_processed": self.stats["markdowns_processed"],
                "total_datasets_found": self.stats["total_datasets_found"],
                "processing_duration_seconds": processing_duration,
                "average_confidence": sum(r.get("extraction_confidence", 0) for r in successful_results) / len(successful_results) if successful_results else 0,
                "output_directory": str(self.output_directory)
            },
            "successful_extractions": successful_results,
            "failed_extractions": failed_results,
            "detailed_stats": self.stats
        }
        
        # Save processing summary
        summary_file = self.output_directory / "processing_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print a formatted summary of processing results"""
        
        print("\n" + "="*60)
        print("🎉 FARMLAND METADATA EXTRACTION COMPLETE")
        print("="*60)
        
        proc_summary = summary["processing_summary"]
        
        print(f"📊 Processing Results:")
        print(f"   Total files: {proc_summary['total_files']}")
        print(f"   ✅ Successful: {proc_summary['successful_files']}")
        print(f"   ❌ Failed: {proc_summary['failed_files']}")
        print(f"   📄 PDFs converted: {proc_summary['pdfs_converted']}")
        print(f"   📝 Markdowns processed: {proc_summary['markdowns_processed']}")
        
        print(f"\n📈 Extraction Statistics:")
        print(f"   🌾 Total datasets found: {proc_summary['total_datasets_found']}")
        print(f"   🎯 Average confidence: {proc_summary['average_confidence']:.2f}")
        print(f"   ⏱️  Processing time: {proc_summary['processing_duration_seconds']:.1f} seconds")
        
        print(f"\n📁 Output:")
        print(f"   Directory: {proc_summary['output_directory']}")
        print(f"   Schema.org JSON files: {proc_summary['successful_files']}")
        print(f"   Summary report: processing_summary.json")
        
        if proc_summary['successful_files'] > 0:
            print(f"\n✅ Successfully generated Schema.org-compliant metadata!")
            print(f"   Ready for web indexing and repository submission")
        
        if proc_summary['failed_files'] > 0:
            print(f"\n⚠️  {proc_summary['failed_files']} files failed processing.")
            print(f"   Check processing_summary.json for error details")


def main():
    """Main function for testing"""
    processor = SimpleFileProcessor()
    
    # Example usage
    test_dir = Path("data/input/pdf_papers")
    if test_dir.exists():
        results = processor.process_directory(test_dir)
        processor.print_summary(results)
    else:
        print(f"Test directory not found: {test_dir}")

if __name__ == "__main__":
    main() 