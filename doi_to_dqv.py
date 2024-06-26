import sys
import re
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, RDF, XSD
from doi_info_fetcher import get_datacite_doi_info

# Namespaces
FAIRAGRO = Namespace("https://fairagro.net/ontology#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCTERMS = Namespace("http://purl.org/dc/terms/")


def create_dqv_representation(doi: str):
    dataset_info = get_datacite_doi_info(doi)
    if not dataset_info:
        return None

    g = Graph()

    doi_slug = doi.replace('/', '-')
    dataset_uri = FAIRAGRO[f"dataset-{doi_slug}"]
    distribution_uri = FAIRAGRO[f"distribution-{doi_slug}"]

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

    return g


if __name__ == "__main__":
    # Check if the script received exactly one command-line argument (the DOI)
    if len(sys.argv) != 2:
        # Prompt the user for a DOI if not provided as a command-line argument
        doi = input("Please enter a DOI: ")
        if not doi:
            print("No DOI provided. Exiting.")
            sys.exit(1)
    else:
        # Assign the DOI provided as the command-line argument to the variable `doi`
        doi = sys.argv[1]

    graph = create_dqv_representation(doi)
    if graph:
        output_file = f"output_{doi.replace('/', '_')}.ttl"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(graph.serialize(format='turtle'))
        print(f"Output written to {output_file}")
    else:
        print("Failed to create DQV representation.")
