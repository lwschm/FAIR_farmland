# Concept for a Schema.org-Based Farmland Research Metadatabase (Germany)

## Introduction

Building a metadatabase for farmland research data in Germany (focusing on farmland sales transactions data) requires a schema that is both researcher-friendly and compliant with web standards. The goal is to make data discoverable, integratable, and aligned with FAIR principles (Findable, Accessible, Interoperable, Reusable). This concept outlines a metadata schema based on Schema.org (using JSON-LD format) to describe farmland sale datasets, ensuring compatibility with repositories like BonaRes (a German agricultural data repository) and others. By using schema.org and related standards, the metadata can be easily harvested by search engines and data catalogs, increasing the data's visibility to researchers. Importantly, actual farmland sale transaction records (prices, dates, locations, etc.) are considered high-quality ("gold standard") data for land economics research, so a robust metadata structure will maximize their reusability.

## Target Audience: This schema is designed for agricultural researchers and data managers who need to document, publish, and integrate farmland transaction datasets. It emphasizes clarity, consistency, and integration with existing data infrastructures, without assuming any specific software stack (the output is standard JSON-LD metadata).

## Approach Overview

### Schema.org Integration

The metadatabase leverages schema.org vocabulary, particularly the Dataset schema for data description, nested within a ScholarlyArticle if the data is associated with a publication. Schema.org was chosen because it's widely used for data indexing (e.g., Google Dataset Search indexes datasets via schema.org metadata on web pages), and it's flexible enough to accommodate domain-specific extensions.

### Standards Alignment

To ensure interoperability with German and international repositories, the schema aligns with:

- **DataCite Metadata Schema**: for DOI registration and citation information
- **INSPIRE (EU Spatial Data standard)**: for geospatial metadata compliance
- **AGROVOC Thesaurus**: for consistent agricultural keywords (used by BonaRes to tag data)

By adhering to these standards, any metadata record can be cross-walked into repository-specific formats. For example, BonaRes requires datasets to have DOIs and uses DataCite schema fields, as well as INSPIRE for spatial info. Our schema.org approach includes equivalent fields (like identifier for DOI, spatialCoverage for location, etc.), ensuring the farmland data can be easily registered and published in BonaRes or similar portals.

### Metadata Focus

This concept concentrates on the metadata structure of the research dataset (the descriptive information), not the raw data storage. We outline what fields (metadata "columns") should describe a farmland transaction dataset and how they map to schema.org. Ultimately, the metadata will be presented in JSON format (JSON-LD), which is both human-readable and machine-actionable for web integration. No specific database or software is assumed; the JSON-LD could be stored in any catalog or embedded in webpages.

## Metadata Schema Architecture

### Hierarchical Structure

The metadata schema follows a nested, hierarchical design reflecting real-world context and provenance. At the top level we have a ScholarlyArticle (or Report) representing the research context (if the dataset is part of a study or publication), under which one or more Dataset entries are described. For each Dataset, further nested properties capture details like variables, spatial/temporal coverage, etc. This hierarchy ensures that:

- **Context is preserved**: Each dataset is linked to its research publication or project for context
- **Reusability**: Datasets can be understood independently, but also traced back to sources
- **Integration**: The structure can be parsed to fill multiple catalogs (publication databases and data repositories)

### Schematic Overview

```
ScholarlyArticle (or ResearchProject)
├── Basic Publication Info (title, authors, datePublished, DOI, etc.)
├── Keywords and License
├── dataset: Dataset
│    ├── Dataset Title and Description
│    ├── Identifier (e.g., DOI for dataset if available)
│    ├── Spatial Coverage (location of farmland)
│    ├── Temporal Coverage (date range of transactions)
│    ├── Variables Measured (key attributes like price, area)
│    ├── Keywords (e.g., "land sale", "farmland")
│    ├── Access Info (access rights, license)
│    └── Optionally: distribution (links to data files)
└── Optionally: additionalProperty or processingInfo (if capturing processing details)
```

This approach nests the Dataset within the context of a publication. If the dataset is standalone (not from a paper), the top-level could simply be Dataset by itself. However, linking data to publications is useful for academic datasets to provide provenance.

### Schema.org Types Employed

- **ScholarlyArticle**: Chosen as the top-level type to model academic outputs. It inherits from CreativeWork but adds specific fields for academic citation. This is ideal to capture publication metadata (DOI, authors, etc.) which many repositories (and DataCite) expect.

- **Dataset**: Represents the actual dataset. It includes properties for description, coverage, format, etc. This is the core of our metadatabase entry, describing farmland sales data in detail.

- **Place (with GeoShape)**: Used for spatial coverage to denote geographic focus (e.g., a state or region in Germany).

- **PropertyValue**: Used to describe variables (columns) within the dataset in a flexible way. Each key attribute of the dataset (like sale price, land area) is given as a PropertyValue with a name and value (and optionally a unit or identifier).

- **Organization/Person**: For author and publisher information, ensuring proper credit and contact info.

- **DataCatalog (optional)**: If integrating into a larger catalog, the dataset might reference a catalog entry or be part of a DataCatalog. For example, BonaRes itself could be represented as a DataCatalog in schema.org terms; our dataset could include "includedInDataCatalog": "BonaRes Repository".

This multi-type integration means our metadata can capture all necessary details. For instance, a ScholarlyArticle can have an author (Person) and a publisher (Organization), and a Dataset can have spatialCoverage (Place), all within one JSON-LD document.

## Core Components of the Metadata Schema

### 1. Publication Metadata (Context)

If the farmland transaction data is part of a research study or report, the metadata begins with the publication context. Key fields include:

- **Identifier (DOI)**: A persistent identifier for the publication (if available). This maps to @id in JSON-LD and identifier property. Using DOIs is crucial for integration and citation.
- **Title (name)**: Title of the article or report.
- **Authors (author)**: List of authors (as Persons, with names and affiliations optionally).
- **Publication Date (datePublished)**: Year (or full date) of publication.
- **Publisher (publisher)**: The institution or journal.
- **License (license)**: License of the publication or data (e.g., Creative Commons).
- **Keywords (keywords)**: Keywords to describe the content (could include terms like farmland, sales, land market, Germany, etc.). Using controlled vocabularies like AGROVOC for keywords enhances interoperability.

**Rationale**: Using ScholarlyArticle ensures we capture rich bibliographic metadata. This is in line with DataCite requirements for dataset registration (since DataCite often links datasets with publications). For example, a dataset could inherit the publication's DOI or have its own; either way, linking them is beneficial. If the data is not linked to a paper, one could use a more generic Dataset at top level, but for research data, context is often a publication.

### 2. Dataset Description

The Dataset is the central part of the metadata, describing the farmland sales transactions data. Key sub-components include:

#### Basic Information

- **Name (name)**: A descriptive title of the dataset, e.g. "Farmland Sales Transactions in Saxony-Anhalt (2014–2017)". This should be concise and informative.

- **Description (description)**: A brief summary of the dataset content. For instance: "This dataset contains records of agricultural land sales in Saxony-Anhalt, Germany, from 2014 to 2017, including sale dates, prices, land area, and buyer type."

- **Identifier**: If the dataset itself has a DOI or other ID (apart from the publication's ID), include it (as identifier or @id). This enables independent citation of the dataset.

#### Spatial Coverage (spatialCoverage)

Geographic area covered by the data. Implemented using a Place with a name (e.g., "Saxony-Anhalt, Germany") and a GeoShape or coordinates. For example:

```json
"spatialCoverage": {
  "@type": "Place",
  "name": "Saxony-Anhalt, Germany",
  "geo": {
    "@type": "GeoShape",
    "box": "50.7 10.9 53.1 13.1" 
  }
}
```

Here GeoShape.box gives a latitude-longitude bounding box of the region for simplicity. This follows standard WGS84 coordinates. More complex shapes (polygons) or place identifiers (like an INSPIRE location code) could be used if needed, but a bounding box is a simple way to declare spatial extent. Using the region name and country code (implicitly in name or as addressCountry: "DE") helps integration with catalogs that filter by country.

#### Temporal Coverage (temporalCoverage)

The time span of the dataset, given as an interval string (ISO 8601 format). For example: "2014/2017" indicates the data covers 2014 through 2017 inclusive. This helps users and catalogs know the period of data collection. It could be more granular (e.g., "2014-01/2017-12" for month range) if needed.

#### Variables Measured (variableMeasured)

This is critical for understanding what attributes the dataset contains. We use an array of PropertyValue entries to list each key variable (or column) in the dataset. Each PropertyValue can include:

- **propertyID**: a unique identifier or code for the variable (could be a short code or ontology term)
- **name**: human-friendly name of the variable
- **value (or unitText etc.)**: an example value or, more appropriately, the general type of value
- **unitText (if numeric and has units)**: e.g., "EUR" for price, "ha" for hectares

#### Farmland Sales Transaction Data – Key Fields

Typical variables for land sale transactions include:

- **Transaction Date**: Date of the sale record
- **Sale Price**: Price at which the land was sold, in Euros
- **Land Area**: Area of land sold, in hectares
- **Land Use Type**: Classification of the land (e.g., arable, pasture)
- **Buyer Type**: Category of buyer (e.g., farmer, private investor, company, etc.)
- **(Possibly) Parcel ID or Location Detail**: An identifier for the specific parcel or a more granular location indicator

Each of these can be represented as a PropertyValue. For example:

```json
"variableMeasured": [
  {
    "@type": "PropertyValue",
    "propertyID": "salePrice",
    "name": "Sale Price",
    "unitText": "EUR",
    "description": "Transaction sale price in Euros"
  },
  {
    "@type": "PropertyValue",
    "propertyID": "landArea",
    "name": "Land Area",
    "unitText": "ha",
    "description": "Area of land sold in hectares"
  },
  {
    "@type": "PropertyValue",
    "propertyID": "transactionDate",
    "name": "Transaction Date",
    "description": "Date of land sale (YYYY-MM-DD)"
  },
  {
    "@type": "PropertyValue",
    "propertyID": "landUseType",
    "name": "Land Use Type",
    "description": "Type of land use (e.g., arable, pasture)"
  },
  {
    "@type": "PropertyValue",
    "propertyID": "buyerType",
    "name": "Buyer Type",
    "description": "Category of buyer (e.g., farmer, investor)"
  }
]
```

Each PropertyValue here acts like a column definition in the metadata, describing what each field means. By providing description for each variable, we ensure clarity for future users. The use of propertyID allows linking to standard definitions or ontologies.

#### Additional Dataset Properties

- **Keywords**: In addition to publication keywords, the dataset can have its own keywords list. These might include terms like "land sales", "farmland transactions", specific regions, etc. Using standardized vocabularies (e.g. AGROVOC or GEMET for environmental terms) is recommended for interoperability.

- **License**: The dataset's license (often the same as publication, but should be explicit). E.g., "license": "https://creativecommons.org/licenses/by/4.0/" for CC BY 4.0.

- **Access conditions**: Using schema.org's isAccessibleForFree or conditionsOfAccess can indicate if the dataset is open, restricted, etc.

- **Related publication link**: If using ScholarlyArticle as context, the link is inherent. If not, one could use citation property to link a paper.

### 3. Example Farmland Transaction Dataset Fields and Definitions

To clarify the dataset's content, below are typical column definitions (variables) one would expect in a farmland sales transactions dataset:

| Dataset Field (Column) | Description | Metadata Representation |
|------------------------|-------------|------------------------|
| Transaction ID | Unique identifier for each transaction record | identifier (as part of Dataset distribution or implicit in data) |
| Transaction Date | Date when the sale was recorded/finalized | variableMeasured: transactionDate (PropertyValue with expected Date format) |
| Sale Price (EUR) | Sale price of the land in Euros | variableMeasured: salePrice (PropertyValue with unitText "EUR") |
| Land Area (ha) | Size of the land parcel sold, in hectares | variableMeasured: landArea (PropertyValue with unitText "ha") |
| Land Use Type | Type of land use or crop at time of sale | variableMeasured: landUseType (PropertyValue, possibly with ontology code) |
| Buyer Type | Category of buyer | variableMeasured: buyerType (PropertyValue, could enumerate values) |
| Location Details | Specific location info | Primarily captured under spatialCoverage |

### 4. Processing and Provenance Information (Optional)

If the dataset was generated or processed through a specific pipeline, metadata can capture that provenance. For example:

```json
"processingInformation": {
  "@type": "CreativeWork",
  "description": "Data processed and quality-checked by the FAIRagro Pipeline v1.2",
  "datePublished": "2025-06-01",
  "softwareApplication": "FAIRagro Toolkit 1.2"
}
```

This could also use schema:Action type (e.g., DataProcessing) to describe an action taken on the data. This is mostly for internal provenance and aligns with advanced metadata practices.

## Controlled Vocabularies and Value Standards

To maximize interoperability, certain fields should use controlled vocabularies or standard codes:

### Locations
For German farmland, use official names of states (Bundesländer) or regions, possibly with codes. E.g., use "Saxony-Anhalt" (English) or "Sachsen-Anhalt" (German) consistently. INSPIRE's NUTS or LAU codes could be included for compatibility with other EU datasets.

### Land Use Types
Could reference a vocabulary like LCML (Land Cover Meta Language) or simply a controlled list: e.g., {arable, pasture, forest, mixed-use, other}. Using standard terms (perhaps AGROVOC or INSPIRE Land Use themes) will help integration.

### Buyer Type
Define a controlled list in the metadata documentation (e.g., categories of buyers). This field might not always be available, but if it is, it's useful for analysis.

### Research Keywords
Using AGROVOC for keywords is recommended since BonaRes and many agricultural data portals integrate AGROVOC. For example, instead of free text "farmland", use the AGROVOC term for farmland and include its identifier if possible.

### Data Type Classification
Internally, we might classify the dataset under a certain type (for internal cataloging). For example: "transaction_data" vs "experimental_data". In our case, transaction_data is appropriate.

## Integration with Repositories (BonaRes and Others)

### BonaRes Repository

BonaRes uses a custom metadata schema merging INSPIRE (for geospatial info) and DataCite (for citation and DOI). By including spatialCoverage and the usual citation fields, we cover both aspects. The mapping includes:

- Title → name
- Authors → author
- DOI → identifier/@id
- Abstract/Description → description
- Spatial extent → spatialCoverage
- Temporal extent → temporalCoverage
- Variables (parameters) → variableMeasured
- License → license
- Keywords → keywords (with AGROVOC URIs ideally)

### Other German/International Repositories

Many repositories use either DataCite or Dublin Core or DCAT metadata. Our schema.org can be crosswalked to those:

- **DataCite XML**: We have all the pieces (creators, title, publisher, publicationYear, geoLocations, etc.)
- **DCAT (Data Catalog Vocabulary)**: DCAT has Dataset as well, with similar fields
- **OAI-PMH harvesting**: If a repository harvests metadata via OAI-PMH in Dublin Core, our fields cover the DC core fields
- **FAIR Data Principles**: By including rich metadata and identifiers, we adhere to FAIR principles

## Technical Implementation Notes

### Format
JSON-LD is the chosen format for metadata exchange. JSON-LD can be easily generated and consumed by web services, and it can also be embedded in HTML pages or sent via APIs.

### No Specific Stack Required
This concept does not assume a particular database or platform. The metadatabase could be:
- A simple collection of JSON files in a Git repository
- A dedicated metadata catalog software
- Part of a research data management system

### Validation
To ensure quality, a JSON Schema or SHACL (for RDF) can be developed to validate that each metadata record conforms to the required structure.

### Example Workflow
1. Researchers input dataset info (perhaps via a web form or metadata editor)
2. The system populates a JSON-LD template with that info
3. The JSON-LD is then published (on a webpage, via an API endpoint, or directly submitted to a repository)
4. Search engines or repository harvesters pick it up, and users can find the dataset online

## Example Metadata Record (JSON-LD)

Below is a simplified example JSON-LD metadata for a hypothetical farmland transaction dataset:

```json
{
  "@context": "https://schema.org/",
  "@type": "ScholarlyArticle",
  "@id": "https://doi.org/10.1234/FARMLAND.SAX14-17", 
  "name": "Farmland Market Analysis in Saxony-Anhalt, 2014-2017",
  "author": [
    { "@type": "Person", "name": "Dr. Anna Müller" },
    { "@type": "Person", "name": "Jonas Schmidt" }
  ],
  "datePublished": "2025-03-01",
  "publisher": { "@type": "Organization", "name": "Leibniz-ZALF" },
  "keywords": ["farmland sale", "land transaction", "Saxony-Anhalt", "land market"],
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "dataset": {
    "@type": "Dataset",
    "name": "Farmland Sales Transactions – Saxony-Anhalt (2014-2017)",
    "description": "Dataset of 150 farmland sale transactions in Saxony-Anhalt, Germany, from 2014 to 2017. Includes sale dates, prices (EUR), land areas (ha), land use type, and buyer category for each transaction.",
    "identifier": "https://doi.org/10.5678/dataset12345", 
    "spatialCoverage": {
      "@type": "Place",
      "name": "Saxony-Anhalt, DE",
      "geo": {
        "@type": "GeoShape",
        "box": "50.7 10.9 53.1 13.1"
      }
    },
    "temporalCoverage": "2014-01/2017-12",
    "variableMeasured": [
      {
        "@type": "PropertyValue",
        "propertyID": "transactionDate",
        "name": "Transaction Date",
        "description": "Date of sale (YYYY-MM-DD)"
      },
      {
        "@type": "PropertyValue",
        "propertyID": "salePrice",
        "name": "Sale Price",
        "unitText": "EUR",
        "description": "Sale price in Euros"
      },
      {
        "@type": "PropertyValue",
        "propertyID": "landArea",
        "name": "Land Area",
        "unitText": "ha",
        "description": "Land area in hectares"
      },
      {
        "@type": "PropertyValue",
        "propertyID": "landUseType",
        "name": "Land Use Type",
        "description": "Type of land use (arable, pasture, etc.)"
      },
      {
        "@type": "PropertyValue",
        "propertyID": "buyerType",
        "name": "Buyer Type",
        "description": "Category of buyer (e.g., farmer, investor)"
      }
    ],
    "keywords": ["agricultural land", "land sale", "transaction data", "Germany"],
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "isAccessibleForFree": true,
    "url": "https://fairagro.example.org/dataset/SA_land_sales_2014-2017"
  }
}
```

In this JSON:
- The top-level is a ScholarlyArticle with a DOI as @id
- It contains one dataset entry of type Dataset with its own DOI
- Both German context and international standards are used
- The url in dataset points to a landing page where the data can be accessed
- The variables listed match the earlier table of columns
- No actual data values are in metadata, just descriptions and units of each field

## Conclusion

This concept provides a comprehensive metadata schema for a farmland research data metadatabase, specifically tailored to farmland sales transaction data in Germany. By using schema.org in JSON-LD, it ensures the metadata is web-friendly and search engine indexed, increasing findability for researchers.

At the same time, aligning with DataCite and INSPIRE standards means the records are ready for integration into national repositories like BonaRes, which emphasize DOIs and spatial metadata.

The schema is designed to capture all crucial information about farmland sales datasets: from the context of the research (publication details) to the specifics of the data (where, when, what variables). It caters to researchers' needs by clearly defining each data element and ensuring that terms and units are standardized.

Finally, the use of an open, flexible format (JSON-LD) without tying to a particular tech stack makes the solution sustainable. It can evolve with schema.org updates or domain standards, and it can be adopted in various environments. By following this concept, the FAIR Agro project can build a metadatabase that not only meets current standards but is robust against future integration demands, thereby truly FAIR-ifying German farmland transaction data for the broader research community.