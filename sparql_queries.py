from SPARQLWrapper import SPARQLWrapper, JSON
from tabulate import tabulate

# Define SPARQL endpoints
SPARQL_ENDPOINTS = {
    'bonares': 'http://localhost:3030/BonaRes/sparql',
    'metrics': 'http://localhost:3030/Metrics/sparql',
    # Add additional endpoints as needed
}

# Define common prefixes
COMMON_PREFIXES = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX fairagro: <https://fairagro.net/ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

# Dictionary of SPARQL query templates
QUERY_TEMPLATES = {
    "fetch_values_below_one": """
    SELECT DISTINCT ?doi ?agent ?dimension ?definition ?value
    WHERE {{
      SERVICE <{metrics_endpoint}> {{
        ?metric skos:definition ?definition.
        ?metric dqv:inDimension ?dimension.
      }}
      SERVICE <{dataset_endpoint}> {{
        ?measurement dqv:isMeasurementOf ?metric.
        ?measurement dqv:value ?value.
        ?measurement dqv:computedBy ?agent.
        ?distribution dcat:accessURL ?doi.
        ?distribution dqv:hasQualityMeasurement ?measurement.
        FILTER (?value < 1.0)
      }}
    }}
    ORDER BY ?doi ?agent ?dimension
    """
    # Add more queries as needed
}


def get_query(query_name: str, dataset_key: str) -> str:
    """
    Retrieve a SPARQL query by name, including common prefixes and formatted with endpoint URLs.

    :param query_name: The key corresponding to the desired query template.
    :param dataset_key: The key for the dataset endpoint in SPARQL_ENDPOINTS.
    :return: A complete SPARQL query string.
    """
    if query_name not in QUERY_TEMPLATES:
        raise ValueError(f"Query '{query_name}' not found.")
    if dataset_key not in SPARQL_ENDPOINTS:
        raise ValueError(f"Dataset endpoint '{dataset_key}' not found.")

    query_template = QUERY_TEMPLATES[query_name]
    return (
            COMMON_PREFIXES
            + query_template.format(
        metrics_endpoint=SPARQL_ENDPOINTS['metrics'],
        dataset_endpoint=SPARQL_ENDPOINTS[dataset_key]
    )
    )


def execute_query(query: str, endpoint_key: str):
    """
    Execute a SPARQL query against the specified endpoint and return results.

    :param query: The SPARQL query string to execute.
    :param endpoint_key: The key for the endpoint in SPARQL_ENDPOINTS.
    :return: Query results in JSON format.
    """
    if endpoint_key not in SPARQL_ENDPOINTS:
        raise ValueError(f"Endpoint '{endpoint_key}' not found.")

    sparql = SPARQLWrapper(SPARQL_ENDPOINTS[endpoint_key])
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def print_results_table(results):
    """
    Print SPARQL query results in a tabular format.

    :param results: The JSON results from a SPARQL query.
    """
    headers = results["head"]["vars"]
    rows = [
        [binding.get(var, {}).get("value", "") for var in headers]
        for binding in results["results"]["bindings"]
    ]
    print(tabulate(rows, headers=headers, tablefmt="grid"))


# Example usage
if __name__ == "__main__":
    query_name = "fetch_values_below_one"
    dataset_key = 'bonares'  # Specify the dataset endpoint key
    query = get_query(query_name, dataset_key)
    results = execute_query(query, endpoint_key='metrics')
    print_results_table(results)
