from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Button, Footer, Input, Checkbox
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual import events
from textual.pilot import Pilot

import typer

import sys
import subprocess
from typing import List


class Header(Static):
    pass


class HomePage(Screen):

    def __init__(self, output) -> None:
        self.output = output
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("Homepage", classes="header")
        yield Container(
            Static(f"Esse3 command line utility", classes="title"),
            Vertical(
                Static("Option preferences", id="login"),
                Input(placeholder="username....     [default: None or env var]", classes="credentials"),
                Input(placeholder="password....     [default: None or env var]", password=True, classes="credentials"),
                Horizontal(
                    Static("enable to show browser backend operations:"),
                    Checkbox(),
                    id="debug"
                ),
                Static("Commands", id="commands"),
            ),
            id="homepage"
        )
        yield Footer()

    def on_mount(self) -> None:
        start = False
        for index, line in enumerate(self.output, start=1):
            if "Commands" in line:
                start = True
                continue
            if start and any(word.isalpha() for word in line.split()):
                command = line.split(" ")
                command = list(filter(bool, command))
                command_name = command[1]
                command_description = " ".join(command[2:-1])
                self.query_one(Vertical).mount(Horizontal(
                    Button(command_name, id=command_name),
                    Static(command_description),
                    classes="commands-horizontal"
                    )
                )


class Booklet(Screen):

    def __init__(self, output) -> None:
        self.output = output
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("Homepage", classes="header")
        yield Vertical()

    def on_mount(self) -> None:
        start = False
        for index, line in enumerate(self.output, start=1):
            if "Options" in line:
                start = True
                continue
            if start and any(word.isalpha() for word in line.split()):
                command = line.split(" ")
                command = list(filter(bool, command))
                command_name = command[1]
                command_description = " ".join(command[2:-1])
                self.query_one(Vertical).mount(Horizontal(
                    Button(command_name, id=command_name),
                    Static(command_description),
                    classes="commands-horizontal"
                    )
                )


class Tui(App):

    def __init__(self, output) -> None:
        self.output = output
        super().__init__()

    CSS_PATH = "style.css"

    BINDINGS = [
        Binding(key="escape", action="key_escape", description="exit"),
    ]

    def on_mount(self) -> None:
        self.install_screen(HomePage(self.output), name="homepage")
        self.push_screen("homepage")

    async def on_key(self, event: events.Key):
        if event.key == "up":
            pilot = Pilot(self)
            await pilot.press("shift+tab")
        if event.key == "down":
            pilot = Pilot(self)
            await pilot.press("tab")

    def action_key_escape(self) -> None:
        self.exit()

    def call_button(self, command: str, debug: bool) -> List[str]:
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

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "booklet":
            debug = self.query("Checkbox").first().value
            result = self.call_button("booklet", debug)
            self.install_screen(Booklet(result), name="booklet")
            self.push_screen("booklet")


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


if __name__ == "__main__":
    result = output()
    Tui(result).run()
