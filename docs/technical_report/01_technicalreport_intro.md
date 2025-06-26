# Technical Report: Schema.org-Based Metadata Schema for German Farmland Research Datasets

## Introduction

The transparent and standardized documentation of farmland sales transactions plays a vital role in agricultural economics, land policy analysis, and rural development research. In Germany, where land markets are regionally fragmented and land ownership is increasingly scrutinized in light of climate policy, demographic change, and structural transformation, high-quality metadata describing land sales datasets is essential for enabling reproducible, comparative, and policy-relevant research.

## The Challenge

Yet, despite the growing volume and importance of farmland transaction data—sourced from land registries, statistical offices, and research institutions—there remains a lack of interoperable metadata standards tailored to this domain. Datasets are often published with minimal context, non-standard variable definitions, and without machine-readable structures, making them difficult to integrate into centralized research repositories or discover via modern web tools.

## Our Approach

This technical report addresses this gap by proposing a schema.org-based metadata schema specifically designed for farmland research datasets in Germany, with a focus on farmland sales transactions. Schema.org, a widely adopted vocabulary for structured data on the web, offers a powerful foundation for making research datasets discoverable, linkable, and semantically rich. 

By aligning with schema.org—and with related standards such as DataCite, DCAT, and INSPIRE—this approach facilitates:

- **Improved discoverability** of datasets through web search engines and data catalogs
- **Interoperability** with existing German research data infrastructures such as BonaRes
- **Reusability and transparency** of data through standardized variable descriptions and clear provenance
- **Compliance with FAIR principles**, particularly in the domains of findability, accessibility, and interoperability

The resulting metadata framework is output as JSON-LD, a lightweight and flexible format that can be embedded into websites, submitted to data repositories, or used as part of internal metadata catalogs.

## Target Audience

The intended audience for this report includes:
- Agricultural researchers
- Data managers
- Repository curators  
- Technical teams in research consortia who need to catalog, publish, or integrate land market datasets

While the schema focuses on farmland sales transactions, it is extensible to broader use cases in agricultural land use and rural land governance.

## Impact and Vision

By providing a robust, standards-aligned, and practical schema, this report contributes to building the digital infrastructure necessary for a transparent, data-driven understanding of land markets—a critical foundation for evidence-based policymaking and sustainable land use in Germany and beyond.