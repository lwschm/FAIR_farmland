#!/usr/bin/env python3
"""
FAIR Farmland Metadata Extraction Tool

A streamlined tool for extracting farmland research metadata from PDF and markdown files
using OpenAI Responses API and generating Schema.org-compliant JSON-LD metadata.

Usage:
    python run_farmland_extraction.py <input_directory> [output_directory]

Examples:
    python run_farmland_extraction.py data/input/papers/
    python run_farmland_extraction.py /path/to/papers/ /path/to/output/
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Add the src directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from fair_farmland.core.simple_processor import SimpleFileProcessor

def setup_argparse():
    """Set up command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Extract farmland research metadata from PDF/markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data/input/papers/
  %(prog)s /path/to/papers/ /path/to/output/
  %(prog)s ./documents/ --output ./results/

Notes:
  - Supports PDF and markdown (.md, .markdown) files
  - PDFs are automatically converted to markdown first
  - Existing markdown files are processed directly
  - Outputs Schema.org-compliant JSON-LD metadata
  - Requires OpenAI API key (set OPENAI_API_KEY or openaikey env variable)
        """
    )
    
    parser.add_argument(
        "input_directory",
        type=str,
        help="Directory containing PDF and/or markdown files to process"
    )
    
    parser.add_argument(
        "output_directory",
        type=str,
        nargs="?",
        default=None,
        help="Output directory for Schema.org JSON files (default: ./output_TIMESTAMP/)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser

def check_api_key():
    """Check if OpenAI API key is available"""
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('openaikey')
    if not api_key:
        print("❌ ERROR: OpenAI API key not found!")
        print()
        print("Please set one of these environment variables:")
        print("  export OPENAI_API_KEY='your_key_here'")
        print("  export openaikey='your_key_here'")
        print()
        print("Or add it to a .env file in the project directory:")
        print("  echo 'OPENAI_API_KEY=your_key_here' > .env")
        print()
        return False
    return True

def print_banner():
    """Print application banner"""
    print("🌾 FAIR Farmland Metadata Extraction Tool")
    print("=" * 50)
    print("🤖 Using OpenAI Responses API with structured outputs")
    print("🌐 Generating Schema.org-compliant JSON-LD metadata")
    print("⭐ FAIR principles assessment included")
    print()

def main():
    """Main function"""
    # Parse arguments
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check API key
    if not check_api_key():
        sys.exit(1)
    
    # Validate input directory
    input_dir = Path(args.input_directory)
    if not input_dir.exists():
        print(f"❌ ERROR: Input directory does not exist: {input_dir}")
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"❌ ERROR: Input path is not a directory: {input_dir}")
        sys.exit(1)
    
    # Set up output directory
    if args.output_directory:
        output_dir = Path(args.output_directory)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"output_{timestamp}")
    
    print(f"📂 Input directory: {input_dir.absolute()}")
    print(f"📁 Output directory: {output_dir.absolute()}")
    print()
    
    # Check for files in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    md_files = list(input_dir.glob("*.md")) + list(input_dir.glob("*.markdown"))
    total_files = len(pdf_files) + len(md_files)
    
    if total_files == 0:
        print(f"❌ ERROR: No PDF or markdown files found in: {input_dir}")
        print("   Supported formats: .pdf, .md, .markdown")
        sys.exit(1)
    
    print(f"📋 Found {total_files} files to process:")
    print(f"   📄 PDF files: {len(pdf_files)}")
    print(f"   📝 Markdown files: {len(md_files)}")
    print()
    
    # Set up logging if verbose
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        # Initialize processor
        print("🔧 Initializing processor...")
        processor = SimpleFileProcessor(output_directory=output_dir)
        
        # Process files
        print("🚀 Starting processing...")
        print()
        
        results = processor.process_directory(input_dir)
        
        # Print results
        processor.print_summary(results)
        
        # Additional helpful information
        proc_summary = results["processing_summary"]
        if proc_summary['successful_files'] > 0:
            print(f"\n📋 Next Steps:")
            print(f"   1. Review generated JSON-LD files in: {output_dir}")
            print(f"   2. Validate Schema.org compliance if needed")
            print(f"   3. Submit to research data repositories")
            print(f"   4. Index in search engines for discoverability")
        
        # Exit with appropriate code
        if proc_summary['failed_files'] > 0:
            print(f"\n⚠️  Some files failed processing. Check logs for details.")
            sys.exit(1)
        else:
            print(f"\n🎉 All files processed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: Processing failed with error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 