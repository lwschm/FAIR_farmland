import json
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD, DCTERMS, RDFS
from urllib.parse import quote
from datetime import datetime

# Define namespaces
FAIRAGRO = Namespace("https://fairagro.net/ontology#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
DQV = Namespace("http://www.w3.org/ns/dqv#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
PROV = Namespace("http://www.w3.org/ns/prov#")

def format_as_dqv(metadata):
    """
    Convert extracted metadata to DQV format using RDF.
    
    Args:
        metadata (dict): The extracted metadata and data sources
        
    Returns:
        dict: The metadata formatted in DQV vocabulary as JSON-LD
    """
    # Create a new RDF graph
    g = Graph()
    
    # Bind namespaces
    g.bind("dcat", DCAT)
    g.bind("dcterms", DCTERMS)
    g.bind("dqv", DQV)
    g.bind("skos", SKOS)
    g.bind("fairagro", FAIRAGRO)
    g.bind("prov", PROV)
    
    # Get DOI and encode it for URIs
    doi = metadata["metadata"].get("doi", "unknown-doi")
    doi_encoded = quote(doi, safe='')
    doi_slug = doi_encoded
    
    # Create URIs
    dataset_uri = FAIRAGRO[f"dataset-{doi_slug}"]
    distribution_uri = FAIRAGRO[f"distribution-{doi_slug}"]
    quality_metadata_uri = FAIRAGRO[f"qualityMetadata-{doi_slug}"]
    
    # Add dataset information
    g.add((dataset_uri, RDF.type, DCAT.Dataset))
    g.add((dataset_uri, DCTERMS.title, Literal(metadata["metadata"]["title"])))
    g.add((dataset_uri, DCTERMS.creator, Literal(", ".join(metadata["metadata"]["authors"]))))
    
    # Handle year value - make sure it's valid for gYear datatype (can't be 0)
    year = metadata["metadata"]["year"]
    if year > 0:
        g.add((dataset_uri, DCTERMS.date, Literal(str(year), datatype=XSD.gYear)))
    else:
        # Use a generic date string for invalid years
        g.add((dataset_uri, DCTERMS.date, Literal("Unknown year")))
    
    g.add((dataset_uri, DCTERMS.isPartOf, Literal(metadata["metadata"]["journal"])))
    g.add((dataset_uri, DCAT.distribution, distribution_uri))
    
    # Add distribution information
    g.add((distribution_uri, RDF.type, DCAT.Distribution))
    g.add((distribution_uri, DCTERMS.title, Literal(f"DOI distribution of {metadata['metadata']['title']}")))
    g.add((distribution_uri, DCAT.accessURL, URIRef(f"https://doi.org/{doi_encoded}")))
    
    # Add quality metadata
    g.add((quality_metadata_uri, RDF.type, DQV.QualityMetadata))
    g.add((quality_metadata_uri, PROV.generatedAtTime, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
    
    # Add FAIR assessment scores if available
    if "assessment" in metadata:
        assessment = metadata["assessment"]
        
        # Define FAIR metrics
        fair_metrics = {
            "findability": {
                "uri": FAIRAGRO["findabilityMetric"],
                "label": "Findability Score",
                "score": assessment.get("findability", 0),
                "reason": assessment.get("findability_reason", "")
            },
            "accessibility": {
                "uri": FAIRAGRO["accessibilityMetric"],
                "label": "Accessibility Score",
                "score": assessment.get("accessibility", 0),
                "reason": assessment.get("accessibility_reason", "")
            },
            "interoperability": {
                "uri": FAIRAGRO["interoperabilityMetric"],
                "label": "Interoperability Score",
                "score": assessment.get("interoperability", 0),
                "reason": assessment.get("interoperability_reason", "")
            },
            "reusability": {
                "uri": FAIRAGRO["reusabilityMetric"],
                "label": "Reusability Score",
                "score": assessment.get("reusability", 0),
                "reason": assessment.get("reusability_reason", "")
            }
        }
        
        # Add each FAIR metric and its measurement
        for metric_key, metric_info in fair_metrics.items():
            # Add metric definition
            g.add((metric_info["uri"], RDF.type, DQV.Metric))
            g.add((metric_info["uri"], SKOS.prefLabel, Literal(metric_info["label"], lang="en")))
            
            # Add measurement
            measurement_uri = FAIRAGRO[f"measurement-{metric_key}-{doi_slug}"]
            g.add((measurement_uri, RDF.type, DQV.QualityMeasurement))
            g.add((measurement_uri, DQV.isMeasurementOf, metric_info["uri"]))
            g.add((measurement_uri, DQV.value, Literal(metric_info["score"], datatype=XSD.decimal)))
            g.add((measurement_uri, DQV.computedOn, dataset_uri))
            
            # Add reason as a note
            if metric_info["reason"]:
                g.add((measurement_uri, DQV.note, Literal(metric_info["reason"])))
            
            # Link measurement to quality metadata
            g.add((quality_metadata_uri, DQV.hasQualityMeasurement, measurement_uri))
    
    # Add data sources as datasets
    for i, source in enumerate(metadata["data_sources"]):
        source_slug = f"{doi_slug}-source-{i}"
        source_uri = FAIRAGRO[f"dataset-{source_slug}"]
        source_distribution_uri = FAIRAGRO[f"distribution-{source_slug}"]
        
        # Source as a dataset
        g.add((source_uri, RDF.type, DCAT.Dataset))
        g.add((source_uri, DCTERMS.title, Literal(source["source_name"])))
        g.add((source_uri, DCTERMS.description, Literal(source["description"])))
        g.add((source_uri, DCAT.distribution, source_distribution_uri))
        g.add((source_uri, DCAT.keyword, Literal(", ".join(source["transaction_types"]))))
        g.add((source_uri, DCTERMS.spatial, Literal(f"{source['country']}, {source['region']}")))
        
        # Handle temporal values - ensure they're valid
        earliest_year = source.get('earliest_year', 0)
        latest_year = source.get('latest_year', 0)
        if earliest_year > 0 and latest_year > 0:
            g.add((source_uri, DCTERMS.temporal, Literal(f"{earliest_year}-{latest_year}")))
        else:
            g.add((source_uri, DCTERMS.temporal, Literal("Unknown time period")))
        
        # Add spatial resolution as a quality measurement
        spatial_resolution_metric = FAIRAGRO[f"spatialResolutionMetric"]
        g.add((spatial_resolution_metric, RDF.type, DQV.Metric))
        g.add((spatial_resolution_metric, SKOS.prefLabel, Literal("Spatial Resolution", lang="en")))
        
        spatial_resolution_measurement = FAIRAGRO[f"measurement-spatial-resolution-{source_slug}"]
        g.add((spatial_resolution_measurement, RDF.type, DQV.QualityMeasurement))
        g.add((spatial_resolution_measurement, DQV.isMeasurementOf, spatial_resolution_metric))
        g.add((spatial_resolution_measurement, DQV.value, Literal(source["spatial_resolution"])))
        
        # Add observation count as a quality measurement
        observation_count_metric = FAIRAGRO[f"observationCountMetric"]
        g.add((observation_count_metric, RDF.type, DQV.Metric))
        g.add((observation_count_metric, SKOS.prefLabel, Literal("Number of Observations", lang="en")))
        
        observation_count_measurement = FAIRAGRO[f"measurement-observation-count-{source_slug}"]
        g.add((observation_count_measurement, RDF.type, DQV.QualityMeasurement))
        g.add((observation_count_measurement, DQV.isMeasurementOf, observation_count_metric))
        
        # Ensure observation count is valid
        observation_count = source.get("number_of_observations", 0)
        if observation_count > 0:
            g.add((observation_count_measurement, DQV.value, Literal(observation_count, datatype=XSD.integer)))
        else:
            g.add((observation_count_measurement, DQV.value, Literal("Unknown", datatype=XSD.string)))
        
        # Source distribution
        g.add((source_distribution_uri, RDF.type, DCAT.Distribution))
        g.add((source_distribution_uri, DCTERMS.title, Literal(f"Distribution of {source['source_name']}")))
        g.add((source_distribution_uri, DCAT.accessURL, URIRef(source.get("url", "https://example.org/not-available"))))
        g.add((source_distribution_uri, DCTERMS.format, Literal(source.get("data_format", "unknown"))))
        g.add((source_distribution_uri, DCTERMS.description, Literal(f"Accessibility: {source['accessibility']}")))
        
        # Link quality measurements to distribution
        g.add((source_distribution_uri, DQV.hasQualityMeasurement, spatial_resolution_measurement))
        g.add((source_distribution_uri, DQV.hasQualityMeasurement, observation_count_measurement))
        
        # Link source dataset to main dataset
        g.add((dataset_uri, DCTERMS.hasPart, source_uri))
    
    # Serialize to JSON-LD
    json_ld = json.loads(g.serialize(format="json-ld"))
    
    return json_ld 