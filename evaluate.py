import os
import re
import wilkinson_evaluation
import FUJI_evaluation
from requests.exceptions import ConnectTimeout
import tkinter as tk
from tkinter import filedialog

cwd = os.getcwd()

file_path = os.path.join(cwd, r"metafiles\\metafiles_list.txt")


def get_identifier(line_str: str) -> str:
    # Regular expression pattern for matching DOIs
    pattern = r'\b(10\.\d{4,}(?:\.\d+)*\/\S+(?:(?![\"&\'<>])\S)*)\b'

    # Find the first match in the text
    match = re.search(pattern, line_str)
    if not match:
        # Define a regular expression pattern to match the URL
        pattern = r'(https?://\S+)'
        # Use re.search to find the first match of the pattern in the line
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


def run_on_list_of_pids():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    filepath_2 = filedialog.askopenfilename(title="Select a CSV file", initialdir=os.path.join(cwd, "input"))

    with (open(filepath_2, "r", encoding="utf-8") as file):
        filepath_result = filepath_2.replace(".csv", "_result.csv")
        filepath_result = filepath_result.replace("input", "output")
        with open(filepath_result, "w", encoding="utf-8") as result:
            headers = ("Dataset Name;Object Identifier;F1: FAIR Metrics Gen2- Unique Identifier;F1: FAIR Metrics Gen2 "
                       "- Identifier Persistence;F1: FAIR Metrics Gen2 - Data Identifier "
                       "Persistence;F2: FAIR Metrics Gen2 - Structured Metadata;F2: FAIR Metrics Gen2 - Grounded "
                       "Metadata;F3: FAIR Metrics Gen2 - Data Identifier Explicitly In "
                       "Metadata;F3: FAIR Metrics Gen2- Metadata Identifier Explicitly In Metadata;F4: FAIR Metrics "
                       "Gen2 - Searchable in major search engine;A1.1: FAIR Metrics Gen2 - Uses open free protocol "
                       "for data retrieval;A1.1: FAIR Metrics Gen2 - Uses open free protocol for metadata "
                       "retrieval;A1.2: FAIR Metrics Gen2 - Data authentication and authorization;A1.2: FAIR Metrics "
                       "Gen2 - Metadata authentication and authorization;A2: FAIR Metrics Gen2 - Metadata "
                       "Persistence;I1: FAIR Metrics Gen2 - Metadata Knowledge Representation Language (weak);I1: "
                       "FAIR Metrics Gen2 - Metadata Knowledge Representation Language (strong);I2: FAIR Metrics Gen2 "
                       "- Metadata uses FAIR vocabularies (weak);I2: FAIR Metrics Gen2 - Metadata uses FAIR "
                       "vocabularies (strong);I3: FAIR Metrics Gen2 - Metadata contains qualified outward "
                       "references);R1.1: FAIR Metrics Gen2 - Metadata Includes License (strong);R1.1: FAIR Metrics "
                       "Gen2 - Metadata Includes License (weak);Average;;A;F;I;R;A1;F1;F2;F3;F4;I1;I2"
                       ";I3;R1;R1.1;R1.2;R1.3;FAIR")
            result.write(headers + "\n")
            for line in file:
                identifier = get_identifier(line)
                print(f"found identifier: {identifier}")

                if identifier:
                    wilkinson_evaluation.evaluate(identifier)
                    result_score_wilkinson = wilkinson_evaluation.get_result_score()
                    #try:
                    FUJI_evaluation.evaluate(identifier)
                    result_score_fuji = FUJI_evaluation.get_result_score()
                    fuji_values = [str(value) for value in result_score_fuji.values()]
                    fuji_success = True
                    # except ConnectTimeout:
                    #     fuji_success = False
                    #     print("Connection timed out while evaluating.")
                    #     # Handle the timeout error gracefully
                    # else:
                    #     print("Evaluation completed successfully.")
                    print(f"result scores: {result_score_wilkinson}, {result_score_fuji}")

                    if fuji_success:
                        newline = line.rstrip().replace(",", ";") + ";" + ";".join(
                            result_score_wilkinson) + ";" + ";" + ";".join(fuji_values)
                    else:
                        newline = line.rstrip().replace(",", ";") + ";" + ";".join(
                            result_score_wilkinson)
                    result.write(newline + "\n")


def run_on_list_of_dois_fuji(filepath_2: str = "input\\bonares_dois.csv"):
    with (open(filepath_2, "r", encoding="utf-8") as file):
        filepath_result = filepath_2.replace(".csv", "_fuji_result.csv")
        filepath_result = filepath_result.replace("input", "output")
        with open(filepath_result, "w", encoding="utf-8") as result:
            for line in file:
                doi = get_identifier(line)
                print(f"found identifier: {doi}")
                if doi:
                    FUJI_evaluation.evaluate(doi)
                    result_score = FUJI_evaluation.get_result_score()
                    print(f"result score: {result_score}")
                    newline = line.rstrip() + ";" + ";".join(result_score)
                    result.write(newline + "\n")


if __name__ == "__main__":
    run_on_list_of_pids()
