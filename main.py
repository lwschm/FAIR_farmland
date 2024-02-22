import os

cwd = os.getcwd()

file_path = os.path.join(cwd, r"metafiles\\metafiles_list.txt")


# Open the file in read mode
def read():
    lines = []
    with open(file_path, 'r') as file:
        # Read and print each line
        for line in file:
            lines.append(line)
        return lines


def evaluate(resource: str):
    return


if __name__ == "__main__":
    lines_list = read()
    print(lines_list[0])
