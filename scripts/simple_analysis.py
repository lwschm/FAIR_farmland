#!/usr/bin/env python3
"""
Simplified Farmland Data Sources Analysis Script

This script generates key descriptive statistics and basic visualizations
for the consolidated farmland data sources.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

class SimpleFarmlandAnalyzer:
    """Simplified analysis of farmland data sources."""
    
    def __init__(self, json_file_path=None, csv_file_path=None):
        """Initialize the analyzer."""
        self.json_file_path = json_file_path
        self.csv_file_path = csv_file_path
        self.data = None
        self.metadata = None
        self.output_dir = Path("analysis_outputs")
        self.output_dir.mkdir(exist_ok=True)
        
    def load_data(self):
        """Load the consolidated farmland data."""
        if self.csv_file_path:
            # Prefer CSV as it has flattened structure
            self.data = pd.read_csv(self.csv_file_path)
        elif self.json_file_path:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                self.metadata = json_data.get('metadata', {})
                self.data = pd.DataFrame(json_data.get('sources', []))
                
                # Flatten the fair_assessment nested structure
                if 'fair_assessment' in self.data.columns:
                    fair_cols = ['findability_score', 'accessibility_score', 'interoperability_score', 
                                'reusability_score', 'overall_fair_score', 'fair_grade']
                    for col in fair_cols:
                        self.data[col] = self.data['fair_assessment'].apply(lambda x: x.get(col, 0) if isinstance(x, dict) else 0)
                
        # Load metadata from JSON if available
        if self.json_file_path and not self.metadata:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                self.metadata = json_data.get('metadata', {})
                
        print(f"Loaded {len(self.data)} data sources for analysis")
        return self.data
    
    def basic_statistics(self):
        """Generate basic descriptive statistics."""
        print("\n" + "="*60)
        print("FARMLAND DATA SOURCES: COMPREHENSIVE STATISTICS")
        print("="*60)
        
        stats = {
            'Total Data Sources': len(self.data),
            'Countries Covered': len(self.data['country'].unique()),
            'Regions Covered': len(self.data['region'].unique()),
            'Temporal Span': f"{self.data['earliest_year'].min()} - {self.data['latest_year'].max()}",
            'Total Observations': f"{self.data['number_of_observations'].sum():,.0f}",
            'Average Time Span': f"{(self.data['latest_year'] - self.data['earliest_year']).mean():.1f} years",
        }
        
        if self.metadata:
            stats.update({
                'Original Sources Count': self.metadata.get('original_sources_count', 'N/A'),
                'Duplicate Groups Found': self.metadata.get('duplicate_groups_found', 'N/A'),
                'Deduplication Savings': self.metadata.get('deduplication_savings', 'N/A')
            })
        
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        return stats
    
    def generate_visualizations(self):
        """Generate key visualizations."""
        print("\n" + "="*60)
        print("GENERATING VISUALIZATIONS")
        print("="*60)
        
        # 1. Temporal Coverage
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 2, 1)
        plt.hist(self.data['earliest_year'], bins=15, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Distribution of Data Start Years')
        plt.xlabel('Earliest Year')
        plt.ylabel('Number of Data Sources')
        
        plt.subplot(2, 2, 2)
        time_spans = self.data['latest_year'] - self.data['earliest_year']
        plt.hist(time_spans, bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
        plt.title('Distribution of Time Spans')
        plt.xlabel('Time Span (Years)')
        plt.ylabel('Number of Data Sources')
        
        # 2. Geographic Distribution
        plt.subplot(2, 2, 3)
        region_counts = self.data['region'].value_counts().head(8)
        plt.barh(range(len(region_counts)), region_counts.values, color='steelblue', alpha=0.7)
        plt.yticks(range(len(region_counts)), region_counts.index)
        plt.title('Top 8 Regions by Data Sources')
        plt.xlabel('Number of Data Sources')
        
        # 3. Accessibility Distribution
        plt.subplot(2, 2, 4)
        access_counts = self.data['accessibility'].value_counts()
        plt.pie(access_counts.values, labels=access_counts.index, autopct='%1.1f%%', startangle=90)
        plt.title('Data Accessibility Distribution')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'farmland_analysis_overview.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Overview visualization saved")
        
        # 4. FAIR Assessment
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        fair_grades = self.data['fair_grade'].value_counts()
        plt.bar(fair_grades.index, fair_grades.values, color='crimson', alpha=0.7)
        plt.title('FAIR Grade Distribution')
        plt.xlabel('FAIR Grade')
        plt.ylabel('Number of Data Sources')
        
        plt.subplot(1, 2, 2)
        plt.hist(self.data['overall_fair_score'], bins=10, alpha=0.7, color='purple', edgecolor='black')
        plt.title('Overall FAIR Score Distribution')
        plt.xlabel('Overall FAIR Score')
        plt.ylabel('Number of Data Sources')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'fair_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ FAIR analysis visualization saved")
        
        # 5. Data Characteristics
        plt.figure(figsize=(15, 10))
        
        # Observations distribution
        plt.subplot(2, 3, 1)
        obs_data = self.data['number_of_observations'].dropna()
        plt.hist(np.log10(obs_data), bins=15, alpha=0.7, color='gold', edgecolor='black')
        plt.title('Distribution of Observations (log10 scale)')
        plt.xlabel('Log10(Number of Observations)')
        plt.ylabel('Number of Data Sources')
        
        # Data formats
        plt.subplot(2, 3, 2)
        format_counts = self.data['data_format'].value_counts().head(6)
        plt.barh(range(len(format_counts)), format_counts.values, color='teal', alpha=0.7)
        plt.yticks(range(len(format_counts)), format_counts.index)
        plt.title('Top 6 Data Formats')
        plt.xlabel('Number of Data Sources')
        
        # Transaction types
        plt.subplot(2, 3, 3)
        transaction_types = []
        for types in self.data['transaction_types'].dropna():
            if isinstance(types, str):
                transaction_types.extend([t.strip() for t in types.split(';')])
        
        transaction_counts = Counter(transaction_types)
        common_transactions = dict(transaction_counts.most_common(8))
        
        plt.bar(range(len(common_transactions)), list(common_transactions.values()), 
               color='lightblue', alpha=0.7)
        plt.xticks(range(len(common_transactions)), list(common_transactions.keys()), rotation=45)
        plt.title('Top 8 Transaction Types')
        plt.ylabel('Frequency')
        
        # Data completeness
        plt.subplot(2, 3, 4)
        completeness_metrics = {
            'URL': self.data['url'].notna().sum() / len(self.data) * 100,
            'License': self.data['data_license'].notna().sum() / len(self.data) * 100,
            'Observations': self.data['number_of_observations'].notna().sum() / len(self.data) * 100,
            'Format': self.data['data_format'].notna().sum() / len(self.data) * 100,
        }
        
        plt.bar(completeness_metrics.keys(), completeness_metrics.values(), 
               color='mediumorchid', alpha=0.7)
        plt.title('Data Completeness by Field')
        plt.ylabel('Completeness (%)')
        plt.xticks(rotation=45)
        plt.ylim(0, 100)
        
        # Research papers contribution
        plt.subplot(2, 3, 5)
        if 'source_papers_count' in self.data.columns:
            paper_counts = self.data['source_papers_count'].value_counts().sort_index()
            plt.bar(paper_counts.index, paper_counts.values, color='royalblue', alpha=0.7)
            plt.title('Papers per Data Source')
            plt.xlabel('Number of Papers')
            plt.ylabel('Number of Data Sources')
        
        # Consolidation status
        plt.subplot(2, 3, 6)
        if 'consolidation_status' in self.data.columns:
            consolidation_counts = self.data['consolidation_status'].value_counts()
            plt.pie(consolidation_counts.values, labels=consolidation_counts.index, 
                   autopct='%1.1f%%', startangle=90)
            plt.title('Consolidation Status')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'data_characteristics.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Data characteristics visualization saved")
        
    def detailed_analysis(self):
        """Generate detailed statistical analysis."""
        print("\n" + "="*60)
        print("DETAILED STATISTICAL ANALYSIS")
        print("="*60)
        
        # Temporal Analysis
        print("\nTEMPORAL ANALYSIS:")
        time_spans = self.data['latest_year'] - self.data['earliest_year']
        print(f"  Average time span: {time_spans.mean():.1f} years")
        print(f"  Median time span: {time_spans.median():.1f} years")
        print(f"  Longest time span: {time_spans.max():.0f} years")
        print(f"  Shortest time span: {time_spans.min():.0f} years")
        
        # Geographic Analysis
        print("\nGEOGRAPHIC ANALYSIS:")
        region_stats = self.data['region'].value_counts()
        print(f"  Total regions: {len(region_stats)}")
        print(f"  Most common region: {region_stats.index[0]} ({region_stats.iloc[0]} sources)")
        print("  Top 5 regions:")
        for i, (region, count) in enumerate(region_stats.head(5).items()):
            print(f"    {i+1}. {region}: {count} sources")
        
        # Data Volume Analysis
        print("\nDATA VOLUME ANALYSIS:")
        obs_stats = self.data['number_of_observations'].describe()
        print(f"  Total observations: {self.data['number_of_observations'].sum():,.0f}")
        print(f"  Average per source: {obs_stats['mean']:,.0f}")
        print(f"  Median per source: {obs_stats['50%']:,.0f}")
        print(f"  Largest dataset: {obs_stats['max']:,.0f} observations")
        print(f"  Smallest dataset: {obs_stats['min']:,.0f} observations")
        
        # FAIR Assessment
        print("\nFAIR ASSESSMENT:")
        fair_stats = self.data['overall_fair_score'].describe()
        print(f"  Average FAIR Score: {fair_stats['mean']:.2f}")
        print(f"  FAIR Grade distribution:")
        grade_counts = self.data['fair_grade'].value_counts()
        for grade, count in grade_counts.items():
            print(f"    Grade {grade}: {count} sources ({count/len(self.data)*100:.1f}%)")
        
        # Accessibility Analysis
        print("\nACCESSIBILITY ANALYSIS:")
        access_counts = self.data['accessibility'].value_counts()
        for access_type, count in access_counts.items():
            print(f"  {access_type}: {count} sources ({count/len(self.data)*100:.1f}%)")
        
    def save_summary_report(self):
        """Save detailed summary report to file."""
        with open(self.output_dir / 'farmland_analysis_report.txt', 'w') as f:
            f.write("FARMLAND DATA SOURCES: COMPREHENSIVE ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Basic statistics
            f.write("BASIC STATISTICS:\n")
            f.write(f"Total Data Sources: {len(self.data)}\n")
            f.write(f"Countries: {len(self.data['country'].unique())}\n")
            f.write(f"Regions: {len(self.data['region'].unique())}\n")
            f.write(f"Temporal Range: {self.data['earliest_year'].min()} - {self.data['latest_year'].max()}\n")
            f.write(f"Total Observations: {self.data['number_of_observations'].sum():,.0f}\n\n")
            
            # Top regions
            f.write("TOP REGIONS BY DATA SOURCES:\n")
            for region, count in self.data['region'].value_counts().head(10).items():
                f.write(f"  {region}: {count} sources\n")
            f.write("\n")
            
            # Data formats
            f.write("TOP DATA FORMATS:\n")
            for format_type, count in self.data['data_format'].value_counts().head(10).items():
                f.write(f"  {format_type}: {count} sources\n")
            f.write("\n")
            
            # Accessibility
            f.write("ACCESSIBILITY DISTRIBUTION:\n")
            for access_type, count in self.data['accessibility'].value_counts().items():
                f.write(f"  {access_type}: {count} sources ({count/len(self.data)*100:.1f}%)\n")
            
        print("✓ Detailed report saved to farmland_analysis_report.txt")
    
    def run_analysis(self):
        """Run the complete analysis."""
        print("Starting farmland data analysis...")
        
        # Load data
        self.load_data()
        
        # Run analyses
        self.basic_statistics()
        self.generate_visualizations()
        self.detailed_analysis()
        self.save_summary_report()
        
        print(f"\n{'='*60}")
        print("🎉 ANALYSIS COMPLETE!")
        print(f"{'='*60}")
        print(f"Files generated in: {self.output_dir.absolute()}")
        print("Generated files:")
        print("  📊 farmland_analysis_overview.png - Overview visualizations")
        print("  ⭐ fair_analysis.png - FAIR assessment analysis")
        print("  📈 data_characteristics.png - Data characteristics")
        print("  📄 farmland_analysis_report.txt - Detailed text report")

def main():
    """Main function."""
    # Find consolidated files
    consolidated_dir = Path("consolidated_outputs")
    json_files = list(consolidated_dir.glob("*farmland_sources*.json"))
    csv_files = list(consolidated_dir.glob("*farmland_sources*.csv"))
    
    if not json_files and not csv_files:
        print("No consolidated farmland data files found!")
        return
    
    json_file = max(json_files, key=lambda x: x.stat().st_mtime) if json_files else None
    csv_file = max(csv_files, key=lambda x: x.stat().st_mtime) if csv_files else None
    
    analyzer = SimpleFarmlandAnalyzer(json_file_path=json_file, csv_file_path=csv_file)
    analyzer.run_analysis()
    
    return analyzer

if __name__ == "__main__":
    analyzer = main() 