#!/usr/bin/env python3
"""
Data Sources Consolidation and Deduplication Tool
Uses OpenAI to identify duplicate data sources and create a final consolidated dataset
"""

import json
import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import logging
from pathlib import Path

# Load environment variables
load_dotenv('.env')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('consolidation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataSourceConsolidator:
    def __init__(self, input_file="batch_outputs/data_sources_summary.json", output_dir="consolidated_outputs"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize OpenAI client
        self.openai_api_key = os.getenv('openaikey')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        
        # Storage for results
        self.original_sources = []
        self.deduplicated_sources = []
        self.duplicate_groups = []
        
        # Data format standardization mapping
        self.data_format_mapping = {
            'csv': 'CSV', 'CSV': 'CSV', 'json': 'JSON', 'JSON': 'JSON',
            'xml': 'XML', 'XML': 'XML', 'excel': 'Excel', 'Excel': 'Excel',
            'xls': 'Excel', 'xlsx': 'Excel', 'pdf': 'PDF', 'PDF': 'PDF',
            'shapefile': 'Shapefile', 'Shapefile': 'Shapefile', 'shp': 'Shapefile',
            'database': 'Database', 'Database': 'Database', 'db': 'Database'
        }
        
        # Spatial resolution standardization mapping
        self.spatial_resolution_mapping = {
            'plot level': 'Plot Level', 'Plot level': 'Plot Level',
            'plot-level': 'Plot Level', 'Plot-level': 'Plot Level',
            'parcel level': 'Plot Level', 'Parcel level': 'Plot Level',
            'municipality level': 'Municipality Level', 'Municipality level': 'Municipality Level',
            'county level': 'County Level', 'County level': 'County Level',
            'county and municipality level': 'County Level',
            'district level': 'District Level', 'District level': 'District Level',
            'national': 'National', 'National': 'National',
            'local': 'Local', 'Local': 'Local',
            'local (within a simulated region)': 'Local',
            'land value zones': 'Zone Level', 'Land value zones': 'Zone Level',
            'plot-specific': 'Plot Level', 'Plot-specific': 'Plot Level',
            'n/a': 'Not Specified', 'N/A': 'Not Specified',
            'not specified': 'Not Specified', 'Not specified': 'Not Specified'
        }
        
    def load_data_sources(self):
        """Load data sources from the summary JSON file"""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file {self.input_file} not found. Please run batch processing first.")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.original_sources = data.get('sources', [])
        
        # Standardize data categories before processing
        self.original_sources = self._standardize_data_sources(self.original_sources)
        
        logger.info(f"Loaded {len(self.original_sources)} data sources for analysis")
        
        return self.original_sources
    
    def _standardize_data_sources(self, sources):
        """Standardize data source categories for consistency"""
        # Accessibility standardization mapping
        accessibility_mapping = {
            # Public variants
            'public': 'Public',
            'Public': 'Public',
            'publicly available': 'Public',
            'Publicly available': 'Public',
            'publicly_available': 'Public',
            'open': 'Public',
            'Open': 'Public',
            
            # Restricted variants
            'restricted': 'Restricted',
            'Restricted': 'Restricted',
            'limited': 'Restricted',
            'Limited': 'Restricted',
            
            # Confidential variants
            'confidential': 'Confidential',
            'Confidential': 'Confidential',
            'private': 'Confidential',
            'Private': 'Confidential',
            
            # Mixed categories
            'confidential and restricted': 'Confidential and Restricted',
            'Confidential and Restricted': 'Confidential and Restricted',
            'restricted and confidential': 'Confidential and Restricted',
            'Restricted and Confidential': 'Confidential and Restricted',
            
            # Not specified variants
            'not specified': 'Not Specified',
            'Not specified': 'Not Specified',
            'Not Specified': 'Not Specified',
            'unknown': 'Not Specified',
            'Unknown': 'Not Specified',
            '': 'Not Specified',
            'N/A': 'Not Specified',
            'n/a': 'Not Specified'
        }
        
        # Country standardization mapping
        country_mapping = {
            'usa': 'United States',
            'USA': 'United States',
            'us': 'United States',
            'US': 'United States',
            'united states': 'United States',
            'United states': 'United States',
            'uk': 'United Kingdom',
            'UK': 'United Kingdom',
            'united kingdom': 'United Kingdom',
            'United kingdom': 'United Kingdom'
        }
        
        for source in sources:
            # Standardize accessibility
            if 'accessibility' in source:
                original_accessibility = source['accessibility']
                if original_accessibility in accessibility_mapping:
                    source['accessibility'] = accessibility_mapping[original_accessibility]
                elif not original_accessibility or str(original_accessibility).strip() == '':
                    source['accessibility'] = 'Not Specified'
            
            # Standardize data format
            if 'data_format' in source:
                original_format = source['data_format']
                if original_format in self.data_format_mapping:
                    source['data_format'] = self.data_format_mapping[original_format]
                elif not original_format or str(original_format).strip() == '':
                    source['data_format'] = 'Not Specified'
            
            # Standardize country
            if 'country' in source:
                original_country = source['country']
                if original_country in country_mapping:
                    source['country'] = country_mapping[original_country]
            
            # Standardize spatial resolution
            if 'spatial_resolution' in source:
                original_spatial_resolution = source['spatial_resolution']
                if original_spatial_resolution in self.spatial_resolution_mapping:
                    source['spatial_resolution'] = self.spatial_resolution_mapping[original_spatial_resolution]
                elif not original_spatial_resolution or str(original_spatial_resolution).strip() == '':
                    source['spatial_resolution'] = 'Not Specified'
        
        logger.info(f"Standardized categories for {len(sources)} data sources")
        return sources
    
    def identify_duplicates_with_openai(self, batch_size=10):
        """Use OpenAI to identify duplicate data sources in batches"""
        logger.info("Starting duplicate identification with OpenAI...")
        
        all_duplicates = []
        processed_sources = set()
        
        # Process sources in batches to avoid token limits
        for i in range(0, len(self.original_sources), batch_size):
            batch = self.original_sources[i:i + batch_size]
            
            # Skip sources already marked as duplicates
            batch = [src for src in batch if id(src) not in processed_sources]
            
            if len(batch) < 2:
                continue
                
            logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} sources")
            
            batch_duplicates = self._analyze_batch_for_duplicates(batch)
            
            # Mark processed sources
            for group in batch_duplicates:
                for src_idx in group:
                    processed_sources.add(id(batch[src_idx]))
            
            all_duplicates.extend(batch_duplicates)
        
        self.duplicate_groups = all_duplicates
        logger.info(f"Found {len(all_duplicates)} duplicate groups")
        
        return all_duplicates
    
    def _analyze_batch_for_duplicates(self, batch):
        """Analyze a batch of sources for duplicates using OpenAI"""
        # Prepare source summaries for analysis
        source_summaries = []
        for idx, source in enumerate(batch):
            summary = {
                "index": idx,
                "source_name": source.get("source_name", ""),
                "description": source.get("description", "")[:200] + "..." if len(source.get("description", "")) > 200 else source.get("description", ""),
                "country": source.get("country", ""),
                "region": source.get("region", ""),
                "earliest_year": source.get("earliest_year", ""),
                "latest_year": source.get("latest_year", ""),
                "url": source.get("url", ""),
                "paper_title": source.get("paper_title", "")
            }
            source_summaries.append(summary)
        
        system_prompt = """You are a data analyst tasked with identifying duplicate farmland data sources. 
        
Analyze the provided data sources and identify which ones refer to the same underlying dataset. Consider:
- Similar source names (accounting for slight variations in naming)
- Same geographic coverage (country/region)
- Overlapping time periods
- Similar URLs or domains
- Similar descriptions of data content

Return ONLY groups of duplicate sources as a JSON array. Each group should contain the indices of sources that are duplicates of each other. Only include groups with 2 or more sources.

Example format:
[
  [0, 3, 7],  // Sources 0, 3, and 7 are duplicates
  [2, 5]      // Sources 2 and 5 are duplicates
]

If no duplicates are found, return an empty array: []"""

        user_prompt = f"Identify duplicate data sources from this list:\n\n{json.dumps(source_summaries, indent=2)}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Handle different possible response formats
            if isinstance(result, dict) and 'duplicates' in result:
                return result['duplicates']
            elif isinstance(result, dict) and 'groups' in result:
                return result['groups']
            elif isinstance(result, list):
                return result
            else:
                logger.warning(f"Unexpected response format: {result}")
                return []
                
        except Exception as e:
            logger.error(f"Error in OpenAI analysis: {str(e)}")
            return []
    
    def consolidate_duplicates_with_openai(self, duplicate_group):
        """Use OpenAI to merge duplicate sources into a single consolidated entry"""
        sources_to_merge = [self.original_sources[idx] for idx in duplicate_group]
        
        system_prompt = """You are tasked with consolidating duplicate farmland data sources into a single, comprehensive entry.

Given multiple sources that refer to the same underlying dataset, create ONE consolidated source that:
1. Combines the most complete and accurate information
2. Uses the most descriptive source name
3. Merges descriptions to capture all relevant details
4. Uses the broadest geographic and temporal coverage
5. Selects the best available URL
6. Combines FAIR assessment scores (use highest scores)
7. Lists all paper titles that reference this source

Return a single JSON object with the consolidated source information using the same schema as the input sources."""

        user_prompt = f"Consolidate these duplicate sources into one:\n\n{json.dumps(sources_to_merge, indent=2)}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=3000
            )
            
            consolidated = json.loads(response.choices[0].message.content)
            
            # Add consolidation metadata
            consolidated["consolidation_info"] = {
                "original_count": len(sources_to_merge),
                "source_papers": list(set([src.get("paper_title", "") for src in sources_to_merge if src.get("paper_title")])),
                "consolidated_at": datetime.now().isoformat()
            }
            
            return consolidated
            
        except Exception as e:
            logger.error(f"Error consolidating sources: {str(e)}")
            # Fallback: return the first source with metadata about the merge
            fallback = sources_to_merge[0].copy()
            fallback["consolidation_info"] = {
                "original_count": len(sources_to_merge),
                "source_papers": list(set([src.get("paper_title", "") for src in sources_to_merge if src.get("paper_title")])),
                "consolidated_at": datetime.now().isoformat(),
                "note": "Automatic consolidation failed, using first source as fallback"
            }
            return fallback
    
    def create_consolidated_dataset(self):
        """Create the final consolidated dataset with deduplicated sources"""
        logger.info("Creating consolidated dataset...")
        
        # Track which sources have been processed
        processed_indices = set()
        consolidated_sources = []
        
        # Process duplicate groups first
        for group in self.duplicate_groups:
            if not any(idx in processed_indices for idx in group):
                logger.info(f"Consolidating duplicate group: {group}")
                consolidated_source = self.consolidate_duplicates_with_openai(group)
                consolidated_sources.append(consolidated_source)
                
                # Mark these indices as processed
                processed_indices.update(group)
        
        # Add unique sources (not in any duplicate group)
        for idx, source in enumerate(self.original_sources):
            if idx not in processed_indices:
                # Add metadata to indicate this is a unique source
                unique_source = source.copy()
                unique_source["consolidation_info"] = {
                    "original_count": 1,
                    "source_papers": [source.get("paper_title", "")],
                    "consolidated_at": datetime.now().isoformat(),
                    "status": "unique"
                }
                consolidated_sources.append(unique_source)
        
        self.deduplicated_sources = consolidated_sources
        logger.info(f"Consolidated from {len(self.original_sources)} to {len(consolidated_sources)} unique sources")
        
        return consolidated_sources
    
    def calculate_enhanced_fair_scores(self):
        """Calculate enhanced FAIR scores for the consolidated dataset"""
        logger.info("Calculating enhanced FAIR scores...")
        
        for source in self.deduplicated_sources:
            # Extract individual FAIR dimensions (if available from original assessments)
            findability = source.get("findability_score", 0)
            accessibility = source.get("accessibility_score", 0) 
            interoperability = source.get("interoperability_score", 0)
            reusability = source.get("reusability_score", 0)
            
            # Calculate overall FAIR score
            fair_scores = [findability, accessibility, interoperability, reusability]
            overall_fair = sum(fair_scores) / len(fair_scores) if any(fair_scores) else 0
            
            # Add enhanced scoring
            source["fair_assessment"] = {
                "findability_score": findability,
                "accessibility_score": accessibility, 
                "interoperability_score": interoperability,
                "reusability_score": reusability,
                "overall_fair_score": overall_fair,
                "fair_grade": self._get_fair_grade(overall_fair)
            }
    
    def _get_fair_grade(self, score):
        """Convert FAIR score to letter grade"""
        if score >= 0.8:
            return "A"
        elif score >= 0.6:
            return "B" 
        elif score >= 0.4:
            return "C"
        elif score >= 0.2:
            return "D"
        else:
            return "F"
    
    def save_consolidated_outputs(self):
        """Save the consolidated dataset in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON
        json_file = self.output_dir / f"consolidated_farmland_sources_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "original_sources_count": len(self.original_sources),
                    "consolidated_sources_count": len(self.deduplicated_sources),
                    "duplicate_groups_found": len(self.duplicate_groups),
                    "deduplication_savings": len(self.original_sources) - len(self.deduplicated_sources)
                },
                "sources": self.deduplicated_sources,
                "duplicate_groups": self.duplicate_groups
            }, f, indent=2, ensure_ascii=False)
        
        # Save CSV for analysis
        csv_data = []
        for source in self.deduplicated_sources:
            fair = source.get("fair_assessment", {})
            consolidation = source.get("consolidation_info", {})
            
            row = {
                "source_name": source.get("source_name", ""),
                "description": source.get("description", "")[:100] + "..." if len(source.get("description", "")) > 100 else source.get("description", ""),
                "country": source.get("country", ""),
                "region": source.get("region", ""),
                "earliest_year": source.get("earliest_year", ""),
                "latest_year": source.get("latest_year", ""),
                "transaction_types": "; ".join(source.get("transaction_types", [])),
                "spatial_resolution": source.get("spatial_resolution", ""),
                "accessibility": source.get("accessibility", ""),
                "number_of_observations": source.get("number_of_observations", ""),
                "data_format": source.get("data_format", ""),
                "url": source.get("url", ""),
                "data_license": source.get("data_license", ""),
                "findability_score": fair.get("findability_score", 0),
                "accessibility_score": fair.get("accessibility_score", 0),
                "interoperability_score": fair.get("interoperability_score", 0),
                "reusability_score": fair.get("reusability_score", 0),
                "overall_fair_score": fair.get("overall_fair_score", 0),
                "fair_grade": fair.get("fair_grade", ""),
                "source_papers_count": consolidation.get("original_count", 1),
                "source_papers": "; ".join(consolidation.get("source_papers", [])),
                "consolidation_status": consolidation.get("status", "consolidated")
            }
            csv_data.append(row)
        
        csv_file = self.output_dir / f"consolidated_farmland_sources_{timestamp}.csv"
        pd.DataFrame(csv_data).to_csv(csv_file, index=False)
        
        logger.info(f"Saved consolidated JSON: {json_file}")
        logger.info(f"Saved consolidated CSV: {csv_file}")
        
        return json_file, csv_file
    
    def generate_consolidation_report(self):
        """Generate a summary report of the consolidation process"""
        duplicate_stats = {
            "total_duplicate_groups": len(self.duplicate_groups),
            "sources_in_duplicates": sum(len(group) for group in self.duplicate_groups),
            "unique_sources": len(self.original_sources) - sum(len(group) for group in self.duplicate_groups),
            "consolidation_ratio": (len(self.original_sources) - len(self.deduplicated_sources)) / len(self.original_sources) if self.original_sources else 0
        }
        
        fair_stats = {}
        if self.deduplicated_sources:
            fair_scores = [src.get("fair_assessment", {}).get("overall_fair_score", 0) for src in self.deduplicated_sources]
            fair_stats = {
                "average_fair_score": sum(fair_scores) / len(fair_scores),
                "highest_fair_score": max(fair_scores),
                "lowest_fair_score": min(fair_scores),
                "sources_with_fair_a": len([s for s in fair_scores if s >= 0.8]),
                "sources_with_fair_b": len([s for s in fair_scores if 0.6 <= s < 0.8]),
                "sources_with_fair_c": len([s for s in fair_scores if 0.4 <= s < 0.6])
            }
        
        report = {
            "consolidation_summary": {
                "original_sources": len(self.original_sources),
                "consolidated_sources": len(self.deduplicated_sources),
                "reduction_achieved": len(self.original_sources) - len(self.deduplicated_sources),
                "reduction_percentage": duplicate_stats["consolidation_ratio"] * 100
            },
            "duplicate_analysis": duplicate_stats,
            "fair_assessment_summary": fair_stats,
            "generated_at": datetime.now().isoformat()
        }
        
        report_file = self.output_dir / "consolidation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Generated consolidation report: {report_file}")
        return report
    
    def run_consolidation(self):
        """Run the complete consolidation process"""
        logger.info("Starting farmland data sources consolidation...")
        
        # Load data
        self.load_data_sources()
        
        # Identify duplicates
        self.identify_duplicates_with_openai()
        
        # Create consolidated dataset
        self.create_consolidated_dataset()
        
        # Calculate enhanced FAIR scores
        self.calculate_enhanced_fair_scores()
        
        # Save outputs
        json_file, csv_file = self.save_consolidated_outputs()
        
        # Generate report
        report = self.generate_consolidation_report()
        
        logger.info("Consolidation completed successfully!")
        
        return {
            "json_file": json_file,
            "csv_file": csv_file,
            "report": report
        }

def main():
    """Main execution function"""
    print("🌾 Farmland Data Sources Consolidation Tool")
    print("=" * 60)
    
    try:
        consolidator = DataSourceConsolidator()
        results = consolidator.run_consolidation()
        
        print("\n✅ Consolidation completed successfully!")
        print(f"📊 Results:")
        print(f"   - JSON output: {results['json_file']}")
        print(f"   - CSV output: {results['csv_file']}")
        print(f"   - Original sources: {results['report']['consolidation_summary']['original_sources']}")
        print(f"   - Consolidated sources: {results['report']['consolidation_summary']['consolidated_sources']}")
        print(f"   - Reduction achieved: {results['report']['consolidation_summary']['reduction_achieved']} sources ({results['report']['consolidation_summary']['reduction_percentage']:.1f}%)")
        
    except Exception as e:
        logger.error(f"Consolidation failed: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 