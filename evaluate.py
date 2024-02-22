import re
import wilkinson_evaluation


def get_doi(line_str: str) -> str:
    # Regular expression pattern for matching DOIs
    pattern = r'\b(10\.\d{4,}(?:\.\d+)*\/\S+(?:(?![\"&\'<>])\S)*)\b'

    # Find the first match in the text
    match = re.search(pattern, line_str)

    # Return the matched DOI or None if no match is found
    return match.group(1) if match else None


def get_result_score():
    with open("wilkinson_result.html", "r", encoding="utf-8") as file:
        # Read the contents of the file
        html_content = file.read()

        # Find all occurrences of alt="5stars" with any number of stars (0-5)
        star_matches = re.findall(r'alt="(\d)stars"', html_content)
        print(f"star_matches: {star_matches}")

        # Convert the star ratings to integers and calculate the average
        total_stars = sum(int(stars) for stars in star_matches)
        average_score = total_stars / len(star_matches) if star_matches else 0

        # Return the average score as a string
        return "{:.3f}".format(round(average_score, 3))


def run():
    with (open("bonares_dois.csv", "r", encoding="utf-8") as file):
        with open("bonares_dois_result.csv", "w", encoding="utf-8") as result:

            for line in file:
                doi = get_doi(line)
                print(f"found doi: {doi}")
                if doi:
                    wilkinson_evaluation.evaluate(doi)
                    result_score = get_result_score()
                    print(f"result score: {result_score}")
                    newline = line.rstrip() + "," + result_score
                    result.write(newline + "\n")


if __name__ == "__main__":
    run()
