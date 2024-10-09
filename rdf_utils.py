from rdflib import Graph, URIRef
from collections import defaultdict
from rdf_cache import FAIRAGRO, metrics_graph
import requests


def validate_doi(doi: str) -> bool:
    """
    Validate the DOI using the doi.org proxy server.

    Args:
        doi (str): The DOI to validate.

    Returns:
        bool: True if the DOI resolves successfully, False otherwise.
    """
    # Construct the DOI URL using the proxy server
    doi_url = f"https://doi.org/{doi}"
    try:
        # Send a HEAD request to check if the DOI resolves
        response = requests.head(doi_url, allow_redirects=True, timeout=10)

        # A status code in the 200 range indicates a valid DOI that resolves
        if response.status_code == 200:
            return True
        else:
            print(f"DOI {doi} did not resolve successfully. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while validating DOI {doi}: {e}")
        return False


def extract_scores_from_rdf(graph: Graph) -> dict:
    # Initialize scores dictionaries for FES and FUJI
    fes_scores = defaultdict(list)
    fuji_scores = defaultdict(list)

    print("Starting extraction of scores from RDF...")

    # Helper function to determine the dimension of a metric
    def get_dimension(metric_uri: URIRef) -> str:
        query = """
        SELECT ?dimension
        WHERE {
            ?metric dqv:inDimension ?dimension .
        }
        """
        result = metrics_graph.query(query, initBindings={'metric': metric_uri})
        for row in result:
            if "findability" in row.dimension:
                return "findability_score"
            elif "accessibility" in row.dimension:
                return "accessibility_score"
            elif "interoperability" in row.dimension:
                return "interoperability_score"
            elif "reusability" in row.dimension:
                return "reusability_score"
        return None

    # SPARQL-like query to extract the metrics, values, and the service they are associated with
    for measurement, metric, value, computed_by in graph.query(
        """
        SELECT ?measurement ?metric ?value ?computedBy
        WHERE {
            ?measurement a dqv:QualityMeasurement ;
                         dqv:isMeasurementOf ?metric ;
                         dqv:value ?value ;
                         dqv:computedBy ?computedBy .
        }
        """
    ):
        # Get the score value as a float
        score_value = float(value.toPython())

        # Get the dimension of the metric
        dimension = get_dimension(metric)
        if dimension:
            # Determine if it's an FES or FUJI measurement based on the computedBy value
            if computed_by == FAIRAGRO["FAIREvaluationServices"]:
                fes_scores[dimension].append(score_value)
            elif computed_by == FAIRAGRO["FUJIAutomatedFAIRDataAssessmentTool"]:
                fuji_scores[dimension].append(score_value)

    # Calculate the average score for each category for FES and FUJI and round to 2 decimal places
    fes_averages = {k: sum(v) / len(v) if v else 0.0 for k, v in fes_scores.items()}
    fuji_averages = {k: sum(v) / len(v) if v else 0.0 for k, v in fuji_scores.items()}

    print(f"Calculated FES averages: {fes_averages}")
    print(f"Calculated FUJI averages: {fuji_averages}")

    return {
        "fes": fes_averages,
        "fuji": fuji_averages,
    }
