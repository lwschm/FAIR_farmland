import csv
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD

# Define namespaces
DAQ = Namespace("http://purl.org/eis/vocab/daq#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
DQV = Namespace("http://www.w3.org/ns/dqv#")
DUV = Namespace("http://www.w3.org/ns/duv#")
OA = Namespace("http://www.w3.org/ns/oa#")
PROV = Namespace("http://www.w3.org/ns/prov#")
SDMX_ATTRIBUTE = Namespace("http://purl.org/linked-data/sdmx/2009/attribute#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
EX = Namespace("http://fairagro.net/vocab#")


def list_to_rdf(dataset_name: str, dataset_uri: str, results: list) -> Graph:
    # Create a graph
    g = Graph()

    # Bind prefixes
    g.bind("daq", DAQ)
    g.bind("dcat", DCAT)
    g.bind("dcterms", DCTERMS)
    g.bind("dqv", DQV)
    g.bind("duv", DUV)
    g.bind("oa", OA)
    g.bind("prov", PROV)
    g.bind("sdmx-attribute", SDMX_ATTRIBUTE)
    g.bind("skos", SKOS)
    g.bind("ex", EX)

    # Define the base URI for the dataset and metrics
    dataset_uri_ref = URIRef(dataset_uri)
    metric_uris = [
        "UniqueIdentifier", "IdentifierPersistence", "DataIdentifierPersistence", "StructuredMetadata",
        "GroundedMetadata", "DataIdentifierExplicitlyInMetadata", "MetadataIdentifierExplicitlyInMetadata",
        "SearchableInMajorSearchEngine", "UsesOpenFreeProtocolForDataRetrieval",
        "UsesOpenFreeProtocolForMetadataRetrieval", "DataAuthenticationAndAuthorization",
        "MetadataAuthenticationAndAuthorization", "MetadataPersistence",
        "MetadataKnowledgeRepresentationLanguageWeak", "MetadataKnowledgeRepresentationLanguageStrong",
        "DataKnowledgeRepresentationLanguageWeak", "DataKnowledgeRepresentationLanguageStrong",
        "MetadataUsesFAIRVocabulariesWeak", "MetadataUsesFAIRVocabulariesStrong",
        "MetadataContainsQualifiedOutwardReferences", "MetadataIncludesLicenseStrong",
        "MetadataIncludesLicenseWeak"
    ]

    fair_components = [
        "F", "F", "F", "F",
        "F", "F", "F",
        "F", "A",
        "A", "A",
        "A", "A",
        "I", "I",
        "I", "I",
        "I", "I",
        "I", "R",
        "R"
    ]

    # Add the dataset to the graph
    g.add((dataset_uri_ref, RDF.type, DCTERMS.Dataset))
    g.add((dataset_uri_ref, DCTERMS.title, Literal(dataset_name)))

    # Add each metric result to the graph
    for i, score in enumerate(results[:-1]):
        metric_uri = URIRef(f"http://fairagro.net/metric/FES/{fair_components[i]}/{metric_uris[i]}")
        g.add((metric_uri, RDF.type, DQV.Metric))
        g.add((metric_uri, DQV.isMeasurementOf, dataset_uri_ref))
        g.add((metric_uri, DQV.value, Literal(score, datatype=XSD.integer)))

    # Add the average score
    average_score_uri = URIRef("http://fairagro.net/metric/FES/average/AverageScore")
    g.add((average_score_uri, RDF.type, DQV.Metric))
    g.add((average_score_uri, DQV.isMeasurementOf, dataset_uri_ref))
    g.add((average_score_uri, DQV.value, Literal(results[-1], datatype=XSD.integer)))

    return g


def main():
    # Open file dialog to select CSV file
    Tk().withdraw()  # We don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])

    if not filename:
        print("No file selected")
        return

    # Read CSV file
    with open(filename, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        rows = list(csvreader)
        if len(rows) < 1 or len(rows[0]) < 2:
            print("CSV file does not have enough columns")
            return

        # Extract dataset name and URI from the single row
        dataset_name = rows[0][0]
        dataset_uri = rows[0][1]

        # Metric results are hardcoded in the script
        results = ['100', '100', '0', '0', '0', '0', '0', '0', '0', '100', '0', '100', '0', '0', '0', '0', '0', '0',
                   '0', '0', '0', '0', '18']

        # Generate RDF graph
        g = list_to_rdf(dataset_name, dataset_uri, results)

        # Serialize the graph to a file in Turtle format
        output_filename = "fair_assessment.ttl"
        with open(output_filename, "wb") as f:
            f.write(g.serialize(format="turtle").encode("utf-8"))

        print(f"RDF data has been written to {output_filename}")


if __name__ == "__main__":
    main()
