import requests


def get_datacite_doi_info(doi: str) -> dict:
    url = f"https://api.datacite.org/dois/{doi}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()['data']['attributes']
        return {
            "title": data.get("titles", [{"title": "N/A"}])[0]["title"],
            "authors": ", ".join([creator.get("name", "N/A") for creator in data.get("creators", [])]) or "N/A",
            "published_date": data.get("publicationYear", "N/A"),
            "publisher": data.get("publisher", "N/A"),
            "doi": data.get("doi", "N/A"),
            "resource_type": data.get("types", {}).get("resourceTypeGeneral", "N/A"),
            "description": data.get("descriptions", [{"description": "N/A"}])[0]["description"],
            "subjects": ", ".join([subject.get("subject", "N/A") for subject in data.get("subjects", [])]) or "N/A",
            "language": data.get("language", "N/A"),
            "funding_references": ", ".join([funding.get("funderName", "N/A") for funding in data.get("fundingReferences", [])]) or "N/A"
        }
    else:
        print(f"No information found for DOI: {doi}. Returning default 'N/A' values.")
        return {
            "title": "N/A",
            "authors": "N/A",
            "published_date": "N/A",
            "publisher": "N/A",
            "doi": doi,  # Return the input DOI, so it is not completely lost
            "resource_type": "N/A",
            "description": "N/A",
            "subjects": "N/A",
            "language": "N/A",
            "funding_references": "N/A"
        }


def print_doi_info(doi_info):
    if doi_info:
        print("DOI Information:")
        print(f"  Title: {doi_info.get('title', 'No title found')}")
        print(f"  Authors: {doi_info.get('authors', 'No authors found')}")
        print(f"  Published Date: {doi_info.get('published_date', 'No publication year found')}")
        print(f"  Publisher: {doi_info.get('publisher', 'No publisher found')}")
        print(f"  DOI: {doi_info.get('doi', 'No DOI found')}")
        print(f"  Resource Type: {doi_info.get('resource_type', 'No resource type found')}")
        print(f"  Description: {doi_info.get('description', 'No description found')}")
        print(f"  Subjects: {doi_info.get('subjects', 'No subjects found')}")
        print(f"  Language: {doi_info.get('language', 'No language found')}")
        print(f"  Funding References: {doi_info.get('funding_references', 'No funding references found')}")
    else:
        print("No information found.")


if __name__ == "__main__":
    # Example usage for testing purposes
    doi = "10.20387/bonares-tdgx-339v"
    info = get_datacite_doi_info(doi)
    print_doi_info(info)
