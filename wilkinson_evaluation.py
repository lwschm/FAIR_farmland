import re
import requests

# This is the Wilkinson FAIR Evaluation Service
url = 'https://fairdata.services:7171/FAIR_Evaluator/collections/6/evaluate'
headers = {
    'accept': '*/*',
    'Content-Type': 'application/json'
}
data_example = {
    "executor": "Exec",
    "resource": "10.20387/bonares-gx1f-bh69",
    # "resource": "https://atlas.thuenen.de/api/v2/resources?page_size=200&format=json",
    "title": "Test_Eval"
}


def get_result_score(name_of_wilkinson_result_html: str = "wilkinson_result.html") -> list:
    with open(name_of_wilkinson_result_html, "r", encoding="utf-8") as file:
        # Read the contents of the file
        html_content = file.read()

        # Find all occurrences of alt="5stars" with any number of stars (0-5)
        score_matches = re.findall(r'Score: (\d+)', html_content)
        # print(f"score_matches: {score_matches}")

        # Convert the star ratings to integers and calculate the average
        total_score = sum(int(stars) for stars in score_matches)
        average_score = total_score / len(score_matches) if score_matches else 0
        score_matches.append("{:.3f}".format(round(average_score, 3)))
        print(f"Returning score matches: {score_matches}")
        return score_matches


def evaluate(data_doi=None):
    data = data_example
    if data_doi:
        data["resource"] = data_doi
    print(f"running wilkinson evaluation for {data}")
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print("Request successful!")

        # Save the response content to a local file
        with open('wilkinson_result.html', 'w', encoding="utf-8") as file:
            file.write(response.content.decode('utf-8'))
            print("Result saved to 'wilkinson_result.html'")
    else:
        print(f"Request failed with status code {response.status_code}")


if __name__ == "__main__":
    evaluate()
    get_result_score()
    pass
