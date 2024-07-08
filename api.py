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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
