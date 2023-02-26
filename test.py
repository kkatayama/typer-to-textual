import sys
import subprocess

from typing import List, Tuple

from rich.console import Console

from tui import Tui


def main_output() -> List[str]:


    result = subprocess.run(
        ["esse3-student", "booklet", "--help"],
        capture_output=True,
    )
    return result.stdout.decode().split('\n')


def process_commands():
    output, app = main_output()
    start_commands = False
    commands = []
    for index, line in enumerate(output, start=1):
        print(line)
        """if "Commands" in line:
            start_commands = True

        if start_commands and any(word.isalpha() for word in line.split()):
            command = line.split(" ")
            words = []
            current_word = ""
            for item in command:
                if item and item != '│':
                    current_word += " " + item
                else:
                    words.append(current_word.strip())
                    current_word = ""

            words = list(filter(bool, words))
            commands.append(words)

    for command in commands:
        print(commands[0])"""


def process_data():
    output, app = main_output()
    start_options = False
    data = {}
    for index, line in enumerate(output, start=1):

        if "Options" in line:
            start_options = True
            continue

        if "Commands" in line:
            start_options = False

        if start_options and any(word.isalpha() for word in line.split()):
            items = line.split(" ")
            words = []
            current_word = ""
            for option in items:
                if option and option != '│' and option != '*':
                    current_word += " " + option
                else:
                    words.append(current_word.strip())
                    current_word = ""

            words = list(filter(bool, words))
            if len(words) == 2:
                words.insert(1, "BOOLEAN")
            if words:
                words[0] = words[0].replace('--', '')
                if words[0] == "help":
                    continue
                data[words[0]] = [words[1], words[2]]

    for k, v in data.items():
        print(f"{v[1]}")


def process_arguments():
    output, app = main_output()
    start_arguments = False
    data = {}
    for index, line in enumerate(output, start=1):

        if "Arguments" in line:
            start_arguments = True
            continue

        if "Options" in line:
            start_arguments = False

        if start_arguments and any(word.isalpha() for word in line.split()):
            items = line.split(" ")
            words = []
            current_word = ""
            for option in items:
                if option and option != '│' and option != '*':
                    current_word += " " + option
                else:
                    words.append(current_word.strip())
                    current_word = ""

            words = list(filter(bool, words))
            if len(words) == 2:
                words.insert(1, " ")
            if words:
                words[2] = words[2].replace('[', '(')
                words[2] = words[2].replace(']', ')')
                if words[0] == "help":
                    continue
            data[words[0]] = [words[1], words[2]]

    for k, v in data.items():
        print(v[1])

def options(output):
    start = False
    options = []
    for index, line in enumerate(output, start=1):
        if "Options" in line:
            start = True
            continue
        if start and any(word.isalpha() for word in line.split()):
            command = line.split(" ")
            words = []
            current_word = ""
            for item in command:
                if item and item != '│':
                    current_word += " " + item
                else:
                    words.append(current_word.strip())
                    current_word = ""

            words = list(filter(bool, words))
            if len(words) == 2:
                words.insert(1, "BOOLEAN")
            if words:
                words[0] = words[0].replace('--', '').replace("-", " ")
                words[2] = words[2].replace('[', '(')
                words[2] = words[2].replace(']', ')')
                if words[0] == "help":
                    continue
            options.append(words)

    return options


if __name__ == "__main__":
    """average_to_achieve = sys.argv[1]
    weighted_average = sys.argv[2]
    weighted_average.replace(",", ".")
    remaining_cfu = sys.argv[3]
    first = (float(average_to_achieve) * 120)
    second = (float(weighted_average) * float(96))
    grade_to_obtain = (first - second) \
                      / float(remaining_cfu)
    print(first)
    print(second)
    print(grade_to_obtain)"""

    output = main_output()
    options = options(output)

    for o in options:
        print(o)

