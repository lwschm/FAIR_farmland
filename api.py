from fastapi import FastAPI, HTTPException, Form
from SPARQLWrapper import SPARQLWrapper, JSON

app = FastAPI()

FUSEKI_ENDPOINT = "http://fuseki:3030/FAIR_DQV/sparql"  # Ensure this matches your Fuseki dataset name


@app.get("/datasets")
async def get_datasets():
    try:
        sparql = SPARQLWrapper(FUSEKI_ENDPOINT)
        sparql.setQuery("""
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            PREFIX dcterms: <http://purl.org/dc/terms/>

            SELECT ?title ?doi
            WHERE {
              ?dataset a dcat:Dataset .
              ?dataset dcterms:title ?title .
              ?dataset dcat:distribution ?distribution .
              ?distribution dcat:accessURL ?doi .
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        datasets = []
        for result in results["results"]["bindings"]:
            title = result["title"]["value"]
            doi = result["doi"]["value"]
            datasets.append({"title": title, "doi": doi})

        return {"datasets": datasets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/metrics_by_doi")
async def handle_sparql(doi: str = Form("10.20387/bonares-tdgx-339v")):
    try:
        sparql = SPARQLWrapper(FUSEKI_ENDPOINT)
        sparql.setQuery(f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX dqv: <http://www.w3.org/ns/dqv#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            PREFIX fairagro: <https://fairagro.net/ontology#>

            SELECT ?metric ?score
            WHERE {{
              ?distribution a dcat:Distribution .
              ?distribution dcat:accessURL <https://doi.org/{doi}> .
              ?distribution dqv:hasQualityMeasurement ?measurement .
              ?measurement dqv:isMeasurementOf ?metric .
              ?measurement dqv:value ?score .
              ?metric rdf:type dqv:Metric .
            }}
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        metrics = []
        for result in results["results"]["bindings"]:
            metric = result["metric"]["value"]
            score = result["score"]["value"]
            metrics.append({"metric": metric, "score": score})

        return {"result": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/metadata_by_doi")
async def metadata_by_doi(doi: str = Form("10.5447/ipk/2017/2")):
    try:
        sparql = SPARQLWrapper(FUSEKI_ENDPOINT)
        sparql.setQuery(f"""
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX fairagro: <https://fairagro.net/ontology#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX dqv: <http://www.w3.org/ns/dqv#>

            SELECT ?title ?generatedAtTime ?accessURL
            WHERE {{
              ?dataset a dcat:Dataset .
              ?dataset dcterms:title ?title .
              ?dataset dcat:distribution ?distribution .
              ?distribution dcat:accessURL <https://doi.org/{doi}> .
              OPTIONAL {{
                ?qualityMetadata a dqv:QualityMetadata ;
                                 prov:generatedAtTime ?generatedAtTime .
              }}
              OPTIONAL {{
                ?distribution dcat:accessURL ?accessURL .
              }}
            }}
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if results["results"]["bindings"]:
            result = results["results"]["bindings"][0]
            metadata = {
                "title": result["title"]["value"],
                "generatedAtTime": result.get("generatedAtTime", {}).get("value", ""),
                "accessURL": result.get("accessURL", {}).get("value", "")
            }
            return {"metadata": metadata}
        else:
            raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/average_quality_measurements")
async def average_quality_measurements(doi: str = Form("10.5447/ipk/2017/2")):
    try:
        sparql = SPARQLWrapper(FUSEKI_ENDPOINT)
        sparql.setQuery(f"""
            PREFIX dqv: <http://www.w3.org/ns/dqv#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            PREFIX fair: <https://fairagro.net/ontology#>

            SELECT ?value ?dimension ?metric
            WHERE {{
              ?distribution a dcat:Distribution .
              ?distribution dcat:accessURL <https://doi.org/{doi}> .
              ?distribution dqv:hasQualityMeasurement ?measurement .
              ?measurement dqv:value ?value .
              ?measurement dqv:isMeasurementOf ?metric .
              ?metric dqv:inDimension ?dimension .
            }}
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if results["results"]["bindings"]:
            values = [float(result["value"]["value"]) for result in results["results"]["bindings"]]
            overall_average = sum(values) / len(values) if values else 0

            # Initialize data structures
            dimension_values = {'findability': [], 'accessibility': [], 'interoperability': [], 'reusability': []}
            dimension_value_counts = {'findability': {}, 'accessibility': {}, 'interoperability': {}, 'reusability': {}}
            fsf_values = []
            fes_values = []
            fsf_dimension_values = {'findability': [], 'accessibility': [], 'interoperability': [], 'reusability': []}
            fsf_dimension_value_counts = {'findability': {}, 'accessibility': {}, 'interoperability': {},
                                          'reusability': {}}
            fes_dimension_values = {'findability': [], 'accessibility': [], 'interoperability': [], 'reusability': []}
            fes_dimension_value_counts = {'findability': {}, 'accessibility': {}, 'interoperability': {},
                                          'reusability': {}}

            # Populate the data structures
            for result in results["results"]["bindings"]:
                value = float(result["value"]["value"])
                metric = result["metric"]["value"]
                dimension = result["dimension"]["value"].split('#')[-1]

                if dimension in dimension_values:
                    dimension_values[dimension].append(value)
                    if value in dimension_value_counts[dimension]:
                        dimension_value_counts[dimension][value] += 1
                    else:
                        dimension_value_counts[dimension][value] = 1

                if metric.startswith("https://fairagro.net/ontology#FsF"):
                    fsf_values.append(value)
                    if dimension in fsf_dimension_values:
                        fsf_dimension_values[dimension].append(value)
                        if value in fsf_dimension_value_counts[dimension]:
                            fsf_dimension_value_counts[dimension][value] += 1
                        else:
                            fsf_dimension_value_counts[dimension][value] = 1
                elif metric.startswith("https://fairagro.net/ontology#FES"):
                    fes_values.append(value)
                    if dimension in fes_dimension_values:
                        fes_dimension_values[dimension].append(value)
                        if value in fes_dimension_value_counts[dimension]:
                            fes_dimension_value_counts[dimension][value] += 1
                        else:
                            fes_dimension_value_counts[dimension][value] = 1

            # Calculate averages for each dimension
            dimension_averages = {dim: (sum(vals) / len(vals) if vals else 0) for dim, vals in dimension_values.items()}
            average_of_dimension_averages = sum(dimension_averages.values()) / len(
                dimension_averages) if dimension_averages else 0

            # Calculate averages for FsF and FES metrics
            fsf_average = sum(fsf_values) / len(fsf_values) if fsf_values else 0
            fes_average = sum(fes_values) / len(fes_values) if fes_values else 0

            fsf_dimension_averages = {dim: (sum(vals) / len(vals) if vals else 0) for dim, vals in
                                      fsf_dimension_values.items()}
            fes_dimension_averages = {dim: (sum(vals) / len(vals) if vals else 0) for dim, vals in
                                      fes_dimension_values.items()}

            fsf_average_of_dimension_averages = sum(fsf_dimension_averages.values()) / len(
                fsf_dimension_averages) if fsf_dimension_averages else 0
            fes_average_of_dimension_averages = sum(fes_dimension_averages.values()) / len(
                fes_dimension_averages) if fes_dimension_averages else 0

            return {
                "overall": {
                    "average_value": overall_average,
                    "average_of_dimension_averages": average_of_dimension_averages,
                    "measurement_count": len(values),
                    "dimension_averages": dimension_averages,
                    "value_breakdown": {
                        "overall": {v: values.count(v) for v in set(values)},
                        "by_dimension": dimension_value_counts
                    }
                },
                "fsf": {
                    "average_value": fsf_average,
                    "average_of_dimension_averages": fsf_average_of_dimension_averages,
                    "measurement_count": len(fsf_values),
                    "dimension_averages": fsf_dimension_averages,
                    "value_breakdown": {
                        "overall": {v: fsf_values.count(v) for v in set(fsf_values)},
                        "by_dimension": fsf_dimension_value_counts
                    }
                },
                "fes": {
                    "average_value": fes_average,
                    "average_of_dimension_averages": fes_average_of_dimension_averages,
                    "measurement_count": len(fes_values),
                    "dimension_averages": fes_dimension_averages,
                    "value_breakdown": {
                        "overall": {v: fes_values.count(v) for v in set(fes_values)},
                        "by_dimension": fes_dimension_value_counts
                    }
                }
            }
        else:
            raise HTTPException(status_code=404, detail="No quality measurements found for the given DOI")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

