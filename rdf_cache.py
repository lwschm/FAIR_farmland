from rdflib import Graph, Namespace

# Define namespaces
FAIRAGRO = Namespace("https://fairagro.net/ontology#")
DQV = Namespace("http://www.w3.org/ns/dqv#")

# Path to the metrics TTL file
METRICS_TTL_PATH = "DataQualityVocabulary/FAIR_data_quality_metrics.ttl"

# Load the static metrics graph only once
metrics_graph = Graph()
metrics_graph.parse(METRICS_TTL_PATH, format="ttl")

# Export only what needs to be used in other modules
__all__ = ["FAIRAGRO", "DQV", "metrics_graph"]
