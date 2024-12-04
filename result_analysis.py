from rdflib import Graph, Namespace
from typing import List, Tuple, Dict

def analyze_graph_results(graph: Graph, metrics_file: str) -> List[Dict[str, str]]:
    """
    Analyze the RDF graph to extract all measurements with values below 1,
    enriched with information from the metrics file.

    Args:
        graph (Graph): The RDF graph containing quality measurements.
        metrics_file (str): Path to the file containing metric definitions.

    Returns:
        List[Dict[str, str]]: A list of dictionaries with enriched results.
    """
    # Load the metrics graph
    metrics_graph = Graph()
    metrics_graph.parse(metrics_file, format="turtle")

    # SPARQL query to find measurements below 1
    query = """
    PREFIX dqv: <http://www.w3.org/ns/dqv#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?measurement ?value ?metric
    WHERE {
        ?measurement a dqv:QualityMeasurement ;
                     dqv:value ?value ;
                     dqv:isMeasurementOf ?metric .
        FILTER(xsd:float(?value) < 1.0)
    }
    """
    results = graph.query(query)

    # Enrich results with metric information
    enriched_results = []
    for row in results:
        measurement = str(row.measurement)
        value = float(row.value)
        metric = str(row.metric)

        # Query metric details
        metric_query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dqv: <http://www.w3.org/ns/dqv#>

        SELECT ?prefLabel ?definition
        WHERE {
            <""" + metric + """> skos:prefLabel ?prefLabel ;
                               skos:definition ?definition .
        }
        """
        metric_info = metrics_graph.query(metric_query)
        metric_details = {
            "measurement": measurement,
            "value": value,
            "metric": metric,
            "label": None,
            "definition": None
        }
        for metric_row in metric_info:
            metric_details["label"] = str(metric_row.prefLabel)
            metric_details["definition"] = str(metric_row.definition)

        enriched_results.append(metric_details)

    return enriched_results


# Test the analysis with `output/output.ttl` and the metrics file
if __name__ == "__main__":
    import os

    # Define the paths
    test_file_path = os.path.join("output", "output.ttl")
    metrics_file_path = os.path.join("DataQualityVocabulary", "FAIR_data_quality_metrics.ttl")

    # Load the RDF graph
    graph = Graph()
    try:
        graph.parse(test_file_path, format="turtle")
        print(f"Successfully loaded {test_file_path}")
    except Exception as e:
        print(f"Error loading RDF file: {e}")
        exit(1)

    # Analyze the graph
    try:
        enriched_results = analyze_graph_results(graph, metrics_file_path)
        if enriched_results:
            print("Enriched Measurements with values below 1:")
            for result in enriched_results:
                print(f"  - Measurement: {result['measurement']}")
                print(f"    Value: {result['value']}")
                print(f"    Metric: {result['metric']}")
                print(f"    Label: {result['label']}")
                print(f"    Definition: {result['definition']}\n")
        else:
            print("No measurements with values below 1 were found.")
    except Exception as e:
        print(f"Error during analysis: {e}")
