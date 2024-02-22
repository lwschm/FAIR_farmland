import requests

# This is the Wilkinson FAIR Evaluation Service
url = 'https://fairdata.services:7171/FAIR_Evaluator/collections/1/evaluate'
headers = {
    'accept': '*/*',
    'Content-Type': 'application/json'
}
data_example = {
    "executor": "Exec",
    "resource": "10.20387/bonares-gx1f-bh69",
    "title": "Test_Eval"
}


def evaluate(data_doi=None):
    data = data_example
    if data_doi:
        data["resource"] = data_doi
    print(f"running evaluation for {data}")
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print("Request successful!")
        # print("Response content:")
        # print(response.content.decode('utf-8'))

        # Save the response content to a local file
        with open('wilkinson_result.html', 'w', encoding="utf-8") as file:
            file.write(response.content.decode('utf-8'))
            print("Result saved to 'wilkinson_result.html'")
    else:
        print(f"Request failed with status code {response.status_code}")


if __name__ == "__main__":
    pass
    # evaluate()
