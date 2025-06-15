#!/usr/bin/env python3
"""
Farmland Data Sources Analysis Script

This script generates comprehensive descriptive statistics and visualizations
for the consolidated farmland data sources extracted from research papers.

Key metrics analyzed:
- Data source distributions and counts
- Geographic and temporal coverage
- FAIR assessment analysis
- Data quality and completeness metrics
- Research paper contributions
- Accessibility and format patterns

Author: AI Assistant
Date: 2024
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

# Set up the plotting style
try:
    plt.style.use('seaborn-v0_8')
except:
    try:
        plt.style.use('seaborn')
    except:
        pass
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

class FarmlandDataAnalyzer:
    """Comprehensive analysis and visualization of farmland data sources."""
    
    def __init__(self, json_file_path=None, csv_file_path=None):
        """Initialize the analyzer with data file paths."""
        self.json_file_path = json_file_path
        self.csv_file_path = csv_file_path
        self.data = None
        self.metadata = None
        self.output_dir = Path("analysis_outputs")
        self.output_dir.mkdir(exist_ok=True)
        
    def load_data(self):
        """Load the consolidated farmland data from JSON and CSV files."""
        if self.json_file_path:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                self.metadata = json_data.get('metadata', {})
                self.data = pd.DataFrame(json_data.get('sources', []))
        
        if self.csv_file_path:
            self.csv_data = pd.read_csv(self.csv_file_path)
            if self.data is None:
                self.data = self.csv_data
                
        print(f"Loaded {len(self.data)} data sources for analysis")
        return self.data
    
    def print_basic_statistics(self):
        """Print basic descriptive statistics."""
        print("\n" + "="*60)
        print("FARMLAND DATA SOURCES: BASIC STATISTICS")
        print("="*60)
        
        print(f"Total Data Sources: {len(self.data)}")
        if self.metadata:
            print(f"Original Sources Count: {self.metadata.get('original_sources_count', 'N/A')}")
            print(f"Consolidated Sources Count: {self.metadata.get('consolidated_sources_count', 'N/A')}")
            print(f"Duplicate Groups Found: {self.metadata.get('duplicate_groups_found', 'N/A')}")
            print(f"Deduplication Savings: {self.metadata.get('deduplication_savings', 'N/A')}")
        
        print(f"\nData Coverage:")
        print(f"  Countries: {len(self.data['country'].unique())}")
        print(f"  Regions: {len(self.data['region'].unique())}")
        print(f"  Earliest Year: {self.data['earliest_year'].min()}")
        print(f"  Latest Year: {self.data['latest_year'].max()}")
        print(f"  Total Observations: {self.data['number_of_observations'].sum():,.0f}")
        
    def analyze_temporal_coverage(self):
        """Analyze temporal patterns in the data sources."""
        print("\n" + "="*60)
        print("TEMPORAL COVERAGE ANALYSIS")
        print("="*60)
        
        # Calculate time spans
        self.data['time_span'] = self.data['latest_year'] - self.data['earliest_year']
        
        # Create temporal analysis plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Temporal Coverage Analysis of Farmland Data Sources', fontsize=16, fontweight='bold')
        
        # 1. Distribution of earliest years
        axes[0, 0].hist(self.data['earliest_year'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Distribution of Data Start Years')
        axes[0, 0].set_xlabel('Earliest Year')
        axes[0, 0].set_ylabel('Number of Data Sources')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Distribution of latest years
        axes[0, 1].hist(self.data['latest_year'], bins=20, alpha=0.7, color='lightcoral', edgecolor='black')
        axes[0, 1].set_title('Distribution of Data End Years')
        axes[0, 1].set_xlabel('Latest Year')
        axes[0, 1].set_ylabel('Number of Data Sources')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Time span distribution
        axes[1, 0].hist(self.data['time_span'], bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
        axes[1, 0].set_title('Distribution of Data Time Spans')
        axes[1, 0].set_xlabel('Time Span (Years)')
        axes[1, 0].set_ylabel('Number of Data Sources')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Timeline visualization
        for i, row in self.data.iterrows():
            axes[1, 1].plot([row['earliest_year'], row['latest_year']], [i, i], 
                          linewidth=2, alpha=0.7)
        axes[1, 1].set_title('Data Source Timeline Coverage')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Data Source Index')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'temporal_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Print temporal statistics
        print(f"Temporal Statistics:")
        print(f"  Average time span: {self.data['time_span'].mean():.1f} years")
        print(f"  Median time span: {self.data['time_span'].median():.1f} years")
        print(f"  Longest time span: {self.data['time_span'].max():.0f} years")
        print(f"  Shortest time span: {self.data['time_span'].min():.0f} years")
        
    def analyze_geographic_coverage(self):
        """Analyze geographic distribution of data sources."""
        print("\n" + "="*60)
        print("GEOGRAPHIC COVERAGE ANALYSIS")
        print("="*60)
        
        # Create geographic analysis plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Geographic Coverage Analysis of Farmland Data Sources', fontsize=16, fontweight='bold')
        
        # 1. Country distribution
        country_counts = self.data['country'].value_counts()
        axes[0, 0].bar(country_counts.index, country_counts.values, color='steelblue', alpha=0.7)
        axes[0, 0].set_title('Data Sources by Country')
        axes[0, 0].set_xlabel('Country')
        axes[0, 0].set_ylabel('Number of Data Sources')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Region distribution (top 10)
        region_counts = self.data['region'].value_counts().head(10)
        axes[0, 1].barh(range(len(region_counts)), region_counts.values, color='forestgreen', alpha=0.7)
        axes[0, 1].set_yticks(range(len(region_counts)))
        axes[0, 1].set_yticklabels(region_counts.index)
        axes[0, 1].set_title('Top 10 Regions by Data Sources')
        axes[0, 1].set_xlabel('Number of Data Sources')
        
        # 3. Spatial resolution analysis
        spatial_res = self.data['spatial_resolution'].value_counts()
        axes[1, 0].pie(spatial_res.values, labels=spatial_res.index, autopct='%1.1f%%', startangle=90)
        axes[1, 0].set_title('Spatial Resolution Distribution')
        
        # 4. Observations by region (top 10)
        region_obs = self.data.groupby('region')['number_of_observations'].sum().sort_values(ascending=False).head(10)
        axes[1, 1].barh(range(len(region_obs)), region_obs.values, color='orange', alpha=0.7)
        axes[1, 1].set_yticks(range(len(region_obs)))
        axes[1, 1].set_yticklabels(region_obs.index)
        axes[1, 1].set_title('Top 10 Regions by Number of Observations')
        axes[1, 1].set_xlabel('Number of Observations')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'geographic_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Geographic Statistics:")
        print(f"  Countries covered: {list(country_counts.index)}")
        print(f"  Total regions: {len(self.data['region'].unique())}")
        print(f"  Most common region: {region_counts.index[0]} ({region_counts.iloc[0]} sources)")
        
    def analyze_fair_assessment(self):
        """Analyze FAIR assessment scores and grades."""
        print("\n" + "="*60)
        print("FAIR ASSESSMENT ANALYSIS")
        print("="*60)
        
        try:
            # Create FAIR analysis plots
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle('FAIR Assessment Analysis of Farmland Data Sources', fontsize=16, fontweight='bold')
        
            # 1. FAIR Grade Distribution
            fair_grades = self.data['fair_grade'].value_counts()
            axes[0, 0].bar(fair_grades.index, fair_grades.values, color='crimson', alpha=0.7)
            axes[0, 0].set_title('FAIR Grade Distribution')
            axes[0, 0].set_xlabel('FAIR Grade')
            axes[0, 0].set_ylabel('Number of Data Sources')
        
        # 2. Individual FAIR Scores Distribution
        fair_scores = ['findability_score', 'accessibility_score', 'interoperability_score', 'reusability_score']
        for i, score in enumerate(fair_scores):
            score_dist = self.data[score].value_counts().sort_index()
            axes[0, 1].bar([f"{score.split('_')[0].title()}\n{x}" for x in score_dist.index], 
                          score_dist.values, alpha=0.7, 
                          label=score.split('_')[0].title())
        axes[0, 1].set_title('Individual FAIR Scores Distribution')
        axes[0, 1].set_ylabel('Number of Data Sources')
        axes[0, 1].legend()
        
        # 3. Overall FAIR Score Distribution
        axes[0, 2].hist(self.data['overall_fair_score'], bins=10, alpha=0.7, color='purple', edgecolor='black')
        axes[0, 2].set_title('Overall FAIR Score Distribution')
        axes[0, 2].set_xlabel('Overall FAIR Score')
        axes[0, 2].set_ylabel('Number of Data Sources')
        
        # 4. FAIR Scores Correlation Heatmap
        fair_cols = ['findability_score', 'accessibility_score', 'interoperability_score', 'reusability_score']
        correlation_matrix = self.data[fair_cols].corr()
        im = axes[1, 0].imshow(correlation_matrix, cmap='coolwarm', aspect='auto')
        axes[1, 0].set_xticks(range(len(fair_cols)))
        axes[1, 0].set_yticks(range(len(fair_cols)))
        axes[1, 0].set_xticklabels([col.split('_')[0].title() for col in fair_cols])
        axes[1, 0].set_yticklabels([col.split('_')[0].title() for col in fair_cols])
        axes[1, 0].set_title('FAIR Scores Correlation Matrix')
        plt.colorbar(im, ax=axes[1, 0])
        
        # 5. FAIR Grade by Accessibility
        accessibility_fair = pd.crosstab(self.data['accessibility'], self.data['fair_grade'])
        accessibility_fair.plot(kind='bar', ax=axes[1, 1], stacked=True)
        axes[1, 1].set_title('FAIR Grade by Accessibility Type')
        axes[1, 1].set_xlabel('Accessibility')
        axes[1, 1].set_ylabel('Number of Data Sources')
        axes[1, 1].legend(title='FAIR Grade')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        # 6. FAIR Score by Number of Observations
        axes[1, 2].scatter(self.data['number_of_observations'], self.data['overall_fair_score'], 
                          alpha=0.6, s=50, color='green')
        axes[1, 2].set_title('FAIR Score vs Number of Observations')
        axes[1, 2].set_xlabel('Number of Observations (log scale)')
        axes[1, 2].set_ylabel('Overall FAIR Score')
        axes[1, 2].set_xscale('log')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'fair_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"FAIR Assessment Statistics:")
        print(f"  Average FAIR Score: {self.data['overall_fair_score'].mean():.2f}")
        print(f"  Most common FAIR Grade: {fair_grades.index[0]} ({fair_grades.iloc[0]} sources)")
        print(f"  Grade distribution: {dict(fair_grades)}")
        
    def analyze_data_characteristics(self):
        """Analyze data characteristics and quality metrics."""
        print("\n" + "="*60)
        print("DATA CHARACTERISTICS ANALYSIS")
        print("="*60)
        
        # Create data characteristics plots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Data Characteristics Analysis of Farmland Data Sources', fontsize=16, fontweight='bold')
        
        # 1. Accessibility distribution
        accessibility_counts = self.data['accessibility'].value_counts()
        axes[0, 0].pie(accessibility_counts.values, labels=accessibility_counts.index, 
                      autopct='%1.1f%%', startangle=90)
        axes[0, 0].set_title('Data Accessibility Distribution')
        
        # 2. Data format distribution
        format_counts = self.data['data_format'].value_counts().head(8)
        axes[0, 1].barh(range(len(format_counts)), format_counts.values, color='teal', alpha=0.7)
        axes[0, 1].set_yticks(range(len(format_counts)))
        axes[0, 1].set_yticklabels(format_counts.index)
        axes[0, 1].set_title('Top 8 Data Formats')
        axes[0, 1].set_xlabel('Number of Data Sources')
        
        # 3. Number of observations distribution
        axes[0, 2].hist(np.log10(self.data['number_of_observations'].dropna()), 
                       bins=15, alpha=0.7, color='gold', edgecolor='black')
        axes[0, 2].set_title('Distribution of Observations (log10 scale)')
        axes[0, 2].set_xlabel('Log10(Number of Observations)')
        axes[0, 2].set_ylabel('Number of Data Sources')
        
        # 4. Transaction types word cloud data
        transaction_types = []
        for types in self.data['transaction_types'].dropna():
            if isinstance(types, str):
                transaction_types.extend([t.strip() for t in types.split(';')])
        
        transaction_counts = Counter(transaction_types)
        common_transactions = dict(transaction_counts.most_common(10))
        
        axes[1, 0].bar(common_transactions.keys(), common_transactions.values(), 
                      color='lightblue', alpha=0.7)
        axes[1, 0].set_title('Top 10 Transaction Types')
        axes[1, 0].set_xlabel('Transaction Type')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 5. Data completeness analysis
        completeness_metrics = {
            'URL': self.data['url'].notna().sum() / len(self.data) * 100,
            'License': self.data['data_license'].notna().sum() / len(self.data) * 100,
            'Observations': self.data['number_of_observations'].notna().sum() / len(self.data) * 100,
            'Format': self.data['data_format'].notna().sum() / len(self.data) * 100,
            'Region': self.data['region'].notna().sum() / len(self.data) * 100
        }
        
        axes[1, 1].bar(completeness_metrics.keys(), completeness_metrics.values(), 
                      color='mediumorchid', alpha=0.7)
        axes[1, 1].set_title('Data Completeness by Field')
        axes[1, 1].set_xlabel('Field')
        axes[1, 1].set_ylabel('Completeness (%)')
        axes[1, 1].set_ylim(0, 100)
        
        # 6. Consolidation status
        if 'consolidation_status' in self.data.columns:
            consolidation_counts = self.data['consolidation_status'].value_counts()
            axes[1, 2].pie(consolidation_counts.values, labels=consolidation_counts.index, 
                          autopct='%1.1f%%', startangle=90)
            axes[1, 2].set_title('Consolidation Status Distribution')
        else:
            axes[1, 2].text(0.5, 0.5, 'Consolidation Status\nData Not Available', 
                           ha='center', va='center', transform=axes[1, 2].transAxes)
            axes[1, 2].set_title('Consolidation Status')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'data_characteristics.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Data Characteristics Statistics:")
        print(f"  Most common accessibility: {accessibility_counts.index[0]}")
        print(f"  Most common data format: {format_counts.index[0]}")
        print(f"  Average observations per source: {self.data['number_of_observations'].mean():,.0f}")
        print(f"  Data completeness: {completeness_metrics}")
        
    def analyze_research_papers(self):
        """Analyze research paper contributions to data sources."""
        print("\n" + "="*60)
        print("RESEARCH PAPER CONTRIBUTION ANALYSIS")
        print("="*60)
        
        # Analyze paper contributions
        if 'source_papers_count' in self.data.columns:
            paper_counts = self.data['source_papers_count'].value_counts().sort_index()
            
            fig, axes = plt.subplots(1, 2, figsize=(15, 6))
            fig.suptitle('Research Paper Contribution Analysis', fontsize=16, fontweight='bold')
            
            # 1. Distribution of sources per paper
            axes[0].bar(paper_counts.index, paper_counts.values, color='royalblue', alpha=0.7)
            axes[0].set_title('Distribution of Papers per Data Source')
            axes[0].set_xlabel('Number of Papers')
            axes[0].set_ylabel('Number of Data Sources')
            
            # 2. Consolidation impact
            if 'consolidation_status' in self.data.columns:
                consolidation_papers = self.data.groupby('consolidation_status')['source_papers_count'].mean()
                axes[1].bar(consolidation_papers.index, consolidation_papers.values, 
                           color='darkorange', alpha=0.7)
                axes[1].set_title('Average Papers per Source by Consolidation Status')
                axes[1].set_xlabel('Consolidation Status')
                axes[1].set_ylabel('Average Number of Papers')
            
            plt.tight_layout()
            plt.savefig(self.output_dir / 'research_papers_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Research Paper Statistics:")
            print(f"  Average papers per data source: {self.data['source_papers_count'].mean():.1f}")
            print(f"  Max papers per data source: {self.data['source_papers_count'].max()}")
            print(f"  Sources with multiple papers: {(self.data['source_papers_count'] > 1).sum()}")
        
    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        print("\n" + "="*60)
        print("COMPREHENSIVE SUMMARY REPORT")
        print("="*60)
        
        summary_stats = {
            'Total Data Sources': len(self.data),
            'Countries Covered': len(self.data['country'].unique()),
            'Regions Covered': len(self.data['region'].unique()),
            'Temporal Span': f"{self.data['earliest_year'].min()} - {self.data['latest_year'].max()}",
            'Total Observations': f"{self.data['number_of_observations'].sum():,.0f}",
            'Average Time Span': f"{self.data['time_span'].mean():.1f} years",
            'Most Common Accessibility': self.data['accessibility'].mode().iloc[0],
            'Average FAIR Score': f"{self.data['overall_fair_score'].mean():.2f}",
            'Most Common FAIR Grade': self.data['fair_grade'].mode().iloc[0],
            'Data Completeness (URLs)': f"{(self.data['url'].notna().sum() / len(self.data) * 100):.1f}%"
        }
        
        # Create summary visualization
        fig, ax = plt.subplots(figsize=(12, 8))
        y_pos = np.arange(len(summary_stats))
        values = [str(v) for v in summary_stats.values()]
        
        # Create a simple text-based summary plot
        ax.barh(y_pos, [1] * len(summary_stats), color='lightsteelblue', alpha=0.3)
        
        for i, (key, value) in enumerate(summary_stats.items()):
            ax.text(0.5, i, f"{key}: {value}", ha='center', va='center', 
                   fontweight='bold', fontsize=11)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(summary_stats.keys())
        ax.set_xlabel('')
        ax.set_title('Farmland Data Sources: Key Statistics Summary', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlim(0, 1)
        ax.set_xticks([])
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'summary_report.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save detailed statistics to file
        with open(self.output_dir / 'detailed_statistics.txt', 'w') as f:
            f.write("FARMLAND DATA SOURCES: DETAILED STATISTICS REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for key, value in summary_stats.items():
                f.write(f"{key}: {value}\n")
            
            f.write("\nTOP REGIONS BY DATA SOURCES:\n")
            top_regions = self.data['region'].value_counts().head(5)
            for region, count in top_regions.items():
                f.write(f"  {region}: {count} sources\n")
            
            f.write("\nTOP DATA FORMATS:\n")
            top_formats = self.data['data_format'].value_counts().head(5)
            for format_type, count in top_formats.items():
                f.write(f"  {format_type}: {count} sources\n")
        
        print(f"Summary report saved to: {self.output_dir}")
        return summary_stats
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline."""
        print("Starting comprehensive farmland data analysis...")
        
        # Load data
        self.load_data()
        
        # Run all analyses
        self.print_basic_statistics()
        self.analyze_temporal_coverage()
        self.analyze_geographic_coverage()
        self.analyze_fair_assessment()
        self.analyze_data_characteristics()
        self.analyze_research_papers()
        
        # Generate final summary
        summary_stats = self.generate_summary_report()
        
        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETE!")
        print(f"{'='*60}")
        print(f"All visualizations saved to: {self.output_dir}")
        print(f"Total analyses generated: 6 visualization sets + 1 summary report")
        
        return summary_stats

def main():
    """Main function to run the farmland data analysis."""
    # Find the most recent consolidated files
    consolidated_dir = Path("consolidated_outputs")
    
    # Find JSON and CSV files
    json_files = list(consolidated_dir.glob("*farmland_sources*.json"))
    csv_files = list(consolidated_dir.glob("*farmland_sources*.csv"))
    
    if not json_files and not csv_files:
        print("No consolidated farmland data files found!")
        print("Please run the consolidation script first.")
        return
    
    # Use the most recent files
    json_file = max(json_files, key=lambda x: x.stat().st_mtime) if json_files else None
    csv_file = max(csv_files, key=lambda x: x.stat().st_mtime) if csv_files else None
    
    print(f"Using data files:")
    if json_file:
        print(f"  JSON: {json_file}")
    if csv_file:
        print(f"  CSV: {csv_file}")
    
    # Create analyzer and run analysis
    analyzer = FarmlandDataAnalyzer(json_file_path=json_file, csv_file_path=csv_file)
    summary_stats = analyzer.run_complete_analysis()
    
    return analyzer, summary_stats

if __name__ == "__main__":
    analyzer, stats = main() 