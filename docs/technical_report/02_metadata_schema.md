# LASI Metadata Schema: Schema.org-Based Framework for German Agricultural Land Market Data

## Introduction and LASI Project Context

The LASI use case (Linking Agrosystem Data with Socio-economic Information) within the FAIRagro consortium addresses gaps in Germany's agricultural research data infrastructure. Building a metadata framework for farmland research data requires integration of socio-economic datasets into research infrastructures while maintaining compliance with metadata standards and compatibility with existing German agricultural data repositories.

This document presents the LASI metadata schema—a domain-specific metadata framework tailored to agricultural land market datasets that serves both human interpretation and machine-actionable workflows. The schema addresses the structural heterogeneity, variable provenance, and legal sensitivity characteristic of German land market data while ensuring integration with the FAIRagro ecosystem.

## Institutional Context and Infrastructure Integration

### FAIRagro and NFDI Integration

The LASI metadata schema operates within Germany's **National Research Data Infrastructure (NFDI)** framework, specifically designed to support **FAIRagro's mission** of enabling seamless data sharing across agricultural, environmental, and economic domains. Key integration requirements include:

- **BonaRes Repository Compatibility**: Direct integration with Germany's premier agricultural data repository
- **INSPIRE Compliance**: Alignment with European spatial data infrastructure standards
- **DataCite Integration**: Support for persistent identifier systems and academic citation frameworks
- **Cross-Domain Interoperability**: Enabling connections between socio-economic land data and agrosystemic research

### Addressing German Land Market Data Challenges

The schema addresses the institutional fragmentation of German land market data, where information is distributed across:

- **BORIS-D**: Federal state land valuation portals with inconsistent metadata practices
- **ALKIS**: Cadastral information systems with varying access conditions across Länder
- **BVVG**: Eastern German privatization agency auction data with specialized access requirements  
- **Statistical Offices**: Administrative datasets with limited interoperability
- ....

## Schema Architecture and Design Principles

### Core Design Objectives

The LASI metadata schema pursues three main objectives:

1. **Standardized Description**: Providing consistent metadata structure across spatial, thematic, legal, and technical dimensions
2. **Comprehensive Inventorization**: Enabling systematic cataloging and documentation of agricultural land market datasets
3. **Repository Integration**: Ensuring compatibility with German and international research data infrastructures

### Hierarchical Information Architecture

The schema employs a **nested, hierarchical design** reflecting real-world context and institutional provenance:

```
ScholarlyArticle/Report (Research Context)
├── Institutional Metadata (Authors, DOI, Journal, Dates)
├── Research Keywords and License Information  
├── Geographic and Temporal Scope
└── dataset: Dataset[] (One or more linked datasets)
     ├── Dataset Identification (Title, Description, DOI)
     ├── Spatial Coverage (INSPIRE-compliant geographic boundaries)
     ├── Temporal Coverage (ISO 8601 interval notation)
     ├── Variable Documentation (PropertyValue objects with units)
     ├── Access and Licensing Information
     ├── Data Format and Technical Specifications
     └── FAIR Compliance Assessment
```

This structure ensures that:
- **Research Context**: Each dataset maintains links to source publications and research provenance
- **Administrative Compliance**: Metadata meets German repository requirements (BonaRes, DataCite)
- **Legal Transparency**: Access conditions and licensing are explicitly documented
- **Technical Interoperability**: Format specifications enable automated processing and integration

## LASI Metadata Dimensions

### Core Descriptive Dimensions

The LASI schema systematically captures seven key metadata dimensions for land market datasets:

#### 1. Identification and General Description
- **Dataset Title**: Descriptive, unique identifier with geographic and temporal context
- **Abstract**: Comprehensive description including methodology, scope, and analytical potential
- **Institutional Responsibility**: Responsible institution, research network, or data provider
- **Publication Context**: Year of publication, associated research project, funding information
- **Persistent Identifiers**: DOI registration or alternative persistent URL where available

*Schema.org Mapping*: `schema:name`, `schema:description`, `schema:publisher`, `schema:identifier`

#### 2. Thematic Focus and Content Classification
- **Land Market Topics**: Categorized coverage (land prices, ownership structures, leasing arrangements, sales transactions)
- **Agricultural Context**: Integration with agrosystem data (soil quality, land use, agricultural production)
- **Economic Scope**: Market analysis focus (regional comparisons, temporal trends, policy impacts)
- **Methodological Approach**: Analytical framework and research methodology

*Controlled Vocabulary*: AGROVOC thesaurus terms for agricultural concepts, custom LASI vocabulary for land market specifics

#### 3. Geographic Scope and Spatial Resolution
- **Administrative Coverage**: Federal state, district, municipality, or sub-municipal resolution
- **Coordinate Systems**: INSPIRE-compliant spatial reference systems (typically ETRS89/UTM)
- **Boundary Specifications**: Precise geographic boundaries using GeoShape objects
- **Urban-Rural Classification**: Settlement context and proximity to urban centers

*Schema.org Implementation*:
```json
"spatialCoverage": {
  "@type": "Place",
  "name": "Saxony-Anhalt, Germany",
  "geo": {
    "@type": "GeoShape",
    "box": "50.7 10.9 53.1 13.1"
  },
  "addressCountry": "DE",
  "containedInPlace": {
    "@type": "AdministrativeArea",
    "name": "Saxony-Anhalt"
  }
}
```

#### 4. Temporal Coverage and Data Currency
- **Data Collection Period**: Start and end dates for data collection (ISO 8601 format)
- **Publication Lag**: Time difference between data collection and publication
- **Update Frequency**: Whether dataset receives regular updates or represents historical snapshot
- **Temporal Resolution**: Annual, quarterly, or irregular observation frequency

*Example*: "temporalCoverage": "2014-01/2017-12" for quarterly data from 2014-2017

#### 5. Variable Documentation and Data Structure
- **Core Transaction Variables**: Sale price, land area, transaction date, property characteristics
- **Contextual Variables**: Soil quality indices, land use classifications, buyer/seller categories
- **Geographic Variables**: Coordinates, administrative codes, distance measurements
- **Quality Indicators**: Data completeness, validation procedures, uncertainty measures

*PropertyValue Structure*:
```json
{
  "@type": "PropertyValue",
  "propertyID": "landSalePrice",
  "name": "Farmland Sale Price per Hectare",
  "description": "Transaction price in Euros per hectare of agricultural land",
  "unitText": "EUR/ha",
  "measurementTechnique": "Administrative record from land registry"
}
```

#### 6. Access Conditions and Legal Framework
- **Public Availability**: Open access, restricted access, or closed access classification
- **Licensing Terms**: Creative Commons, institutional, or proprietary licensing
- **Access Procedures**: Registration requirements, institutional approval, data sharing agreements
- **Legal Constraints**: GDPR compliance, commercial sensitivity, privacy protection measures
- **Usage Restrictions**: Academic use only, non-commercial restrictions, attribution requirements

#### 7. Technical Specifications and Format Information
- **Data Formats**: CSV, Excel, Shapefile, GeoJSON, database formats
- **File Sizes**: Dataset scale and processing requirements
- **Access Methods**: Direct download, API access, web services (WMS/WFS)
- **Technical Documentation**: Data dictionaries, processing scripts, validation procedures

## Integration with German Research Infrastructure

### BonaRes Repository Alignment

The LASI schema ensures **direct compatibility** with BonaRes metadata requirements:

| BonaRes Requirement | LASI Schema Element | Schema.org Property |
|---------------------|---------------------|---------------------|
| Dataset Title | name | schema:name |
| Principal Investigator | author | schema:author |
| DOI Registration | identifier | schema:identifier |
| Spatial Coverage | spatialCoverage | schema:spatialCoverage |
| Temporal Coverage | temporalCoverage | schema:temporalCoverage |
| Keywords (AGROVOC) | keywords | schema:keywords |
| License Information | license | schema:license |
| Access Conditions | conditionsOfAccess | schema:conditionsOfAccess |

### INSPIRE Directive Compliance

For datasets with spatial components, the schema incorporates **INSPIRE metadata elements**:

- **Geographic Extent**: Precise boundary definitions using ETRS89 coordinate system
- **Temporal References**: Creation, publication, and revision dates
- **Data Quality**: Completeness, consistency, and accuracy indicators  
- **Responsible Organizations**: Data providers and contact information
- **Access Constraints**: Legal and security restrictions

### DataCite Integration

Schema elements map directly to **DataCite metadata schema** for DOI registration:

```json
{
  "identifier": "10.5194/soil-data-journal-example",
  "creators": [{"name": "Research Team", "affiliation": "Institution"}],
  "titles": [{"title": "Dataset Title"}],
  "publicationYear": "2024",
  "resourceType": "Dataset",
  "geoLocations": [{"geoLocationBox": "50.7 10.9 53.1 13.1"}]
}
```

## AI-Enhanced Metadata Quality Assessment

### Automated Metadata Validation Framework

The LASI schema incorporates **AI-assisted quality assessment** using structured prompts and large language models:

#### 1. Prompt-Based Extraction and Classification
- **Metadata Parsing**: Automated identification of schema.org elements from unstructured descriptions
- **Content Validation**: Classification of metadata elements for completeness and accuracy
- **Consistency Validation**: Cross-reference checking between related metadata fields

#### 2. Completeness Assessment
- **Field-Level Assessment**: Evaluation of individual metadata element completeness and quality
- **Schema-Level Coverage**: Overall dataset documentation coverage assessment
- **Confidence Indicators**: AI model confidence scores for extracted metadata elements

#### 3. Enhancement Recommendations
- **Gap Identification**: Systematic detection of missing or incomplete metadata elements
- **Standardization Suggestions**: Recommendations for vocabulary alignment and format standardization
- **Documentation Improvement**: Specific suggestions for enhancing metadata completeness and clarity

### Validation and Curation Workflow

```
Raw Dataset Description → AI Extraction → Schema Validation → Human Review → Repository Submission
                              ↓               ↓               ↓
                         Confidence      Completeness    Quality
                         Scoring         Assessment      Enhancement
```

## Implementation Examples

### Example 1: BVVG Auction Dataset

```json
{
  "@context": "https://schema.org/",
  "@type": "ScholarlyArticle",
  "name": "On the effectiveness of restricted tendering as a form of policy intervention on agricultural land markets",
  "author": [
    {
      "type": "Person",
      "name": "Cord-Friedrich von Hobe",
      "affiliation": "Department of Agricultural Economics and Rural Development, Georg-August-Universität Göttingen",
      "identifier": ""
    },
    {
      "type": "Person",
      "name": "Oliver Musshoff",
      "affiliation": "Department of Agricultural Economics and Rural Development, Georg-August-Universität Göttingen",
      "identifier": ""
    }
  ],
  "date_published": "2021-02-22",
  "publication_year": "2021",
  "publisher": {
    "type": "Organization",
    "name": "Elsevier"
  },
  "is_part_of": {
    "type": "Periodical",
    "name": "Land Use Policy",
    "issn": "0264-8377",
    "publisher": {
      "type": "Organization",
      "name": "Elsevier"
    }
  },
  "publication_volume": "103",
  "publication_issue": "",
  "page_start": "",
  "page_end": "",
  "pagination": "",
  "identifier": "10.1016/j.landusepol.2021.105343",
  "doi": "10.1016/j.landusepol.2021.105343",
  "pmid": "",
  "abstract": "The ongoing sharp rise in farmland prices in Europe has led to a discussion concerning the need for political intervention and stronger market regulation on agricultural land markets. In this context, restricted tendering for the privatization of agricultural land in post-communist countries is discussed and used as one form of political intervention. Only certain groups of bidders may participate in such tendering procedures in order to give them greater opportunities and to counteract effects such as land grabbing or structural change. Against this background this paper aims to answer the question, whether restricted tendering procedures allow structurally disadvantaged groups of bidders to buy at lower prices as is intended by the assessed policy intervention. A rich data set of over 12,000 first-price-sealed-bit auctions of agricultural land between 2005 and 2019 from Eastern Germany is analyzed using an auction theory individual private value framework and Propensity Score Matching. Results show that restricted tendering on agricultural land markets does not fulfill its intended purpose. Although the policy’s intermediate aim of considerably reducing the number of bidders is achieved, the ultimate goal of lower purchase prices is missed. On the contrary, the findings indicate that restricted tendering actually leads to higher purchase prices for comparable farmland plots.",
  "keywords": [
    "Agricultural land markets",
    "Farmland auctions",
    "Restricted tendering",
    "Propensity score matching"
  ],
  "subject": [
    "Land Use Policy",
    "Agricultural Economics"
  ],
  "in_language": "en",
  "license": "©2021 Elsevier Ltd. All rights reserved.",
  "url": "https://doi.org/10.1016/j.landusepol.2021.105343",
  "is_accessible_for_free": false,
  "citation": "von Hobe, C.-F., & Musshoff, O. (2021). On the effectiveness of restricted tendering as a form of policy intervention on agricultural land markets. Land Use Policy, 103, 105343. https://doi.org/10.1016/j.landusepol.2021.105343",
  "dataset": [
    {
      "type": "Dataset",
      "name": "Eastern Germany Agricultural Land Auctions Dataset",
      "description": "A dataset of over 12,000 first-price-sealed-bid auctions of agricultural land between 2005 and 2019, used to analyze the effectiveness of restricted tendering procedures.",
      "spatial_coverage": {
        "type": "Place",
        "name": "Eastern Germany",
        "address_country": "DE"
      },
      "temporal_coverage": "2005/2019",
      "variable_measured": [
        {
          "type": "PropertyValue",
          "property_id": "purchase_price",
          "name": "Purchase price",
          "description": "Winning bid price for the land plot",
          "unit_text": "€/ha"
        },
        {
          "type": "PropertyValue",
          "property_id": "number_of_bids",
          "name": "Number of bids",
          "description": "Total number of bids received for the auction",
          "unit_text": "count"
        },
        {
          "type": "PropertyValue",
          "property_id": "lot_size",
          "name": "Lot size",
          "description": "Size of the land plot",
          "unit_text": "ha"
        },
        {
          "type": "PropertyValue",
          "property_id": "number_of_land_parcels",
          "name": "Number of land parcels",
          "description": "Number of parcels in the land plot",
          "unit_text": "count"
        },
        {
          "type": "PropertyValue",
          "property_id": "share_of_arable_land",
          "name": "Share of arable land",
          "description": "Proportion of the land that is arable",
          "unit_text": "ratio"
        },
        {
          "type": "PropertyValue",
          "property_id": "soil_quality",
          "name": "Soil quality",
          "description": "Quality index of the soil",
          "unit_text": "index"
        }
      ],
      "keywords": [
        "farmland"
      ],
      "license": "",
      "conditions_of_access": "Data provided by the land privatizing agency in Eastern Germany (BVVG).",
      "identifier": "",
      "encoding_format": "",
      "content_size": ""
    }
  ],
  "funding": "We gratefully acknowledge financial support from Deutsche Forschungsgemeinschaft (DFG), Germany (Grant ID Mu 1825/22-2).",
  "about": [],
  "genre": "research article",
  "extraction_metadata": {
    "reasoning": "The extraction process involved identifying key metadata elements from the provided text, focusing on bibliographic details and dataset information related to farmland transactions. The article's title, authors, and affiliations were clearly stated, allowing for accurate extraction. The publication details, including journal name, volume, issue, and DOI, were also explicitly mentioned. The abstract provided insights into the study's focus on restricted tendering in agricultural land markets, which guided the identification of relevant datasets. The dataset description was derived from the text's mention of over 12,000 land transactions analyzed, with specific geographic and temporal coverage. Variable descriptions were inferred from the context of the study, focusing on auction and land characteristics. The extraction confidence is high due to the clarity and specificity of the provided information.",
    "confidence": 0.95,
    "processing_notes": [
      "Processed at 2025-06-26T18:34:46.377815",
      "Model: gpt-4o",
      "Content length: 53234 characters",
      "API: OpenAI Responses API with structured outputs"
    ],
    "generated_at": "2025-06-26T18:34:46.378211",
    "generator": "FAIR Farmland AI Metadata Extractor"
  }
}
```

### Example 2: Regional Land Transaction Analysis

```json
{
  "@context": "https://schema.org/",
  "@type": "Dataset",
  "name": "Saxony-Anhalt Agricultural Land Transactions (2014-2017)",
  "description": "Comprehensive land transaction records from Saxony-Anhalt including sale prices, plot characteristics, and buyer/seller information for agricultural land markets analysis.",
  "keywords": ["farmland sales", "land markets", "Saxony-Anhalt", "agricultural economics", "AGROVOC:farmland", "AGROVOC:land_markets"],
  "spatialCoverage": {
    "@type": "Place",
    "name": "Saxony-Anhalt, Germany",
    "geo": {"@type": "GeoShape", "box": "50.7 10.9 53.1 13.1"},
    "addressCountry": "DE",
    "containedInPlace": {
      "@type": "AdministrativeArea",
      "name": "Saxony-Anhalt",
      "identifier": "DE-ST"
    }
  },
  "temporalCoverage": "2014-01/2017-12",
  "variableMeasured": [
    {
      "@type": "PropertyValue",
      "propertyID": "salePrice",
      "name": "Sale Price per Hectare", 
      "unitText": "EUR/ha",
      "description": "Transaction sale price in Euros per hectare of agricultural land"
    },
    {
      "@type": "PropertyValue",
      "propertyID": "plotSize",
      "name": "Plot Size",
      "unitText": "ha",
      "description": "Size of agricultural land plot in hectares"
    },
    {
      "@type": "PropertyValue",
      "propertyID": "buyerCategory",
      "name": "Buyer Category",
      "description": "Classification of land buyer (farmer, investor, institution)"
    }
  ],
  "distribution": {
    "@type": "DataDownload",
    "encodingFormat": "CSV",
    "contentUrl": "https://repository.example.org/dataset/example.csv"
  },
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "isAccessibleForFree": true,
  "provider": {
    "@type": "Organization",
    "name": "Statistical Office Saxony-Anhalt",
    "url": "https://example.example.de/"
  }
}
```

## Quality Assurance and Validation

### Automated Validation Procedures

- **JSON-LD Syntax Validation**: Ensures proper schema.org structure and syntax
- **Required Field Completeness**: Verifies presence of mandatory metadata elements
- **Controlled Vocabulary Compliance**: Validates use of AGROVOC and other standard vocabularies
- **Geographic Coordinate Validation**: Confirms spatial coverage within reasonable bounds
- **Temporal Format Consistency**: Ensures ISO 8601 compliance for all date fields

### Community-Based Enhancement

- **Researcher Feedback Integration**: Mechanisms for metadata authors to refine and enhance descriptions
- **Expert Review Workflows**: Subject matter expert validation of domain-specific metadata
- **Version Control**: Tracking metadata improvements and corrections over time
- **Usage Analytics**: Monitoring metadata quality through usage patterns and user feedback

## Conclusion

The LASI metadata schema provides a standards-compliant framework for documenting German agricultural land market datasets within the FAIRagro ecosystem. By integrating Schema.org vocabulary with domain-specific requirements and German research infrastructure standards, the schema enables:

- Discoverability: Web-scale indexing and discovery through standard vocabularies
- Repository Integration: Compatibility with BonaRes, DataCite, and INSPIRE systems
- Quality Assurance: AI-assisted validation and enhancement of metadata quality
- Research Integration: Connection between socio-economic land data and broader agricultural research

This framework provides a foundation for agricultural research data management in Germany, supporting the transition from fragmented, poorly documented datasets to a coherent, discoverable, and reusable research data infrastructure that supports evidence-based policy making and interdisciplinary research collaboration.