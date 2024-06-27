import sys
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, RDF, XSD, PROV, RDFS
from doi_info_fetcher import get_datacite_doi_info
from FES_evaluation import fes_evaluate_to_list  # Import the fes_evaluate_to_list method
from datetime import datetime

# Namespaces
FAIRAGRO = Namespace("https://fairagro.net/ontology#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
DQV = Namespace("http://www.w3.org/ns/dqv#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

# Read the metrics and checkers Turtle files into separate graphs
metrics_graph = Graph()
metrics_graph.parse("fair_data_quality_metrics.ttl", format='turtle')

checkers_graph = Graph()
checkers_graph.parse("fair_quality_services.ttl", format='turtle')

# Mapping of FES evaluation results to metric URIs
fes_metric_mapping = {
    "category": FAIRAGRO["FAIRDataQuality"],
    "dimensions": {
        "findability": {
            "dimension_uri": FAIRAGRO["findability"],
            "definition": "The degree to which data is easy to find for both humans and computers. Metadata and data should be easy to discover with search mechanisms and be uniquely identifiable using standard identifiers.",
            "metrics": [
                FAIRAGRO["FES-UniqueIdentifierMetric"],
                FAIRAGRO["FES-IdentifierPersistenceMetric"],
                FAIRAGRO["FES-DataIdentifierPersistenceMetric"],
                FAIRAGRO["FES-StructuredMetadataMetric"],
                FAIRAGRO["FES-GroundedMetadataMetric"],
                FAIRAGRO["FES-DataIdentifierExplicitlyInMetadataMetric"],
                FAIRAGRO["FES-MetadataIdentifierExplicitlyInMetadataMetric"],
                FAIRAGRO["FES-SearchableInMajorSearchEngineMetric"]
            ]
        },
        "accessibility": {
            "dimension_uri": FAIRAGRO["accessibility"],
            "definition": "The degree to which data is retrievable and accessible by authorized individuals or systems. This includes providing metadata that allows data to be accessed through well-defined protocols.",
            "metrics": [
                FAIRAGRO["FES-OpenFreeProtocolDataRetrievalMetric"],
                FAIRAGRO["FES-OpenFreeProtocolMetadataRetrievalMetric"],
                FAIRAGRO["FES-DataAuthenticationAuthorizationMetric"],
                FAIRAGRO["FES-MetadataAuthenticationAuthorizationMetric"],
                FAIRAGRO["FES-MetadataPersistenceMetric"]
            ]
        },
        "interoperability": {
            "dimension_uri": FAIRAGRO["interoperability"],
            "definition": "The degree to which data is able to be integrated with other data and systems. This involves using shared vocabularies, ontologies, and standards to enable data exchange and reuse across different contexts.",
            "metrics": [
                FAIRAGRO["FES-MetadataKnowledgeRepresentationLanguageWeakMetric"],
                FAIRAGRO["FES-MetadataKnowledgeRepresentationLanguageStrongMetric"],
                FAIRAGRO["FES-DataKnowledgeRepresentationLanguageWeakMetric"],
                FAIRAGRO["FES-DataKnowledgeRepresentationLanguageStrongMetric"],
                FAIRAGRO["FES-MetadataUsesFAIRVocabulariesWeakMetric"],
                FAIRAGRO["FES-MetadataUsesFAIRVocabulariesStrongMetric"],
                FAIRAGRO["FES-MetadataContainsQualifiedOutwardReferencesMetric"]
            ]
        },
        "reusability": {
            "dimension_uri": FAIRAGRO["reusability"],
            "definition": "The degree to which data can be reused for future research and analysis. This involves providing rich metadata, clear usage licenses, and provenance information to ensure data can be effectively reused.",
            "metrics": [
                FAIRAGRO["FES-MetadataIncludesLicenseStrongMetric"],
                FAIRAGRO["FES-MetadataIncludesLicenseWeakMetric"]
            ]
        }
    }
}




def create_dqv_representation(doi: str, fes_evaluation_result: list, start_time: datetime, end_time: datetime):
    dataset_info = get_datacite_doi_info(doi)
    if not dataset_info:
        return None

    g = Graph()

    # Bind namespaces
    g.bind("dcat", DCAT)
    g.bind("dcterms", DCTERMS)
    g.bind("dqv", DQV)
    g.bind("skos", SKOS)
    g.bind("fairagro", FAIRAGRO)
    g.bind("prov", PROV)

    doi_slug = doi.replace('/', '-')
    dataset_uri = FAIRAGRO[f"dataset-{doi_slug}"]
    distribution_uri = FAIRAGRO[f"distribution-{doi_slug}"]
    fes_service_uri = FAIRAGRO["FAIREvaluationServices"]
    quality_metadata_uri = FAIRAGRO[f"qualityMetadata-{doi_slug}"]
    quality_checking_activity_uri = FAIRAGRO[f"qualityChecking-{doi_slug}"]

    # Adding dataset information
    g.add((dataset_uri, RDF.type, DCAT.Dataset))
    g.add((dataset_uri, DCTERMS.title, Literal(dataset_info["title"])))
    g.add((dataset_uri, DCAT.distribution, distribution_uri))

    # Adding distribution information
    g.add((distribution_uri, RDF.type, DCAT.Distribution))
    g.add((distribution_uri, DCTERMS.title, Literal("DOI distribution of dataset")))
    g.add((distribution_uri, DCAT.accessURL, URIRef(f"https://doi.org/{doi}")))
    g.add((distribution_uri, DCTERMS["format"], Literal(dataset_info["resource_type"])))

    if "byteSize" in dataset_info:
        g.add((distribution_uri, DCAT.byteSize, Literal(dataset_info["byteSize"], datatype=XSD.decimal)))

    # Adding quality metadata
    g.add((quality_metadata_uri, RDF.type, DQV.QualityMetadata))
    g.add((quality_metadata_uri, PROV.wasAttributedTo, fes_service_uri))
    g.add((quality_metadata_uri, PROV.generatedAtTime, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
    g.add((quality_metadata_uri, PROV.wasGeneratedBy, quality_checking_activity_uri))

    # Adding quality checking activity
    g.add((quality_checking_activity_uri, RDF.type, PROV.Activity))
    g.add((quality_checking_activity_uri, RDFS.label,
           Literal("The checking of the dataset distribution's quality", datatype=XSD.string)))
    g.add((quality_checking_activity_uri, PROV.wasAssociatedWith, fes_service_uri))
    g.add((quality_checking_activity_uri, PROV.used, distribution_uri))
    g.add((quality_checking_activity_uri, PROV.generated, quality_metadata_uri))
    g.add((quality_checking_activity_uri, PROV.startedAtTime, Literal(start_time.isoformat(), datatype=XSD.dateTime)))
    g.add((quality_checking_activity_uri, PROV.endedAtTime, Literal(end_time.isoformat(), datatype=XSD.dateTime)))

    # Adding category and dimensions from the metrics_graph
    category_uri = fes_metric_mapping["category"]
    g.add((category_uri, RDF.type, DQV.Category))
    for s, p, o in metrics_graph.triples((category_uri, None, None)):
        g.add((s, p, o))

    for dimension_key, dimension_info in fes_metric_mapping["dimensions"].items():
        dimension_uri = dimension_info["dimension_uri"]
        g.add((dimension_uri, RDF.type, DQV.Dimension))
        g.add((dimension_uri, DQV.inCategory, category_uri))
        g.add((dimension_uri, SKOS.prefLabel, Literal(dimension_key.capitalize(), lang="en")))
        g.add((dimension_uri, SKOS.definition, Literal(dimension_info["definition"], lang="en")))
        for s, p, o in metrics_graph.triples((dimension_uri, None, None)):
            g.add((s, p, o))

    # Adding FES quality service if evaluation result exists
    if fes_evaluation_result:
        for s, p, o in checkers_graph.triples((fes_service_uri, None, None)):
            g.add((s, p, o))

        # Adding quality measurements and metrics
        measurements = []
        metric_index = 0
        for dimension_info in fes_metric_mapping["dimensions"].values():
            for metric_uri in dimension_info["metrics"]:
                if metric_index >= len(fes_evaluation_result):
                    break
                result = fes_evaluation_result[metric_index]
                measurement_uri = FAIRAGRO[f"measurement-{metric_index + 1}__{doi_slug}"]
                metric_index += 1

                # Add metric to the graph
                for s, p, o in metrics_graph.triples((metric_uri, None, None)):
                    g.add((s, p, o))

                g.add((measurement_uri, RDF.type, DQV.QualityMeasurement))
                g.add((measurement_uri, DQV.isMeasurementOf, metric_uri))
                g.add((measurement_uri, DQV.value, Literal(result, datatype=XSD.float)))
                g.add((measurement_uri, DQV.computedBy, fes_service_uri))
                measurements.append(measurement_uri)

        # Linking measurements to the distribution
        for measurement in measurements:
            g.add((distribution_uri, DQV.hasQualityMeasurement, measurement))

    return g


if __name__ == "__main__":
    # Fixed DOI for testing
    doi = "10.20387/bonares-tdgx-339v"

    # Define the start time before the evaluation
    start_time = datetime.now()

    # Get the evaluation result from FES
    # fes_evaluation_result = fes_evaluate_to_list(doi)
    fes_evaluation_result = ['1', '1', '0', '1', '1', '0', '0', '0', '0', '1', '0', '1', '0', '1', '1', '0', '0', '1',
                             '0', '1', '0', '1']
    if fes_evaluation_result:
        print("FES Evaluation Result:", fes_evaluation_result)

    # Define the end time after the evaluation
    end_time = datetime.now()

    # Create DQV representation
    graph = create_dqv_representation(doi, fes_evaluation_result, start_time, end_time)
    if graph:
        output_file = f"output_{doi.replace('/', '_')}.ttl"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(graph.serialize(format='turtle'))
        print(f"Output written to {output_file}")
    else:
        print("Failed to create DQV representation.")
