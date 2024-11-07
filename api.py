from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from SPARQLWrapper import SPARQLWrapper, JSON

from landing_page import get_landing_page
from doi_to_dqv import create_dqv_representation, fes_evaluate_to_list, fuji_evaluate_to_list
from rdf_utils import extract_scores_from_rdf, validate_doi

from datetime import datetime
from io import BytesIO
from urllib.parse import quote
import tempfile

FUSEKI_ENDPOINT = "http://fuseki:3030/FAIR_DQV/sparql"  # Ensure this matches your Fuseki dataset name

# Temporary in-memory cache for RDF graphs
rdf_cache = {}

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


@app.get("/", response_class=HTMLResponse)
async def landing_page():
    return get_landing_page()


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


@app.post("/fes_evaluation")
async def run_fes_evaluation(doi: str = Form("10.5447/ipk/2017/2")):
    try:
        # Call the fes_evaluate_to_list function with the provided DOI
        evaluation_result = fes_evaluate_to_list(doi)

        if evaluation_result:
            return {"doi": doi, "evaluation_scores": evaluation_result}
        else:
            raise HTTPException(status_code=500, detail="FES evaluation failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fuji_evaluation")
async def run_fuji_evaluation(doi: str = Form("10.20387/bonares-q82e-t008-test")):
    try:
        # Call the fuji_evaluate_to_list function with the provided DOI
        evaluation_result = fuji_evaluate_to_list(doi)

        if evaluation_result:
            return {"doi": doi, "evaluation_scores": evaluation_result}
        else:
            raise HTTPException(status_code=500, detail="FUJI evaluation failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_dqv_file/")
async def generate_dqv_file(
    doi: str = Form(...), fes: str = Form("true"), fuji: str = Form("true"), output_format: str = Form("ttl")
):
    try:
        # Validate the DOI before proceeding
        if not validate_doi(doi):
            raise HTTPException(status_code=404, detail=f"No information found for DOI: {doi}")

        # Convert the string values to booleans
        fes = fes.lower() == "true"
        fuji = fuji.lower() == "true"

        # Start time for evaluation
        start_time = datetime.now()

        # Placeholder for evaluation results
        fes_evaluation_result = None
        fuji_evaluation_result = None

        # Perform FES evaluation if fes is True
        if fes:
            try:
                fes_evaluation_result = fes_evaluate_to_list(doi)
                if not fes_evaluation_result:
                    raise HTTPException(status_code=500, detail="Failed to get FES evaluation results")
            except Exception as fes_error:
                print(f"FES evaluation failed: {fes_error}")
                raise HTTPException(status_code=500, detail="FES evaluation failed")

        # Perform FUJI evaluation if fuji is True
        if fuji:
            try:
                fuji_evaluation_result = fuji_evaluate_to_list(doi)
                if not fuji_evaluation_result:
                    fuji_evaluation_result = {}  # If FUJI fails, use an empty dict
            except Exception as fuji_error:
                print(f"FUJI evaluation failed or timed out: {fuji_error}")
                fuji_evaluation_result = {}  # Proceed without FUJI if it fails

        # End time for evaluation
        end_time = datetime.now()

        # Create the DQV representation graph
        graph = create_dqv_representation(
            doi,
            fes_evaluation_result or [],
            fuji_evaluation_result or {},
            start_time,
            end_time
        )

        if not graph:
            raise HTTPException(status_code=500, detail="Failed to generate DQV representation graph")

        # Store the graph in memory cache
        rdf_cache[doi] = graph

        # Generate output files in memory using a BytesIO buffer
        buffer = BytesIO()
        try:
            serialize_graph(graph, buffer, output_format)
        except HTTPException as e:
            print(e.detail)
            raise HTTPException(status_code=e.status_code, detail=e.detail)

        # Set buffer position to the beginning
        buffer.seek(0)

        sanitized_doi = doi.replace('/', '_')
        filename = f"output_{sanitized_doi}.{output_format}"
        encoded_filename = quote(filename)

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}',
            "X-Content-Type-Options": "nosniff"
        }
        print(f"headers: {headers}")
        return StreamingResponse(
            buffer,
            media_type="application/octet-stream",
            headers=headers
        )

    except HTTPException as http_exc:
        raise http_exc  # Let the existing HTTPException be handled as is
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_dqv_summary/")
async def generate_dqv_summary(doi: str = Form(...)):
    try:
        print(f"Received request to generate DQV summary for DOI: {doi}")

        # Retrieve the RDF graph from cache.
        graph = rdf_cache.get(doi)
        if not graph:
            raise ValueError(
                "The RDF graph for the given DOI could not be found. Please ensure the DOI is correct and try generating the DQV file first.")

        # Extract scores from the graph.
        summary_data = extract_scores_from_rdf(graph)

        # Prepare and return the summary data.
        summary_data["doi"] = doi
        return JSONResponse(content=summary_data)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


def serialize_graph(graph, buffer, output_format: str):
    print(f"serialize_graph output_format: {output_format}")
    if output_format in ("ttl", "turtle"):
        graph.serialize(destination=buffer, format='turtle')
    elif output_format in ("jsonld", "json-ld"):
        graph.serialize(destination=buffer, format='json-ld')
    elif output_format == "xml":
        graph.serialize(destination=buffer, format='pretty-xml')
    elif output_format in ("ntriples", "nt", "nt11"):
        graph.serialize(destination=buffer, format='nt')
    elif output_format == "n3":
        graph.serialize(destination=buffer, format='n3')
    elif output_format == "trig":
        graph.serialize(destination=buffer, format='trig')
    else:
        raise HTTPException(status_code=400, detail="Invalid output format")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

