import os
import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD, DCTERMS, SKOS

# Load the CSV file with UTF-8 encoding
input_file = "input/2024-08-05_QUALITYINFO_PRE_17-19_Metrics.csv"
file_size = os.path.getsize(input_file)  # Get the file size in bytes
df = pd.read_csv(input_file, encoding='utf-8', skiprows=2, delimiter=';')

# Drop rows where 'year' or 'n' are missing or non-numeric
df = df.dropna(subset=['year', 'n'])

# Ensure 'year' and 'n' columns are integers
df['year'] = df['year'].astype(int)
df['n'] = df['n'].astype(int)

# Namespaces
DQV = Namespace("http://www.w3.org/ns/dqv#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
FAIR = Namespace("https://fairagro.net/DQV/")  # Changed from # to /
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
g = Graph()

# Bind namespaces
g.bind("dqv", DQV)
g.bind("dcat", DCAT)
g.bind("fair", FAIR)
g.bind("dcterms", DCTERMS)
g.bind("skos", SKOS)

# Define dataset and distribution
dataset_uri = FAIR["myDataset"]
distribution_uri = FAIR["myDatasetDistribution"]

g.add((dataset_uri, RDF.type, DCAT.Dataset))
g.add((dataset_uri, DCTERMS.title, Literal("My dataset", lang="en")))
g.add((dataset_uri, DCAT.distribution, distribution_uri))

g.add((distribution_uri, RDF.type, DCAT.Distribution))
g.add((distribution_uri, DCTERMS.title, Literal("2024-08-05_QUALITYINFO_PRE_17-19_Metrics", lang="en")))
g.add((distribution_uri, DCAT.downloadURL, URIRef("https://drive.google.com/drive/folders/1RPv3X_ek5mnwdEs2pi59-C9W9mIEdAyQ")))
g.add((distribution_uri, DCAT.mediaType, Literal("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")))
g.add((distribution_uri, DCAT.byteSize, Literal(file_size, datatype=XSD.integer)))

# Define dimensions
dimensions = {
    "accuracy": {
        "label": "Accuracy",
        "definition": "Measures how closely data values align with expected or true values."
    },
    "consistency": {
        "label": "Consistency",
        "definition": "Assesses how consistent the data is either internally or across different datasets."
    },
    "variability": {
        "label": "Variability",
        "definition": "Relates to the spread or variability within the dataset, indicating stability."
    },
    "statisticalSignificance": {
        "label": "Statistical Significance",
        "definition": "Assesses the significance of observed differences, indicating the reliability of statistical findings."
    },
    "statisticalConsistency": {
        "label": "Statistical Consistency",
        "definition": "Assesses the degree to which two datasets follow the same distribution."
    }
}

# Create the dimension resources in RDF
for dimension, details in dimensions.items():
    dimension_uri = FAIR[dimension]
    g.add((dimension_uri, RDF.type, DQV.Dimension))
    g.add((dimension_uri, SKOS.prefLabel, Literal(details["label"], lang="en")))
    g.add((dimension_uri, SKOS.definition, Literal(details["definition"], lang="en")))

# Define columns to be used as metrics with their metadata and corresponding dimensions
metrics = {
    'mean IACS': {
        'definition': "Mean value of IACS.",
        'expectedDataType': XSD.float,
        'dimension': FAIR.accuracy
    },
    'mean CTC': {
        'definition': "Mean value of CTC.",
        'expectedDataType': XSD.float,
        'dimension': FAIR.accuracy
    },
    'mean of differences': {
        'definition': "Mean of differences between IACS and CTC.",
        'expectedDataType': XSD.float,
        'dimension': FAIR.consistency
    },
    'p-value (t-test)': {
        'definition': "P-value of the t-test between IACS and CTC.",
        'expectedDataType': XSD.float,
        'dimension': FAIR.statisticalSignificance
    },
    'sd IACS': {
        'definition': "Standard deviation of IACS.",
        'expectedDataType': XSD.float,
        'dimension': FAIR.variability
    },
    'sd CTC': {
        'definition': "Standard deviation of CTC.",
        'expectedDataType': XSD.float,
        'dimension': FAIR.variability
    },
    'Rý': {
        'definition': "Correlation coefficient between IACS and CTC.",
        'expectedDataType': XSD.float,
        'dimension': FAIR.consistency
    },
    'RMSE': {
        'definition': "Root Mean Square Error between IACS and CTC.",
        'expectedDataType': XSD.float,
        'dimension': FAIR.accuracy
    },
    'p-value (ks)': {
        'definition': "P-value of the KS test between IACS and CTC.",
        'expectedDataType': XSD.float,
        'dimension': FAIR.statisticalSignificance
    },
    'D (ks)': {
        'definition': "D statistic of the KS test between IACS and CTC.",
        'expectedDataType': XSD.float,
        'dimension': FAIR.statisticalConsistency
    }
}

# Create a dqv:Metric for each column with its metadata and dimension
for metric, details in metrics.items():
    metric_uri = FAIR[metric.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")]
    g.add((metric_uri, RDF.type, DQV.Metric))
    g.add((metric_uri, SKOS.definition, Literal(details['definition'], lang="en")))
    g.add((metric_uri, DQV.expectedDataType, details['expectedDataType']))
    g.add((metric_uri, DQV.inDimension, details['dimension']))

# Add quality measurements for each row
for index, row in df.iterrows():
    # Create a unique base URI for the QualityMeasurement using the first four columns
    base_uri = f"measurement/{row['BL']}/{row['year']}/{row['CTC']}/{row['n']}"

    # Create a separate QualityMeasurement for each metric
    for metric in metrics.keys():
        measurement_uri = FAIR[
            f"{base_uri}/{metric.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')}"]
        metric_uri = FAIR[metric.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")]

        g.add((measurement_uri, RDF.type, DQV.QualityMeasurement))
        g.add((measurement_uri, DQV.computedOn, distribution_uri))
        g.add((measurement_uri, DQV.isMeasurementOf, metric_uri))
        g.add((measurement_uri, DQV.value, Literal(row[metric], datatype=XSD.float)))

# Output the graph in Turtle format
output_file = "output/2024-08-05_QUALITYINFO_PRE_17-19_Metrics.ttl"
g.serialize(destination=output_file, format="turtle")

print(f"RDF data has been written to {output_file}")
