import os
import json
import streamlit as st
from openai import OpenAI


# Load OpenAI API key directly from streamlit secrets


@st.cache_data(show_spinner=True)
def extract_metadata(markdown_text):
    """
    Extract metadata from markdown text using OpenAI API.
    
    Args:
        markdown_text (str): The markdown text extracted from a PDF
        
    Returns:
        dict: The extracted metadata and data sources
    """
    openaiapikey = st.secrets["OpenAI_key"]

    # Check if API key is available
    if not openaiapikey:
        st.sidebar.error("OpenAI API key not found in .env file")
        api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
        if not api_key:
            return {
                "metadata": {
                    "authors": ["No API key provided"],
                    "journal": "Unknown",
                    "title": "API key missing", 
                    "doi": "Unknown",
                    "year": 0
                },
                "data_sources": []
            }
        openaiapikey = api_key

    try:
        # Initialize OpenAI client with the API key
        client = OpenAI(api_key=openaiapikey)
        
        # Create system message
        system_prompt = "Extract metadata from scientific publications, including authors, journal, title, DOI, year of publication, and detailed information about the farmland data used in the study.\n\nYou are tasked with scanning scientific publications to identify and extract critical metadata, as well as providing detailed descriptions of the farmland  source(s) used within each study.\nOnly consider the data which includes farmland data like transaction data of farmland sales or leases or other farmland related data. \nDo not consider additional data like census data or other non-farmland data.\nDo not consider the data which includes non-farmland data like weather data or other non-farmland related data.\n\n- Metadata to Extract:\n  - Authors\n  - Journal\n  - Title\n  - DOI\n  - Year of Publication\n\n- Data Description: Include a detailed summary of each data source used in the study, providing contextual information such as:\n  - Type of Data\n  - Purpose within the study\n  - Collection methods\n  - Sample sizes\n  - Key findings or conclusions drawn from the data\n  - Any unique characteristics or limitations of the data\n\n# Steps\n\n1. **Identify Metadata**: Scan the publication for metadata sections or headers that typically contain details like authors, journal name, title, DOI, and publication year.\n2. **Locate Data Sources**: Examine sections of the publication like \"Methods,\" \"Materials and Methods,\" or \"Data\" for information on the datasets used.\n3. **Extract and Describe Data**: Extract pertinent information about each dataset, including type, purpose, collection methods, sample sizes, and any unique details about the data.\n4. **Summarize each dataset:** Provide a concise yet comprehensive description of each dataset, highlighting its role and significance in the study.\n\n# Notes\n\n- Ensure accurate extraction and detail, especially regarding data source descriptions, to support comprehensible summaries for future use.\n- Pay attention to the context and nuances in the description of data sources, as these can vary widely between studies."
        
        # Create user message
        user_prompt = f"Extract metadata from the scientific publication and list the data sources used in the model.\n\n{markdown_text}"
        

        
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                {"role": "user", "content": user_prompt}
            ],
           text={
                "format": {
                "type": "json_schema",
                "name": "scientific_publication_fair_assessment",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                    "metadata": {
                        "type": "object",
                        "description": "Bibliographic and descriptive metadata of the scientific publication.",
                        "properties": {
                        "authors": {
                            "type": "array",
                            "description": "A list of full names of all authors as stated in the publication.",
                            "items": {
                            "type": "string"
                            }
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
                            "description": "The Digital Object Identifier (DOI) of the publication, used to uniquely identify and resolve the article."
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
                            "description": "The primary language of the publication, e.g., 'en' for English."
                        },
                        "keywords": {
                            "type": "array",
                            "description": "A list of keywords describing the subject or topic areas of the publication.",
                            "items": {
                            "type": "string"
                            }
                        },
                        "license": {
                            "type": "string",
                            "description": "The usage license of the publication (e.g., CC-BY, CC0, All Rights Reserved), indicating whether reuse is permitted."
                        }
                        },
                        "required": [
                        "authors",
                        "journal",
                        "title",
                        "doi",
                        "year",
                        "publisher",
                        "language",
                        "keywords",
                        "license"
                        ],
                        "additionalProperties": False
                    },
                    "data_sources": {
                        "type": "array",
                        "description": "A list of datasets used or referenced in the publication.",
                        "items": {
                        "type": "object",
                        "description": "Detailed information about a single dataset or data source used in the study.",
                        "properties": {
                            "source_name": {
                            "type": "string",
                            "description": "The name or title of the dataset as referred to in the publication."
                            },
                            "description": {
                            "type": "string",
                            "description": "A brief summary of the dataset content, including its thematic focus and relevance to the study."
                            },
                            "country": {
                            "type": "string",
                            "description": "The country where the data was collected or primarily applies to."
                            },
                            "region": {
                            "type": "string",
                            "description": "A more specific geographic region within the country, if applicable."
                            },
                            "earliest_year": {
                            "type": "number",
                            "description": "The earliest year of observation/data entry in the dataset."
                            },
                            "latest_year": {
                            "type": "number",
                            "description": "The latest year of observation/data entry in the dataset."
                            },
                            "transaction_types": {
                            "type": "array",
                            "description": "The types of transactions or observations in the dataset (e.g., 'sales', 'leases', 'crop yields').",
                            "items": {
                                "type": "string"
                            }
                            },
                            "spatial_resolution": {
                            "type": "string",
                            "description": "The granularity of spatial data (e.g., 'plot-level', 'municipality', 'grid cell 1km²')."
                            },
                            "accessibility": {
                            "type": "string",
                            "description": "Access level for the data source: one of 'open', 'embargoed', 'restricted', or 'metadata-only'."
                            },
                            "access_conditions": {
                            "type": "string",
                            "description": "Additional textual description of conditions or steps required to access the dataset (e.g., registration, approval process)."
                            },
                            "number_of_observations": {
                            "type": "integer",
                            "description": "Total number of records, plots, or entities included in the dataset."
                            },
                            "url": {
                            "type": "string",
                            "description": "The URL or landing page where the dataset (or metadata) can be accessed."
                            },
                            "data_format": {
                            "type": "string",
                            "description": "The digital format of the data files (e.g., 'CSV', 'GeoJSON', 'NetCDF')."
                            },
                            "identifier_type": {
                            "type": "string",
                            "description": "Type of identifier used for the dataset (e.g., 'DOI', 'UUID', 'ARK', 'URL')."
                            },
                            "persistent_identifier": {
                            "type": "boolean",
                            "description": "Indicates whether the identifier is persistent (resolves consistently and is maintained over time)."
                            },
                            "data_license": {
                            "type": "string",
                            "description": "The license or reuse conditions under which the dataset is made available."
                            },
                            "metadata_standard": {
                            "type": "string",
                            "description": "The metadata schema used (e.g., 'DataCite', 'DCAT', 'ISO19115')."
                            },
                            "structured_metadata": {
                            "type": "boolean",
                            "description": "True if metadata is provided in a machine-readable format (e.g., JSON-LD, RDF, XML)."
                            },
                            "semantic_vocabularies": {
                            "type": "array",
                            "description": "List of ontologies or controlled vocabularies referenced in the metadata (e.g., AGROVOC, ENVO).",
                            "items": {
                                "type": "string"
                            }
                            },
                            "provenance_included": {
                            "type": "boolean",
                            "description": "True if the metadata describes how the dataset was generated, collected, or processed."
                            },
                            "linked_entities": {
                            "type": "array",
                            "description": "List of identifiers for related publications, people (ORCID), organizations (ROR), or datasets (DOI).",
                            "items": {
                                "type": "string"
                            }
                            }
                        },
                        "required": [
                            "source_name",
                            "description",
                            "country",
                            "region",
                            "earliest_year",
                            "latest_year",
                            "transaction_types",
                            "spatial_resolution",
                            "accessibility",
                            "access_conditions",
                            "number_of_observations",
                            "url",
                            "data_format",
                            "identifier_type",
                            "persistent_identifier",
                            "data_license",
                            "metadata_standard",
                            "structured_metadata",
                            "semantic_vocabularies",
                            "provenance_included",
                            "linked_entities"
                        ],
                        "additionalProperties": False
                        }
                    },
                    "assessment": {
                        "type": "object",
                        "description": "Quantitative FAIRness scores and justifications across the four FAIR principles.",
                        "properties": {
                        "findability": {
                            "type": "number",
                            "description": "Score between 0 and 1 reflecting how easily the data and metadata can be found."
                        },
                        "findability_reason": {
                            "type": "string",
                            "description": "A short explanation justifying the assigned findability score. Should mention elements like DOI, metadata quality, and indexing."
                        },
                        "accessibility": {
                            "type": "number",
                            "description": "Score between 0 and 1 reflecting the ease and clarity of accessing the dataset."
                        },
                        "accessibility_reason": {
                            "type": "string",
                            "description": "A short explanation justifying the assigned accessibility score. Should address access conditions, open protocols, and landing pages."
                        },
                        "interoperability": {
                            "type": "number",
                            "description": "Score between 0 and 1 reflecting how well the data integrates with other systems (e.g., use of standard formats or vocabularies)."
                        },
                        "interoperability_reason": {
                            "type": "string",
                            "description": "A short explanation justifying the assigned interoperability score. Should refer to ontologies, RDF, or standard formats."
                        },
                        "reusability": {
                            "type": "number",
                            "description": "Score between 0 and 1 reflecting how easily the data can be reused by others."
                        },
                        "reusability_reason": {
                            "type": "string",
                            "description": "A short explanation justifying the assigned reusability score. Should include details on licenses, provenance, and metadata richness."
                        }
                        },
                        "required": [
                        "findability",
                        "findability_reason",
                        "accessibility",
                        "accessibility_reason",
                        "interoperability",
                        "interoperability_reason",
                        "reusability",
                        "reusability_reason"
                        ],
                        "additionalProperties": False
                    }
                    },
                    "required": [
                    "metadata",
                    "data_sources",
                    "assessment"
                    ],
                    "additionalProperties": False
                }
                }
            },
            reasoning={},
            tools=[],
            temperature=1,
            max_output_tokens=2048,
            top_p=1,
            store=True
            )
        
        raw = response.output_text
        parsed = json.loads(raw)
        return parsed
        
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        # Return a minimal valid structure to prevent downstream errors
        return {
            "metadata": {
                "authors": ["Error occurred"],
                "journal": "Error", 
                "title": f"API Error: {str(e)[:100]}", 
                "doi": "Unknown",
                "year": 0
            },
            "data_sources": []
        } 