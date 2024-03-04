import os
import re
import wilkinson_evaluation
import FUJI_evaluation

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
    with open(filepath_2, "r", encoding="utf-8") as file:
        filepath_result = filepath_2.replace(".csv", "_result.csv")
        with open(filepath_result, "w", encoding="utf-8") as result:
            headers = ("Dataset Name;Object Identifier;F1: FAIR Metrics Gen2- Unique Identifier;F1: FAIR Metrics Gen2 "
                       "- Identifier Persistence;F1: FAIR Metrics Gen2 - Data Identifier "
                       "Persistence;F2: FAIR Metrics Gen2 - Structured Metadata;F2: FAIR Metrics Gen2 - Grounded "
                       "Metadata;F3: FAIR Metrics Gen2 - Data Identifier Explicitly In "
                       "Metadata;F3: FAIR Metrics Gen2- Metadata Identifier Explicitly In Metadata;F4: FAIR Metrics "
                       "Gen2 - Searchable in major search engine;Average;;A;F;I;R;A1;F1;F2;F3;F4;I1;I2"
                       ";I3;R1;R1.1;R1.2;R1.3;FAIR")
            result.write(headers + "\n")
            for line in file:
                doi = get_doi(line)
                print(f"found doi: {doi}")
                if doi:
                    wilkinson_evaluation.evaluate(doi)
                    result_score_wilkinson = wilkinson_evaluation.get_result_score()
                    FUJI_evaluation.evaluate(doi)
                    result_score_fuji = FUJI_evaluation.get_result_score()
                    print(f"result scores: {result_score_wilkinson}, {result_score_fuji}")
                    print(f"result type fuji: {type(result_score_fuji)}")
                    fuji_values = [str(value) for value in result_score_fuji.values()]
                    newline = line.rstrip().replace(",", ";") + ";" + ";".join(result_score_wilkinson) + ";" + ";" + ";".join(fuji_values)
                    result.write(newline + "\n")


def run_on_list_of_dois_fuji(filepath_2: str = "bonares_dois.csv"):
    with (open(filepath_2, "r", encoding="utf-8") as file):
        filepath_result = filepath_2.replace(".csv", "_fuji_result.csv")
        with open(filepath_result, "w", encoding="utf-8") as result:
            for line in file:
                doi = get_doi(line)
                print(f"found doi: {doi}")
                if doi:
                    FUJI_evaluation.evaluate(doi)
                    result_score = FUJI_evaluation.get_result_score()
                    print(f"result score: {result_score}")
                    newline = line.rstrip() + ";" + ";".join(result_score)
                    result.write(newline + "\n")


if __name__ == "__main__":
    run_on_list_of_dois("bonares_dois.csv")
