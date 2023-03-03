import sys
import subprocess

from typing import List, Tuple

from rich.console import Console

from tui import Tui


def main_output():

    result = subprocess.run(
        ["esse3-student", "booklet", "--help"],
        capture_output=True,
    )

    output = result.stdout.decode().split('\n')
    start = False
    options = {}
    for index, line in enumerate(output, start=1):
        if "Options" in line:
            start = True
            continue
        if start:
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

            if words:

                if ',' in words[0]:
                    words[0] = words[0].split(",")[0]
                words[0] = words[0].replace('--', '')

                if words[0] == "help":
                    continue

                if len(words) > 1:
                    if words[1].startswith("-"):
                        words.remove(words[1])

                if len(words) == 1:
                    words.append("BOOLEAN")

                if len(words) == 2:
                    types = ["INTEGER", "FLOAT", "TEXT", "[", "<", "UUID", "PATH", "FILENAME", "BOOLEAN"]
                    if not any(words[1].replace('[', '(').replace('<', '(').startswith(t) for t in types):
                        words.insert(1, "BOOLEAN")

                if len(words) == 2:
                    words.append("No description")

                for i in range(2, len(words)):
                    words[i] = words[i].replace('[', '(').replace(']', ')')

                options[words[0]] = words[1:]

    for k, v in options.items():
        print(f"{k}:  {', '.join(str(x) for x in v)}")


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


def booklet_options(output):
    start = False
    options = {}
    for index, line in enumerate(output, start=1):
        if "Options" in line:
            start = True
            continue
        if start:
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

            if words:

                if ',' in words[0]:
                    words[0] = words[0].split(",")[0]
                words[0] = words[0].replace('--', '')

                if words[0] == "help":
                    continue

                if len(words) > 1:
                    if words[1].startswith("-"):
                        words.remove(words[1])

                if len(words) == 1:
                    words.append("BOOLEAN")

                if len(words) == 2:
                    types = ["INTEGER", "FLOAT", "TEXT", "[", "<", "UUID", "PATH", "FILENAME", "BOOLEAN"]
                    if not any(words[1].replace('[', '(').replace('<', '(').startswith(t) for t in types):
                        words.insert(1, "BOOLEAN")

                if len(words) == 2:
                    words.append("No description")

                words[2] = words[2].replace('[', '(').replace(']', ')')

                options[words[0]] = words[1:]

    for k, v in options.items():
        print(f"{k}: {v[0]}, {v[1]}")


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

    result = subprocess.run(
        ["esse3-student", "--help"],
        capture_output=True,
    )

    output = result.stdout.decode().split('\n')

    start_commands = False
    buttons = []
    for index, line in enumerate(output, start=1):

        if "Commands" in line:
            start_commands = True
            continue

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
            buttons.append(words[1])

    print(buttons)


