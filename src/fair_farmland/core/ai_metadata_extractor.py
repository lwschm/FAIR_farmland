#!/usr/bin/env python3
"""
AI-Powered Farmland Metadata Extractor using OpenAI Responses API

This module implements the Schema.org-based farmland research metadata schema
using OpenAI's Responses API with structured outputs and Pydantic models for reliable extraction.
Based on the technical specification in docs/technical_report/02_metadata_schema.md
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, Field, HttpUrl, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class GeoShape(BaseModel):
    """Geographic shape following GeoJSON-style bounding box"""
    type: str = Field(default="GeoShape", description="Schema.org type")
    box: str = Field(description="Bounding box coordinates as 'lat1 lon1 lat2 lon2'")

class Place(BaseModel):
    """Geographic place following Schema.org Place"""
    type: str = Field(default="Place", description="Schema.org type")
    name: str = Field(description="Place name (e.g., 'Saxony-Anhalt, Germany')")
    geo: Optional[GeoShape] = Field(default=None, description="Geographic boundaries")
    address_country: str = Field(default="DE", description="ISO country code")

class PropertyValue(BaseModel):
    """Variable or property description following Schema.org PropertyValue"""
    type: str = Field(default="PropertyValue", description="Schema.org type")
    property_id: str = Field(description="Unique identifier for the property")
    name: str = Field(description="Human-readable name of the property")
    description: str = Field(description="Detailed description of the property")
    unit_text: Optional[str] = Field(default=None, description="Unit of measurement (e.g., 'EUR', 'ha')")
    value_reference: Optional[str] = Field(default=None, description="Reference to value type or ontology")

class Person(BaseModel):
    """Person following Schema.org Person"""
    type: str = Field(default="Person", description="Schema.org type")
    name: str = Field(description="Full name of the person")
    affiliation: Optional[str] = Field(default=None, description="Institutional affiliation")
    identifier: Optional[str] = Field(default=None, description="ORCID or other identifier")

class Organization(BaseModel):
    """Organization following Schema.org Organization"""
    type: str = Field(default="Organization", description="Schema.org type")
    name: str = Field(description="Organization name")
    url: Optional[str] = Field(default=None, description="Organization website")
    identifier: Optional[str] = Field(default=None, description="Organization identifier")

class Periodical(BaseModel):
    """Journal/Periodical following Schema.org Periodical"""
    type: str = Field(default="Periodical", description="Schema.org type")
    name: str = Field(description="Journal or periodical name")
    issn: Optional[str] = Field(default=None, description="ISSN of the journal")
    publisher: Optional[Organization] = Field(default=None, description="Journal publisher")
    url: Optional[str] = Field(default=None, description="Journal website")

class PublicationIssue(BaseModel):
    """Publication issue following Schema.org PublicationIssue"""
    type: str = Field(default="PublicationIssue", description="Schema.org type")
    issue_number: Optional[str] = Field(default=None, description="Issue number")
    is_part_of: Optional[Periodical] = Field(default=None, description="Parent periodical")

class PublicationVolume(BaseModel):
    """Publication volume following Schema.org PublicationVolume"""
    type: str = Field(default="PublicationVolume", description="Schema.org type")
    volume_number: Optional[str] = Field(default=None, description="Volume number")
    is_part_of: Optional[Periodical] = Field(default=None, description="Parent periodical")

class DataCatalog(BaseModel):
    """Data catalog following Schema.org DataCatalog"""
    type: str = Field(default="DataCatalog", description="Schema.org type")
    name: str = Field(description="Catalog name")
    url: Optional[str] = Field(default=None, description="Catalog URL")
    description: Optional[str] = Field(default=None, description="Catalog description")

class Dataset(BaseModel):
    """Dataset following Schema.org Dataset with farmland-specific properties"""
    type: str = Field(default="Dataset", description="Schema.org type")
    id: Optional[str] = Field(default=None, description="Dataset identifier/DOI")
    name: str = Field(description="Dataset title")
    description: str = Field(description="Detailed dataset description")
    
    # Coverage information
    spatial_coverage: Optional[Place] = Field(default=None, description="Geographic coverage")
    temporal_coverage: Optional[str] = Field(default=None, description="Temporal coverage (ISO 8601 interval)")
    
    # Variables and structure
    variable_measured: List[PropertyValue] = Field(default_factory=list, description="Variables/columns in the dataset")
    
    # Access and licensing
    keywords: List[str] = Field(default_factory=list, description="Dataset keywords")
    license: Optional[str] = Field(default=None, description="Dataset license URL or name")
    is_accessible_for_free: Optional[bool] = Field(default=None, description="Whether dataset is freely accessible")
    conditions_of_access: Optional[str] = Field(default=None, description="Access conditions")
    url: Optional[str] = Field(default=None, description="Landing page URL")
    
    # Additional farmland-specific metadata
    identifier: Optional[str] = Field(default=None, description="Dataset DOI or persistent identifier")
    included_in_data_catalog: Optional[DataCatalog] = Field(default=None, description="Parent data catalog")
    
    # Distribution information
    encoding_format: Optional[str] = Field(default=None, description="Data format (CSV, JSON, etc.)")
    content_size: Optional[str] = Field(default=None, description="Dataset size")
    
    @validator('temporal_coverage')
    def validate_temporal_coverage(cls, v):
        """Validate ISO 8601 interval format"""
        if v and '/' not in v:
            # Convert single years to interval format
            if v.isdigit() and len(v) == 4:
                return f"{v}/{v}"
        return v

class ScholarlyArticle(BaseModel):
    """Scholarly article following Schema.org ScholarlyArticle"""
    context: str = Field(default="https://schema.org/", alias="@context")
    type: str = Field(default="ScholarlyArticle", alias="@type")
    id: Optional[str] = Field(default=None, alias="@id", description="DOI or URL of the article")
    
    # Basic publication metadata
    name: str = Field(description="Article title")
    author: List[Person] = Field(description="List of authors")
    date_published: Optional[str] = Field(default=None, description="Publication date (YYYY-MM-DD)")
    publication_year: Optional[str] = Field(default=None, description="Publication year (YYYY)")
    publisher: Optional[Organization] = Field(default=None, description="Publisher organization")
    
    # Journal/Publication details
    is_part_of: Optional[Periodical] = Field(default=None, description="Journal or periodical where published")
    publication_volume: Optional[str] = Field(default=None, description="Volume number")
    publication_issue: Optional[str] = Field(default=None, description="Issue number")
    page_start: Optional[str] = Field(default=None, description="Starting page number")
    page_end: Optional[str] = Field(default=None, description="Ending page number")
    pagination: Optional[str] = Field(default=None, description="Page range (e.g., '123-145')")
    
    # Identifiers
    identifier: Optional[str] = Field(default=None, description="DOI or other persistent identifier")
    doi: Optional[str] = Field(default=None, description="Digital Object Identifier")
    pmid: Optional[str] = Field(default=None, description="PubMed ID")
    
    # Content metadata
    abstract: Optional[str] = Field(default=None, description="Article abstract")
    keywords: List[str] = Field(default_factory=list, description="Article keywords")
    subject: List[str] = Field(default_factory=list, description="Subject categories/classifications")
    in_language: str = Field(default="en", description="Language of the article")
    
    # Access and licensing
    license: Optional[str] = Field(default=None, description="Article license")
    url: Optional[str] = Field(default=None, description="Article URL")
    is_accessible_for_free: Optional[bool] = Field(default=None, description="Whether article is open access")
    
    # Citation information
    citation: Optional[str] = Field(default=None, description="Formatted citation string")
    cite_as: Optional[str] = Field(default=None, description="How to cite this article")
    
    # Associated datasets
    dataset: List[Dataset] = Field(default_factory=list, description="Datasets described in the article")
    
    # Additional metadata
    funding: Optional[str] = Field(default=None, description="Funding information")
    about: List[str] = Field(default_factory=list, description="Main topics/themes of the article")
    genre: Optional[str] = Field(default="research article", description="Type of scholarly work")
    
    @validator('doi')
    def validate_doi(cls, v):
        """Ensure DOI format is correct"""
        if v and not v.startswith(('10.', 'https://doi.org/')):
            if '/' in v and v.count('.') >= 1:
                return f"10.{v}" if not v.startswith('10.') else v
        return v

class FarmlandMetadataExtractionResult(BaseModel):
    """Complete result from farmland metadata extraction"""
    reasoning: str = Field(description="Explanation of the extraction process and decisions made")
    scholarly_article: ScholarlyArticle = Field(description="The complete scholarly article with datasets")
    extraction_confidence: float = Field(ge=0.0, le=1.0, description="Confidence score for the extraction (0-1)")
    processing_notes: List[str] = Field(default_factory=list, description="Additional notes about processing")

class AIMetadataExtractor:
    """AI-powered metadata extractor using OpenAI Responses API with Structured Outputs"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """Initialize the extractor with OpenAI client"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or os.getenv('openaikey')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        
        # System prompt for comprehensive farmland metadata extraction
        self.system_prompt = """You are an expert in agricultural research data management and metadata standards. Your task is to extract comprehensive metadata from farmland research publications following Schema.org standards, with special focus on complete bibliographic information.

CRITICAL INSTRUCTIONS:
1. Focus ONLY on farmland-related datasets (land sales, transactions, leases, valuations, market data)
2. Ignore non-farmland data (weather, census, demographic data unless directly related to land markets)
3. Extract COMPLETE bibliographic metadata for the scholarly article
4. For each farmland dataset, provide detailed Schema.org-compliant metadata
5. Use controlled vocabularies where possible (AGROVOC for agricultural terms)
6. Generate accurate geographic and temporal coverage information
7. Assess data accessibility and licensing information
8. Always provide reasoning for your extraction decisions

NEVER HALLUCINATE OR MAKE THINGS UP. IF INFORMATION IS NOT PRESENT IN THE TEXT, MARK IT AS EMPTY STRING OR NULL.

SCHOLARLY ARTICLE METADATA REQUIREMENTS:
- Complete citation information (authors with affiliations, title, journal, volume, issue, pages)
- DOI and other persistent identifiers (PubMed ID, etc.)
- Publication dates (both full date and year)
- Journal metadata (name, ISSN, publisher)
- Abstract and keywords
- Subject classifications
- Language and licensing information
- Open access status
- Funding acknowledgments
- Complete formatted citation

DATASET METADATA REQUIREMENTS:
- Use Schema.org types and properties correctly
- Generate valid JSON-LD output structure
- Include geographic coordinates in WGS84 format when possible (lat1 lon1 lat2 lon2)
- Use ISO 8601 for temporal coverage (e.g., "2014/2017")
- Provide detailed variable descriptions with units for farmland transaction data
- Assess FAIR principles compliance in your reasoning
- Extract dataset DOIs and persistent identifiers when available
- Include data format, size, and access conditions

FARMLAND DATA FOCUS:
Look for datasets containing:
- Land sale prices and transactions
- Farmland lease agreements
- Agricultural land valuations
- Land use change data
- Farm transaction records
- Land market analysis data
- Agricultural land ownership data
- Farmland rental rates
- Land parcel information
- Agricultural property characteristics

EXTRACTION QUALITY STANDARDS:
- Complete author names with institutional affiliations
- Precise publication details (journal, volume, issue, page numbers)
- Accurate DOIs and persistent identifiers
- Detailed variable descriptions with proper units
- Geographic coverage with coordinates when available
- Temporal coverage in ISO 8601 interval format
- License and access condition information
- High confidence scoring based on information completeness
"""

    def _fix_schema_for_responses_api(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix JSON schema for OpenAI Responses API by adding strict validation requirements:
        - additionalProperties: false for all objects
        - required array including ALL properties for each object
        - ensuring type field is present
        """
        def fix_object_schema(obj):
            if isinstance(obj, dict):
                # If this is an object type, ensure strict validation
                if obj.get("type") == "object":
                    obj["additionalProperties"] = False
                    
                    # Ensure all properties are marked as required
                    if "properties" in obj:
                        # Get all property names
                        all_properties = list(obj["properties"].keys())
                        
                        # Add all properties to required array
                        obj["required"] = all_properties
                        
                        # Recursively fix nested objects
                        for prop_name, prop_schema in obj["properties"].items():
                            fix_object_schema(prop_schema)
                
                # Handle arrays with object items
                if obj.get("type") == "array" and "items" in obj:
                    fix_object_schema(obj["items"])
                
                # Handle oneOf, anyOf, allOf
                for key in ["oneOf", "anyOf", "allOf"]:
                    if key in obj:
                        for item in obj[key]:
                            fix_object_schema(item)
                
                # Recursively process all nested objects
                for key, value in obj.items():
                    if isinstance(value, (dict, list)) and key not in ["properties", "items", "oneOf", "anyOf", "allOf"]:
                        fix_object_schema(value)
            
            elif isinstance(obj, list):
                for item in obj:
                    fix_object_schema(item)
        
        # Create a deep copy to avoid modifying the original
        import copy
        fixed_schema = copy.deepcopy(schema)
        
        # Fix the root schema
        fix_object_schema(fixed_schema)
        
        return fixed_schema

    def extract_metadata(self, markdown_text: str, source_filename: str = "") -> FarmlandMetadataExtractionResult:
        """
        Extract farmland metadata from markdown text using OpenAI Responses API with structured outputs
        
        Args:
            markdown_text: The research paper content in markdown format
            source_filename: Original filename for reference
            
        Returns:
            FarmlandMetadataExtractionResult: Structured metadata extraction result
        """
        try:
            # Create comprehensive schema for OpenAI Responses API with enhanced scholarly metadata
            simplified_schema = {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": "Explanation of the extraction process and decisions made"
                    },
                    "extraction_confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "Confidence score for the extraction (0-1)"
                    },
                    # Enhanced article metadata
                    "article_title": {
                        "type": "string",
                        "description": "Title of the scholarly article"
                    },
                    "authors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Full name of the author"},
                                "affiliation": {"type": "string", "description": "Institutional affiliation"},
                                "orcid": {"type": "string", "description": "ORCID identifier if available"}
                            },
                            "required": ["name", "affiliation", "orcid"],
                            "additionalProperties": False
                        },
                        "description": "List of authors with affiliations"
                    },
                    "publication_date": {
                        "type": "string",
                        "description": "Publication date in YYYY-MM-DD format"
                    },
                    "publication_year": {
                        "type": "string",
                        "description": "Publication year (YYYY)"
                    },
                    # Journal and publication details
                    "journal_name": {
                        "type": "string",
                        "description": "Name of the journal or periodical"
                    },
                    "journal_issn": {
                        "type": "string",
                        "description": "ISSN of the journal"
                    },
                    "volume": {
                        "type": "string",
                        "description": "Volume number"
                    },
                    "issue": {
                        "type": "string",
                        "description": "Issue number"
                    },
                    "page_start": {
                        "type": "string",
                        "description": "Starting page number"
                    },
                    "page_end": {
                        "type": "string",
                        "description": "Ending page number"
                    },
                    "pagination": {
                        "type": "string",
                        "description": "Complete page range (e.g., '123-145')"
                    },
                    # Identifiers
                    "doi": {
                        "type": "string",
                        "description": "Digital Object Identifier (DOI) of the article"
                    },
                    "pmid": {
                        "type": "string",
                        "description": "PubMed ID if available"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL of the article"
                    },
                    # Content metadata
                    "abstract": {
                        "type": "string",
                        "description": "Abstract or summary of the article"
                    },
                    "keywords": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "Article keywords and key terms"
                    },
                    "subject_categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Subject classifications or categories"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language of the article (ISO code)"
                    },
                    # Publisher and access
                    "publisher": {
                        "type": "string",
                        "description": "Publisher name"
                    },
                    "license": {
                        "type": "string",
                        "description": "License information"
                    },
                    "is_open_access": {
                        "type": "boolean",
                        "description": "Whether the article is open access"
                    },
                    "funding": {
                        "type": "string",
                        "description": "Funding information"
                    },
                    # Citation
                    "citation": {
                        "type": "string",
                        "description": "Formatted citation string"
                    },
                    # Dataset information (enhanced)
                    "datasets_found": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Dataset name/title"},
                                "description": {"type": "string", "description": "Detailed dataset description"},
                                "location": {"type": "string", "description": "Geographic location/coverage"},
                                "coordinates": {"type": "string", "description": "Geographic coordinates if available (lat1 lon1 lat2 lon2)"},
                                "time_period": {"type": "string", "description": "Temporal coverage (ISO 8601 interval format)"},
                                "variables": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string", "description": "Variable name"},
                                            "description": {"type": "string", "description": "Variable description"},
                                            "unit": {"type": "string", "description": "Unit of measurement"}
                                        },
                                        "required": ["name", "description", "unit"],
                                        "additionalProperties": False
                                    },
                                    "description": "Detailed list of variables/columns in dataset"
                                },
                                "is_farmland_related": {"type": "boolean", "description": "Whether this is farmland transaction/market data"},
                                "access_info": {"type": "string", "description": "Data access information"},
                                "license": {"type": "string", "description": "Data license"},
                                "format": {"type": "string", "description": "Data format (CSV, JSON, etc.)"},
                                "size": {"type": "string", "description": "Dataset size if mentioned"},
                                "doi": {"type": "string", "description": "Dataset DOI if available"}
                            },
                            "required": ["name", "description", "location", "coordinates", "time_period", "variables", "is_farmland_related", "access_info", "license", "format", "size", "doi"],
                            "additionalProperties": False
                        },
                        "description": "List of datasets found in the paper with comprehensive metadata"
                    }
                },
                "required": [
                    "reasoning", 
                    "extraction_confidence", 
                    "article_title", 
                    "authors", 
                    "publication_date",
                    "publication_year",
                    "journal_name",
                    "journal_issn",
                    "volume",
                    "issue", 
                    "page_start",
                    "page_end",
                    "pagination",
                    "doi",
                    "pmid",
                    "url",
                    "abstract",
                    "keywords",
                    "subject_categories",
                    "language",
                    "publisher",
                    "license",
                    "is_open_access", 
                    "funding",
                    "citation",
                    "datasets_found"
                ],
                "additionalProperties": False
            }

            user_input = f"""Extract comprehensive farmland research metadata from this scientific publication:

SOURCE: {source_filename}

CONTENT:
{markdown_text[:50000]}  # Limit content to prevent token overflow

Please provide:
1. Complete scholarly article metadata following Schema.org standards
2. Detailed information about ALL farmland datasets mentioned
3. Geographic and temporal coverage for each dataset
4. Variable descriptions for transaction/market data
5. Assessment of data accessibility and FAIR compliance
6. Clear reasoning for your extraction decisions

Focus on creating high-quality, Schema.org-compliant JSON-LD metadata that can be indexed by search engines and integrated into research data catalogs like BonaRes.

{self.system_prompt}"""

            # Use Responses API with structured outputs
            response = self.client.responses.create(
                model=self.model,
                input=user_input,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "farmland_metadata_extraction",
                        "schema": simplified_schema
                    }
                },
                temperature=0.1,  # Low temperature for consistent results
                max_output_tokens=16000   # Increased for comprehensive extraction
            )
            
            # Parse the JSON response and convert to Pydantic model structure
            response_text = response.output[0].content[0].text
            simplified_data = json.loads(response_text)
            
            # Convert simplified response to comprehensive Pydantic model structure
            datasets = []
            for dataset_data in simplified_data.get('datasets_found', []):
                # Create variable measurements from enhanced variables list
                variables = []
                for var_data in dataset_data.get('variables', []):
                    if isinstance(var_data, dict):
                        variables.append(PropertyValue(
                            property_id=var_data.get('name', '').lower().replace(' ', '_'),
                            name=var_data.get('name', ''),
                            description=var_data.get('description', ''),
                            unit_text=var_data.get('unit', '')
                        ))
                    else:
                        # Handle string format (fallback)
                        variables.append(PropertyValue(
                            property_id=str(var_data).lower().replace(' ', '_'),
                            name=str(var_data),
                            description=f"Variable: {var_data}"
                        ))
                
                # Create enhanced spatial coverage with coordinates
                spatial_coverage = None
                if dataset_data.get('location'):
                    geo_shape = None
                    if dataset_data.get('coordinates'):
                        geo_shape = GeoShape(box=dataset_data['coordinates'])
                    
                    spatial_coverage = Place(
                        name=dataset_data['location'],
                        geo=geo_shape,
                        address_country="DE"  # Assume Germany for farmland data
                    )
                
                # Create enhanced dataset
                dataset = Dataset(
                    name=dataset_data['name'],
                    description=dataset_data['description'],
                    spatial_coverage=spatial_coverage,
                    temporal_coverage=dataset_data.get('time_period'),
                    variable_measured=variables,
                    license=dataset_data.get('license'),
                    conditions_of_access=dataset_data.get('access_info'),
                    keywords=['farmland'] if dataset_data.get('is_farmland_related') else [],
                    encoding_format=dataset_data.get('format'),
                    content_size=dataset_data.get('size'),
                    identifier=dataset_data.get('doi')
                )
                datasets.append(dataset)
            
            # Create enhanced authors list with affiliations
            authors = []
            for author_data in simplified_data.get('authors', []):
                if isinstance(author_data, dict):
                    authors.append(Person(
                        name=author_data.get('name', ''),
                        affiliation=author_data.get('affiliation', ''),
                        identifier=author_data.get('orcid', '')
                    ))
                else:
                    # Handle string format (fallback)
                    authors.append(Person(name=str(author_data)))
            
            # Create journal/periodical information
            journal = None
            if simplified_data.get('journal_name'):
                publisher_org = None
                if simplified_data.get('publisher'):
                    publisher_org = Organization(name=simplified_data['publisher'])
                
                journal = Periodical(
                    name=simplified_data['journal_name'],
                    issn=simplified_data.get('journal_issn'),
                    publisher=publisher_org
                )
            
            # Create comprehensive scholarly article
            scholarly_article = ScholarlyArticle(
                name=simplified_data.get('article_title', 'Unknown Title'),
                author=authors,
                date_published=simplified_data.get('publication_date'),
                publication_year=simplified_data.get('publication_year'),
                is_part_of=journal,
                publication_volume=simplified_data.get('volume'),
                publication_issue=simplified_data.get('issue'),
                page_start=simplified_data.get('page_start'),
                page_end=simplified_data.get('page_end'),
                pagination=simplified_data.get('pagination'),
                doi=simplified_data.get('doi'),
                identifier=simplified_data.get('doi'),  # Use DOI as main identifier
                pmid=simplified_data.get('pmid'),
                url=simplified_data.get('url'),
                abstract=simplified_data.get('abstract'),
                keywords=simplified_data.get('keywords', []),
                subject=simplified_data.get('subject_categories', []),
                in_language=simplified_data.get('language', 'en'),
                publisher=Organization(name=simplified_data['publisher']) if simplified_data.get('publisher') else None,
                license=simplified_data.get('license'),
                is_accessible_for_free=simplified_data.get('is_open_access'),
                funding=simplified_data.get('funding'),
                citation=simplified_data.get('citation'),
                dataset=datasets
            )
            
            # Create result
            result = FarmlandMetadataExtractionResult(
                reasoning=simplified_data.get('reasoning', 'Extraction completed'),
                scholarly_article=scholarly_article,
                extraction_confidence=simplified_data.get('extraction_confidence', 0.0),
                processing_notes=[]
            )
            
            # Add processing metadata
            processing_info = {
                "processed_at": datetime.now().isoformat(),
                "source_filename": source_filename,
                "model_used": self.model,
                "content_length": len(markdown_text),
                "extraction_method": "OpenAI Responses API with Structured Outputs"
            }
            
            # Add processing info to notes
            result.processing_notes.append(f"Processed at {processing_info['processed_at']}")
            result.processing_notes.append(f"Model: {processing_info['model_used']}")
            result.processing_notes.append(f"Content length: {processing_info['content_length']} characters")
            result.processing_notes.append(f"API: OpenAI Responses API with structured outputs")
            
            logger.info(f"Successfully extracted metadata from {source_filename}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {source_filename}: {str(e)}")
            
            # Return error result with minimal valid structure
            error_result = FarmlandMetadataExtractionResult(
                reasoning=f"Extraction failed due to error: {str(e)}",
                scholarly_article=ScholarlyArticle(
                    name=f"Error processing {source_filename}",
                    author=[Person(name="Processing Error")],
                    date_published=datetime.now().strftime("%Y-%m-%d")
                ),
                extraction_confidence=0.0,
                processing_notes=[f"Error: {str(e)}"]
            )
            return error_result

    def extract_to_jsonld(self, markdown_text: str, source_filename: str = "") -> Dict[str, Any]:
        """
        Extract metadata and return as JSON-LD dictionary
        
        Args:
            markdown_text: The research paper content
            source_filename: Original filename for reference
            
        Returns:
            Dict: JSON-LD formatted metadata
        """
        result = self.extract_metadata(markdown_text, source_filename)
        
        # Convert Pydantic model to JSON-LD compatible dictionary
        jsonld_data = result.scholarly_article.model_dump(by_alias=True, exclude_none=True)
        
        # Add extraction metadata
        jsonld_data["extraction_metadata"] = {
            "reasoning": result.reasoning,
            "confidence": result.extraction_confidence,
            "processing_notes": result.processing_notes,
            "generated_at": datetime.now().isoformat(),
            "generator": "FAIR Farmland AI Metadata Extractor"
        }
        
        return jsonld_data

    def batch_extract_from_directory(self, 
                                   markdown_dir: Union[str, Path], 
                                   output_dir: Union[str, Path],
                                   file_pattern: str = "*.md") -> Dict[str, Any]:
        """
        Batch extract metadata from multiple markdown files
        
        Args:
            markdown_dir: Directory containing markdown files
            output_dir: Directory to save JSON-LD files
            file_pattern: File pattern to match (default: *.md)
            
        Returns:
            Dict: Summary of batch processing results
        """
        markdown_dir = Path(markdown_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        markdown_files = list(markdown_dir.glob(file_pattern))
        results = []
        errors = []
        
        logger.info(f"Starting batch extraction of {len(markdown_files)} files")
        
        for md_file in markdown_files:
            try:
                # Read markdown content
                with open(md_file, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                
                # Extract metadata
                jsonld_data = self.extract_to_jsonld(markdown_content, md_file.name)
                
                # Save JSON-LD file
                output_file = output_dir / f"{md_file.stem}_schema_metadata.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(jsonld_data, f, indent=2, ensure_ascii=False)
                
                results.append({
                    "source_file": str(md_file),
                    "output_file": str(output_file),
                    "datasets_found": len(jsonld_data.get('dataset', [])),
                    "confidence": jsonld_data.get('extraction_metadata', {}).get('confidence', 0.0)
                })
                
                logger.info(f"Processed {md_file.name} -> {output_file.name}")
                
            except Exception as e:
                error_info = {
                    "source_file": str(md_file),
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                errors.append(error_info)
                logger.error(f"Failed to process {md_file.name}: {str(e)}")
        
        # Generate batch summary
        summary = {
            "batch_processing_summary": {
                "total_files": len(markdown_files),
                "successful_extractions": len(results),
                "failed_extractions": len(errors),
                "success_rate": len(results) / len(markdown_files) if markdown_files else 0,
                "total_datasets_found": sum(r["datasets_found"] for r in results),
                "average_confidence": sum(r["confidence"] for r in results) / len(results) if results else 0,
                "processed_at": datetime.now().isoformat(),
                "output_directory": str(output_dir)
            },
            "successful_extractions": results,
            "failed_extractions": errors
        }
        
        # Save batch summary
        summary_file = output_dir / "batch_extraction_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Batch extraction complete. Summary saved to {summary_file}")
        return summary

def main():
    """Main function for testing the extractor"""
    extractor = AIMetadataExtractor()
    
    # Test with markdown directory if available
    md_dir = Path("data/input/md_papers")
    output_dir = Path("data/output/schema_metadata")
    
    if md_dir.exists():
        results = extractor.batch_extract_from_directory(md_dir, output_dir)
        print(f"Processed {results['batch_processing_summary']['successful_extractions']} files successfully")
    else:
        print("No markdown directory found. Please run PDF processing first.")

if __name__ == "__main__":
    main() 