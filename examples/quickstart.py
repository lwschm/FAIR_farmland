#!/usr/bin/env python3
"""
Quickstart Example: FAIR Farmland Data Analysis Toolkit

This example demonstrates the basic workflow of the toolkit:
1. Process PDFs to extract metadata
2. Consolidate data sources
3. Generate analysis and visualizations
"""

import sys
from pathlib import Path

# Add src to path for development
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from fair_farmland.core.batch_processor import BatchPDFProcessor
from fair_farmland.core.consolidator import DataSourceConsolidator
from fair_farmland.analysis.analyzer import FarmlandDataAnalyzer

def run_quickstart_example():
    """Run the complete analysis pipeline."""
    print("🌾 FAIR Farmland Data Analysis - Quickstart Example")
    print("=" * 60)
    
    # Step 1: Batch Processing
    print("\n1. 📄 Processing PDF papers...")
    try:
        processor = BatchPDFProcessor(
            pdf_directory="data/input/pdf_papers",
            output_directory="data/output/batch_outputs",
            md_directory="data/input/md_papers"
        )
        processor.process_all_pdfs()
        print(f"   ✅ Processed {len(processor.results)} PDFs successfully")
        
    except Exception as e:
        print(f"   ❌ Error in batch processing: {e}")
        return False
    
    # Step 2: Consolidation
    print("\n2. 🔄 Consolidating data sources...")
    try:
        consolidator = DataSourceConsolidator(
            input_file="data/output/batch_outputs/data_sources_summary.json",
            output_dir="data/output/consolidated_outputs"
        )
        results = consolidator.run_consolidation()
        print(f"   ✅ Consolidated {results['report']['consolidation_summary']['original_sources']} sources")
        print(f"   📊 Final count: {results['report']['consolidation_summary']['consolidated_sources']} sources")
        
    except Exception as e:
        print(f"   ❌ Error in consolidation: {e}")
        return False
    
    # Step 3: Analysis
    print("\n3. 📈 Generating comprehensive analysis...")
    try:
        analyzer = FarmlandDataAnalyzer(
            json_file_path="data/output/consolidated_outputs/consolidated_sources.json",
            csv_file_path="data/output/consolidated_outputs/consolidated_sources.csv"
        )
        analyzer.run_complete_analysis()
        print("   ✅ Analysis completed with visualizations")
        
    except Exception as e:
        print(f"   ❌ Error in analysis: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Quickstart example completed successfully!")
    print("\nGenerated outputs:")
    print("📁 data/output/batch_outputs/       - Raw extraction results")
    print("📁 data/output/consolidated_outputs/ - Consolidated data sources")
    print("📁 data/output/analysis_outputs/     - Analysis and visualizations")
    print("\nNext steps:")
    print("1. Review the generated reports and visualizations")
    print("2. Launch the web interface: streamlit run src/fair_farmland/web_app/main.py")
    print("3. Explore the API documentation in the docs/ folder")
    
    return True

if __name__ == "__main__":
    success = run_quickstart_example()
    sys.exit(0 if success else 1) 