import os
import re
import wilkinson_evaluation

cwd = os.getcwd()

file_path = os.path.join(cwd, r"metafiles\\metafiles_list.txt")


def get_doi(line_str: str) -> str:
    # Regular expression pattern for matching DOIs
    pattern = r'\b(10\.\d{4,}(?:\.\d+)*\/\S+(?:(?![\"&\'<>])\S)*)\b'

    # Find the first match in the text
    match = re.search(pattern, line_str)

    # Return the matched DOI or None if no match is found
    return match.group(1) if match else None


# Open the file in read mode
def read_file_to_list(file_filepath: str = file_path) -> list:
    lines = []
    with open(file_filepath, 'r') as file:
        # Read each line
        for line in file:
            lines.append(line)
        return lines


def run_on_list_of_dois(filepath_2: str = "bonares_dois.csv"):
    with (open(filepath_2, "r", encoding="utf-8") as file):
        filepath_result = filepath_2.replace(".csv", "_result.csv")
        with open(filepath_result, "w", encoding="utf-8") as result:
            for line in file:
                doi = get_doi(line)
                print(f"found doi: {doi}")
                if doi:
                    wilkinson_evaluation.evaluate(doi)
                    result_score = wilkinson_evaluation.get_result_score()
                    print(f"result score: {result_score}")
                    newline = line.rstrip() + "," + ",".join(result_score)
                    result.write(newline + "\n")


if __name__ == "__main__":
    run_on_list_of_dois()
