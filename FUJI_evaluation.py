import os
import json
from dotenv import load_dotenv
import requests
import csv

# Load dotenv
load_dotenv()

USERNAME = os.getenv("fuji_username")
PASSWORD = os.getenv("fuji_password")
fuji_auth = (USERNAME, PASSWORD)
print(fuji_auth)

# This is the Wilkinson FAIR Evaluation Service
url = 'http://192.168.220.71:1071/fuji/api/v1/evaluate'
headers = {
    'accept': '*/*',
    'Content-Type': 'application/json'
}
data_example = {
  "object_identifier": "DOI: 10.20387/bonares-zyd4-w9c2",
  "test_debug": True,
  "metadata_service_endpoint": "",
  "metadata_service_type": "oai_pmh",
  "use_datacite": True,
  "metric_version": "metrics_v0.5"
}


def get_result_score(name_of_fuji_result_json: str = "fuji_result.json"):
    with open(name_of_fuji_result_json, "r", encoding="utf-8") as file:
        # Read the contents of the file
        json_content = file.read()
        json_data = json.loads(json_content)
        score_percent = json_data["summary"]["score_percent"]
        object_identifier = json_data["request"]["object_identifier"]
        # write_result_to_csv(object_identifier, score_percent)
        return score_percent


def write_result_to_csv(object_identifier, score_percent):
    with open("fuji_result.csv", "w", newline='', encoding="utf-8") as csv_file:
        # Create CSV writer with custom delimiter
        writer = csv.writer(csv_file, delimiter=';')
        # Write header row
        writer.writerow(["Object Identifier"] + list(score_percent.keys()))
        # Format score percentages as strings with two decimal places
        formatted_scores = [f'{score:.2f}' for score in score_percent.values()]
        # Write data row
        writer.writerow([object_identifier] + formatted_scores)


def evaluate(data_doi=None):
    data = data_example
    if data_doi:
        data["resource"] = data_doi
    print(f"running evaluation for {data}")
    response = requests.post(url, json=data, headers=headers, auth=fuji_auth)

    if response.status_code == 200:
        print("Request successful!")
        parsed_response = json.loads(response.text)
        # Save the response content to a local file
        with open('fuji_result.json', 'w+', encoding="utf-8") as file:
            file.write(json.dumps(parsed_response, indent=4))
            print("Result saved to 'fuji_result.json'")
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    evaluate()
    get_result_score()
    pass
