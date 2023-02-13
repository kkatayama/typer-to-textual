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


def call_button(command: str) -> List[str]:
    application = "esse3-student"

    if len(sys.argv) != 3:
        raise Exception("numero di parametri incorretto")

    result = subprocess.run(
        [application, command, "--help"],
        capture_output=True,
    )
    return result.stdout.decode().split('\n')


if __name__ == "__main__":
    result = output()
    Tui(result).run()
    """for index, line in enumerate(result, start=1):
        print(line)"""



    """error = risultato.stderr.decode().split('\n')
    for line in error:
        print(line)
    """