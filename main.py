import sys
import subprocess
from typing import List

from tui import Tui


def output() -> List[str]:
    comando = "esse3-student"

    if len(sys.argv) < 2:
        raise Exception("Non sono stati passati argomenti.")

    argomento = sys.argv[1]

    if len(sys.argv) == 2 and argomento != "--help":
        raise Exception("L'unico argomento passato non è '--help'.")

    risultato = subprocess.run(
        [comando, argomento, "--help"],
        capture_output=True,
    )
    return risultato.stdout.decode().split('\n')


def call_button(command: str, debug: bool) -> List[str]:
    application = "esse3-student"

    """if len(sys.argv) != 3:
        raise Exception("numero di parametri incorretto")"""

    if debug:
        result = subprocess.run(
            [application, "--debug", command, "--help"],
            capture_output=True,
        )
    else:
        result = subprocess.run(
            [application, command, "--help"],
            capture_output=True,
        )

    return result.stdout.decode().split('\n')


if __name__ == "__main__":
    result = output()
    Tui(result).run()
    """application = "esse3-student"

    result = subprocess.run(
        [application, "--help"],
        capture_output=True,
    )
    output = result.stdout.decode().split('\n')
    start = False
    for index, line in enumerate(output, start=1):
        if "Commands" in line:
            start = True
            continue
        if start and any(word.isalpha() for word in line.split()):
            command = line.split(" ")
            command = list(filter(bool, command))
            command_name = command[1]
            command_description = " ".join(command[2:-1])
            print(command_name + " " + command_description)
"""


    """error = risultato.stderr.decode().split('\n')
    for line in error:
        print(line)
    """