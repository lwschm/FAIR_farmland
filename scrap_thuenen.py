import os
import re
import requests
from bs4 import BeautifulSoup
import csv

# Ensure the output directory exists
output_dir = 'thuenen'
os.makedirs(output_dir, exist_ok=True)

# Function to fetch and parse a webpage
def fetch_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')

# Function to extract publications from a soup object
def extract_publications(soup):
    publications = []
    results = soup.find_all('div', class_='list-group-item search-result results-entry')
    for result in results:
        title_tag = result.find('h3', class_='results-topic')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Extract DOI from the text content of the result
            doi_tag = result.find('p', class_='result-content')
            if doi_tag:
                doi_match = re.search(r'DOI:\s*(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', doi_tag.get_text(), re.IGNORECASE)
                if doi_match:
                    doi = doi_match.group(1)
                    publications.append((title, doi))
    return publications

# Base URL to scrape
base_url = 'https://www.thuenen.de/de/literaturrecherche'

# Prepare the CSV file
output_file = os.path.join(output_dir, 'publications.csv')
doi_set = set()

with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Title', 'DOI'])

    # Loop through pages 1 to 1051
    for page_number in range(1, 1052):
        url = f"{base_url}?tx_solr[page]={page_number}"
        soup = fetch_page(url)
        publications = extract_publications(soup)
        for publication in publications:
            title, doi = publication
            if doi not in doi_set:
                writer.writerow(publication)
                doi_set.add(doi)
        print(f'Processed page {page_number}')

print(f'CSV file has been created in {output_dir}')
